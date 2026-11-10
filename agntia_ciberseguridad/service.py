"""Foundation business operations; audit preview never executes a scanner."""
from datetime import timedelta
import json
import re
import sqlite3

from .auth import Authenticator, Principal
from .config import Settings
from .contracts import AssetKind, AssetPublic, Profile
from .errors import not_found, reject
from .network_policy import local_target, pin_target
from .storage import Database
from .telemetry.tracing import Telemetry
from .util import canonical, digest, now, uid, utcnow


class Service:
    def __init__(self, settings: Settings, database: Database):
        self.settings = settings
        self.db = database
        self.auth = Authenticator(settings)
        self.telemetry = Telemetry(settings)
        self.db.telemetry=self.telemetry

    def authorize(self, actor: Principal, tenant: str, capability: str):
        with self.telemetry.span("policy.authorize",component="policy",operation="authorize"):
            self.auth.authorize(actor, tenant, capability)
        with self.db.connection(readonly=True) as db:
            if not db.execute("SELECT 1 FROM tenants WHERE id=?", (tenant,)).fetchone():
                not_found()

    @staticmethod
    def _asset(db, tenant, asset_id):
        row = db.execute("SELECT body FROM assets WHERE tenant_id=? AND id=?", (tenant, asset_id)).fetchone()
        if not row:
            not_found()
        return json.loads(row["body"])

    @staticmethod
    def _grant(db, tenant, grant_id):
        row = db.execute("SELECT body FROM grants WHERE tenant_id=? AND id=?", (tenant, grant_id)).fetchone()
        if not row:
            not_found()
        return json.loads(row["body"])

    @staticmethod
    def public_asset(asset):
        return AssetPublic.model_validate({k: asset[k] for k in AssetPublic.model_fields if k in asset}).model_dump(mode="json")

    def create_asset(self, actor, tenant, body, correlation):
        self.authorize(actor, tenant, "assets.register")
        target = self.settings.targets.get(body.target_ref)
        if not target or target.tenant_id != tenant or target.kind != body.kind:
            not_found()
        asset = {"schema_version": 1, "id": uid(), "tenant_id": tenant,
                 **body.model_dump(mode="json"), "revision": 0, "state": "registered", "created_at": now(),
                 "configuration_hash": digest(target.model_dump(mode="json"))}
        try:
            with self.db.transaction() as db:
                self.auth.authorize(actor, tenant, "assets.register")
                db.execute("INSERT INTO assets VALUES(?,?,?,?,?,?)", (tenant, asset["id"], body.target_ref, 0, "registered", canonical(asset)))
                self.db.audit(db, tenant, actor.actor_id, "asset.registered", asset["id"], correlation,
                              {"asset_id": asset["id"], "configuration_hash": asset["configuration_hash"]})
        except sqlite3.IntegrityError:
            reject("conflict", "El activo ya está registrado o su ámbito cambió", 409)
        return self.public_asset(asset)

    def get_asset(self, actor, tenant, asset_id):
        self.authorize(actor, tenant, "assets.read")
        with self.db.connection(readonly=True) as db:
            return self.public_asset(self._asset(db, tenant, asset_id))

    def list_assets(self, actor, tenant, limit=100, after=""):
        self.authorize(actor, tenant, "assets.read")
        if not 1 <= limit <= 100 or (after and not re.fullmatch(r"[a-f0-9]{32}", after)):
            reject("validation", "Paginación inválida", 422)
        with self.db.connection(readonly=True) as db:
            rows = db.execute("SELECT body FROM assets WHERE tenant_id=? AND id>? ORDER BY id LIMIT ?", (tenant, after, limit)).fetchall()
        return {"items": [self.public_asset(json.loads(r["body"])) for r in rows],
                "next_cursor": json.loads(rows[-1]["body"])["id"] if len(rows) == limit else None}

    def _configuration(self, tenant, asset, consent_ref):
        target = self.settings.targets.get(asset["target_ref"])
        consent = self.settings.consents.get(consent_ref)
        if (not target or not consent or target.tenant_id != tenant or consent.tenant_id != tenant
                or asset["target_ref"] not in consent.target_refs):
            not_found()
        if asset["state"] != "registered" or asset["configuration_hash"] != digest(target.model_dump(mode="json")):
            reject("configuration_changed", "El activo requiere una nueva revisión de configuración", 409)
        authorities = [p for p in self.settings.principals if p.actor_id == consent.authority_actor_id]
        if len(authorities) != 1:
            reject("consent_revoked", "Autorización de titular no disponible", 403)
        authority = self.auth.current(authorities[0].id)
        if tenant not in authority.tenants or authority.role.value not in ("owner", "reviewer"):
            reject("consent_revoked", "Autorización de titular no disponible", 403)
        fingerprint = digest({"target": target.model_dump(mode="json"), "consent": consent.model_dump(mode="json")})
        return target, consent, fingerprint

    @staticmethod
    def _check_profile(target, profile, settings):
        if profile == Profile.static_read and target.kind == AssetKind.web:
            reject("profile_scope", "El perfil estático no admite este activo web", 422)
        if profile != Profile.static_read and target.kind != AssetKind.web:
            reject("profile_scope", "El perfil web requiere un activo web", 422)
        if profile == Profile.active_lab and not settings.lab_mode:
            reject("profile_scope", "Las pruebas activas solo se admiten en laboratorio autorizado", 422)

    @staticmethod
    def _proposal_hash(grant):
        return digest({k: v for k, v in grant.items() if k not in ("proposal_hash", "approval", "revocation", "state", "revision")})

    def propose_grant(self, actor, tenant, body, correlation):
        self.authorize(actor, tenant, "grants.propose")
        with self.db.transaction() as db:
            self.auth.authorize(actor, tenant, "grants.propose")
            asset = self._asset(db, tenant, body.asset_id)
            target, consent, fingerprint = self._configuration(tenant, asset, body.consent_ref)
            self._check_profile(target, body.profile, self.settings)
            current = utcnow()
            if body.expires_at <= current or body.starts_at < consent.starts_at or body.expires_at > consent.expires_at:
                reject("grant_interval", "Intervalo fuera de la autorización del titular", 422)
            if body.profile not in consent.profiles or body.max_requests > consent.max_requests or body.max_cost_cents > consent.max_cost_cents:
                reject("grant_expansion", "La propuesta amplía la autorización del titular", 403)
            grant = {"schema_version": 1, "id": uid(), "tenant_id": tenant,
                     **body.model_dump(mode="json"), "configuration_hash": fingerprint,
                     "created_by": actor.actor_id, "created_at": now(), "revision": 0, "state": "proposed",
                     "approval": None, "revocation": None}
            grant["proposal_hash"] = self._proposal_hash(grant)
            db.execute("INSERT INTO grants VALUES(?,?,?,?,?,?)", (tenant, grant["id"], body.asset_id, 0, "proposed", canonical(grant)))
            self.db.audit(db, tenant, actor.actor_id, "grant.proposed", grant["id"], correlation,
                          {"grant_id": grant["id"], "asset_id": body.asset_id, "proposal_hash": grant["proposal_hash"]})
        return grant

    def get_grant(self, actor, tenant, grant_id):
        self.authorize(actor, tenant, "grants.read")
        with self.db.connection(readonly=True) as db:
            return self._grant(db, tenant, grant_id)

    def approve_grant(self, actor, tenant, grant_id, body, correlation):
        self.authorize(actor, tenant, "grants.approve")
        with self.db.transaction() as db:
            self.auth.authorize(actor, tenant, "grants.approve")
            grant = self._grant(db, tenant, grant_id)
            if grant["created_by"] == actor.actor_id:
                reject("separation_of_duties", "La propuesta requiere otro revisor autorizado", 403)
            if (grant["revision"] != body.expected_revision or grant["state"] != "proposed"
                    or grant["proposal_hash"] != body.proposal_hash or self._proposal_hash(grant) != body.proposal_hash):
                reject("conflict", "La propuesta o su revisión no coinciden", 409)
            asset = self._asset(db, tenant, grant["asset_id"])
            _, consent, fingerprint = self._configuration(tenant, asset, grant["consent_ref"])
            from datetime import datetime
            if (fingerprint != grant["configuration_hash"] or datetime.fromisoformat(grant["expires_at"]) <= utcnow()
                    or consent.expires_at <= utcnow()):
                reject("configuration_changed", "La propuesta caducó o cambió su autorización", 409)
            grant.update(state="approved", revision=grant["revision"] + 1,
                         approval={"actor_id": actor.actor_id, "binding_id": actor.binding_id,
                                   "at": now(), "notes": body.notes, "proposal_hash": body.proposal_hash})
            self._save_grant(db, tenant, grant)
            self.db.audit(db, tenant, actor.actor_id, "grant.approved", grant_id, correlation,
                          {"grant_id": grant_id, "proposal_hash": body.proposal_hash, "revision": grant["revision"]})
        return grant

    @staticmethod
    def _save_grant(db, tenant, grant):
        db.execute("UPDATE grants SET revision=?,state=?,body=? WHERE tenant_id=? AND id=?",
                   (grant["revision"], grant["state"], canonical(grant), tenant, grant["id"]))

    def revoke_grant(self, actor, tenant, grant_id, body, correlation):
        self.authorize(actor, tenant, "grants.revoke")
        with self.db.transaction() as db:
            self.auth.authorize(actor, tenant, "grants.revoke")
            grant = self._grant(db, tenant, grant_id)
            if grant["revision"] != body.expected_revision or grant["state"] == "revoked":
                reject("conflict", "La revisión o estado de autorización no coincide", 409)
            grant.update(state="revoked", revision=grant["revision"] + 1,
                         revocation={"actor_id": actor.actor_id, "at": now(), "notes": body.notes})
            self._save_grant(db, tenant, grant)
            self.db.audit(db, tenant, actor.actor_id, "grant.revoked", grant_id, correlation,
                          {"grant_id": grant_id, "revision": grant["revision"]})
        return grant

    def validate_authorization(self, actor, tenant, body):
        from datetime import datetime
        self.authorize(actor, tenant, "audits.preview")
        with self.db.connection(readonly=True) as db:
            asset = self._asset(db, tenant, body.asset_id)
            grant = self._grant(db, tenant, body.grant_id)
            target, consent, fingerprint = self._configuration(tenant, asset, grant["consent_ref"])
            if grant["asset_id"] != asset["id"]:
                not_found()
            if (grant["state"] != "approved" or not grant["approval"]
                    or grant["proposal_hash"] != self._proposal_hash(grant)):
                reject("grant_not_active", "Autorización no activa", 403)
            instant = utcnow()
            if not datetime.fromisoformat(grant["starts_at"]) <= instant < datetime.fromisoformat(grant["expires_at"]):
                reject("grant_expired", "Autorización fuera de ventana", 403)
            if not consent.starts_at <= instant < consent.expires_at or fingerprint != grant["configuration_hash"]:
                reject("consent_changed", "Autorización del titular modificada o caducada", 403)
            approver = self.auth.current(grant["approval"]["binding_id"])
            self.auth.authorize(approver, tenant, "grants.approve")
            if (approver.actor_id != grant["approval"]["actor_id"]
                    or grant["approval"]["proposal_hash"] != grant["proposal_hash"]):
                reject("approval_revoked", "Aprobación no vigente", 403)
            if body.profile.value != grant["profile"] or body.requests > grant["max_requests"] or body.maximum_cost_cents > grant["max_cost_cents"]:
                reject("grant_expansion", "Solicitud fuera del alcance autorizado", 403)
            self._check_profile(target, body.profile, self.settings)
        return asset, grant, target

    def preview(self, actor, tenant, body, correlation, resolver=None):
        asset, grant, target = self.validate_authorization(actor, tenant, body)
        if target.kind in (AssetKind.repository, AssetKind.directory):
            local_target(target, self.settings)
        elif target.kind == AssetKind.web:
            pin_target(target, self.settings, resolver)
        elif not re.fullmatch(r"[a-zA-Z0-9._/:-]+@sha256:[a-f0-9]{64}", target.location):
            reject("target_configuration", "La imagen aprobada necesita digest", 424)
        # A grant/principal can expire or be revoked during DNS/filesystem preflight.
        self.validate_authorization(actor, tenant, body)
        with self.db.transaction() as db:
            self.auth.authorize(actor, tenant, "audits.preview")
            current = self._grant(db, tenant, grant["id"])
            if current["revision"] != grant["revision"] or current["state"] != "approved":
                reject("conflict", "La autorización cambió durante la previsualización", 409)
            self.db.audit(db, tenant, actor.actor_id, "audit.previewed", asset["id"], correlation,
                          {"asset_id": asset["id"], "grant_id": grant["id"], "profile": body.profile.value})
        return {"status": "preflight_passed", "asset_id": asset["id"], "grant_id": grant["id"],
                "grant_revision": grant["revision"], "profile": body.profile.value,
                "security_scan_executed": False, "budget_reserved": False,
                "notice": "Solo comprobación de alcance; no scanner, auditoría completada ni protección activa."}

    def audit_integrity(self, actor, tenant):
        self.authorize(actor, tenant, "audit.read")
        with self.db.connection(readonly=True) as db:
            return self.db.verify_audit(db, tenant)

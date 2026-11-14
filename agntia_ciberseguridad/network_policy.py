"""Pure preflight: validates and pins a destination but never opens a connection."""
from dataclasses import dataclass
import ipaddress
from pathlib import Path
import socket
from urllib.parse import unquote, urljoin, urlsplit

from .config import Settings, TargetConfig
from .errors import reject


@dataclass(frozen=True)
class PinnedTarget:
    scheme: str
    host: str
    port: int
    address: str
    all_addresses: tuple[str, ...]


def _parts(location: str):
    try:
        p = urlsplit(location)
        if (p.scheme not in ("https", "http") or not p.hostname or not p.hostname.isascii()
                or p.username is not None or p.password is not None or p.query or p.fragment
                or "?" in location or "#" in location or "%" in p.hostname or p.hostname.endswith(".")
                or any(ord(c) <= 32 or ord(c) == 127 for c in location)):
            raise ValueError()
        port = p.port or (443 if p.scheme == "https" else 80)
        return p, port
    except ValueError:
        reject("network_policy", "Destino de red no autorizado", 422)


def pin_target(target: TargetConfig, settings: Settings, resolver=None) -> PinnedTarget:
    parts, port = _parts(target.location)
    _check_paths(parts.path, target.allowed_path_prefixes or [parts.path or "/"])
    if port not in target.allowed_ports:
        reject("network_policy", "Puerto no autorizado", 422)
    if parts.scheme != "https" and not (settings.lab_mode and target.allow_insecure_lab):
        reject("network_policy", "Se requiere TLS fuera del laboratorio autorizado", 422)
    try:
        networks = [ipaddress.ip_network(n, strict=True) for n in target.allowed_networks]
        addresses = resolver(parts.hostname, port) if resolver else [r[4][0] for r in socket.getaddrinfo(parts.hostname, port, type=socket.SOCK_STREAM)]
        if not addresses or len(addresses) > 64 or not networks:
            raise ValueError()
        valid = []
        for address in addresses:
            if "%" in address:
                raise ValueError()
            ip = ipaddress.ip_address(address)
            if getattr(ip, "ipv4_mapped", None):
                ip = ip.ipv4_mapped
            if (ip.is_unspecified or ip.is_multicast or ip.is_link_local
                    or str(ip) in ("100.100.100.200", "fd00:ec2::254")
                    or (ip.is_loopback and not (settings.lab_mode and target.allow_loopback_lab))
                    or not any(ip in net for net in networks)):
                raise ValueError()
            if parts.scheme == "http" and not (ip.is_private or ip.is_loopback):
                raise ValueError()
            valid.append(str(ip))
        values = tuple(sorted(set(valid)))
        return PinnedTarget(parts.scheme, parts.hostname.lower(), port, values[0], values)
    except Exception:
        reject("network_policy", "Destino no permitido o no resoluble", 422)


def validate_redirect(target: TargetConfig, previous_url: str, location: str, settings: Settings, resolver=None):
    original, port = _parts(target.location)
    previous, old_port = _parts(previous_url)
    follow, next_port = _parts(urljoin(previous_url, location))
    expected = (original.scheme, original.hostname.lower(), port)
    if (previous.scheme, previous.hostname.lower(), old_port) != expected or (follow.scheme, follow.hostname.lower(), next_port) != expected:
        reject("network_policy", "Redirección fuera del activo autorizado", 422)
    prefixes = target.allowed_path_prefixes or [original.path or "/"]
    _check_paths(follow.path, prefixes)
    return pin_target(target.model_copy(update={"location": follow.geturl()}), settings, resolver)


def _check_paths(path, prefixes):
    decoded = path or "/"
    for _ in range(3):
        newer = unquote(decoded)
        if newer == decoded:
            break
        decoded = newer
    if ("%" in decoded or "\\" in decoded or any(part in (".", "..") for part in decoded.split("/"))
            or any(ord(c) <= 32 or ord(c) == 127 for c in decoded)):
        reject("network_policy", "Ruta de red no permitida", 422)
    for prefix in prefixes:
        if not prefix.startswith("/") or any(part in (".", "..") for part in prefix.split("/")) or "%" in prefix or "\\" in prefix:
            reject("target_configuration", "Prefijo de ruta aprobado inválido", 424)
    if not any(prefix == "/" or decoded == prefix.rstrip("/") or decoded.startswith(prefix.rstrip("/") + "/") for prefix in prefixes):
        reject("network_policy", "Ruta fuera del activo autorizado", 422)


def local_target(target: TargetConfig, settings: Settings) -> Path:
    requested = Path(target.location)
    if not requested.is_absolute():
        reject("target_configuration", "El recurso local requiere una ruta aprobada absoluta", 424)
    try:
        resolved = requested.resolve(strict=True)
        if not resolved.is_dir() or not any(resolved == root.resolve() or root.resolve() in resolved.parents for root in settings.approved_workspace_roots):
            raise ValueError()
        return resolved
    except (OSError, ValueError):
        reject("scope_violation", "Recurso local fuera de los directorios aprobados", 422)

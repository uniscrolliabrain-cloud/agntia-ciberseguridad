$ErrorActionPreference = 'Stop'
Push-Location (Join-Path $PSScriptRoot '..')
try {
& python -X utf8 --version
if ($LASTEXITCODE -ne 0) { throw 'Python unavailable' }
& node --version
if ($LASTEXITCODE -ne 0) { throw 'Node unavailable' }
& python -X utf8 -m agntia_ciberseguridad.releasecheck
if ($LASTEXITCODE -ne 0) { throw 'Installed package smoke failed' }
& python -X utf8 scripts/validate_foundation.py
if ($LASTEXITCODE -ne 0) { throw 'Documentation validation failed' }
& python -X utf8 scripts/validate_campaign.py
if ($LASTEXITCODE -ne 0) { throw 'Campaign validation failed' }
if (Get-Command docker -ErrorAction SilentlyContinue) {
  & docker info 1>$null 2>$null
  if ($LASTEXITCODE -eq 0) { Write-Output 'Docker reachable; Linux-container validation remains separate.' }
  else { Write-Output 'Docker NOT VERIFIED: daemon/socket unavailable.' }
} else { Write-Output 'Docker NOT VERIFIED: executable unavailable.' }
# No Set-ExecutionPolicy, global installs, secret printing or destructive reset.

} finally { Pop-Location }

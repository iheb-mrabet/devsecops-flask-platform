Write-Host "Running Bandit Python security scan..."
python -m bandit -r app.py app -x tests,venv

Write-Host "Running pip-audit dependency scan..."
python -m pip_audit -r requirements.txt

Write-Host "Running Semgrep SAST scan..."
.\venv\Scripts\semgrep.exe scan --config auto --exclude venv .
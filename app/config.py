import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    # Intentional vulnerability for DevSecOps demos:
    # Weak session secret key.
    # Secure version notes: generate a long random value, load it from a secret
    # manager or environment variable, and rotate it safely.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")

    DATABASE = os.environ.get("DATABASE", str(BASE_DIR / "devsecops_platform.db"))

    # Intentional vulnerability for DevSecOps demos:
    # This is a fake key with a secret-like shape so tools such as Gitleaks can
    # detect the pattern. It is not a real credential and does not grant access.
    # Secure version notes: never commit secrets; use a vault or cloud secret
    # manager and inject credentials at runtime.
    FAKE_RECRUITMENT_API_KEY = "sk_live_FAKE_RECRUITMENT_API_KEY_DO_NOT_USE_123456"

    # Intentional vulnerability for DevSecOps demos:
    # Debug defaults to enabled.
    # Secure version notes: disable debug in production and enforce a production
    # config profile in CI/CD.
    DEBUG = os.environ.get("INSECURE_DEBUG", "1") == "1"

    # No CSRF framework is configured on purpose.
    WTF_CSRF_ENABLED = False

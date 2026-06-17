import os

from app import create_app


app = create_app()


if __name__ == "__main__":
    # Intentional vulnerability for DevSecOps demos:
    # Debug mode is enabled by default so scanners and reviewers can flag it.
    # Secure version notes: default this to False and enable debug only in a
    # local development profile that is never deployed.
    debug_enabled = os.environ.get("INSECURE_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=5000, debug=debug_enabled)

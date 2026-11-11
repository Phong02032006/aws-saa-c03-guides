import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    # Local: SQLite. Azure: mssql+pymssql://USER:PASSWORD@SERVER.database.windows.net:1433/DBNAME
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///quiz.db")
    # pool_pre_ping matters for Azure SQL serverless (free offer), which auto-pauses and drops idle connections.
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 280}

    # "dev" = pick a role on a login form (local only); "entra" = Microsoft Entra External ID.
    AUTH_MODE = os.environ.get("AUTH_MODE", "dev")
    ENTRA_CLIENT_ID = os.environ.get("ENTRA_CLIENT_ID", "")
    ENTRA_CLIENT_SECRET = os.environ.get("ENTRA_CLIENT_SECRET", "")
    # e.g. https://<tenant-subdomain>.ciamlogin.com/<tenant-subdomain>.onmicrosoft.com
    ENTRA_AUTHORITY = os.environ.get("ENTRA_AUTHORITY", "")

    # Empty GRADER_URL = grade in-process and store PDFs locally (no AWS needed).
    GRADER_URL = os.environ.get("GRADER_URL", "")
    GRADER_SECRET = os.environ.get("GRADER_SECRET", "")
    LOCAL_CERT_DIR = os.environ.get("LOCAL_CERT_DIR", "")

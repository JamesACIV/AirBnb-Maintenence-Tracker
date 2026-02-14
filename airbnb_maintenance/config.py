import os
from pathlib import Path

def get_db_path():
    """Get default database path in user's Documents folder."""
    documents = Path.home() / "Documents"
    db_dir = documents / "airbnb_maintenance"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / "maintenance.db"

DB_PATH = get_db_path()

import shutil
import os
from dental_clinic.services.database import Database


def backup_database(db: Database, destination_path: str) -> str:
	os.makedirs(os.path.dirname(destination_path), exist_ok=True)
	shutil.copyfile(db.db_path, destination_path)
	return destination_path


def restore_database(db: Database, source_path: str) -> None:
	# Close current connection if exists by recreating db wrapper (simple approach)
	shutil.copyfile(source_path, db.db_path)
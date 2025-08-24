from typing import List, Optional
from dataclasses import asdict

from services.database import Database
from models import Patient


class PatientService:
	def __init__(self, db: Database) -> None:
		self.db = db

	def create_patient(self, patient: Patient) -> int:
		return self.db.execute(
			"INSERT INTO patients(name, age, gender, phone, address) VALUES(?,?,?,?,?)",
			(patient.name, patient.age, patient.gender, patient.phone, patient.address),
		)

	def update_patient(self, patient: Patient) -> None:
		assert patient.id is not None, "Patient ID is required for update"
		self.db.execute(
			"""
			UPDATE patients
			SET name=?, age=?, gender=?, phone=?, address=?, updated_at=datetime('now')
			WHERE id=?
			""",
			(patient.name, patient.age, patient.gender, patient.phone, patient.address, patient.id),
		)

	def delete_patient(self, patient_id: int) -> None:
		self.db.execute("DELETE FROM patients WHERE id=?", (patient_id,))

	def get_patient(self, patient_id: int) -> Optional[Patient]:
		rows = self.db.query("SELECT * FROM patients WHERE id=?", (patient_id,))
		if not rows:
			return None
		row = rows[0]
		return Patient(
			id=row["id"],
			name=row["name"],
			age=row["age"],
			gender=row["gender"],
			phone=row["phone"],
			address=row["address"],
		)

	def list_patients(self, query_text: str = "") -> List[Patient]:
		if query_text:
			like = f"%{query_text.strip()}%"
			rows = self.db.query(
				"SELECT * FROM patients WHERE name LIKE ? OR phone LIKE ? ORDER BY name ASC",
				(like, like),
			)
		else:
			rows = self.db.query("SELECT * FROM patients ORDER BY name ASC")
		return [
			Patient(
				id=r["id"],
				name=r["name"],
				age=r["age"],
				gender=r["gender"],
				phone=r["phone"],
				address=r["address"],
			)
			for r in rows
		]
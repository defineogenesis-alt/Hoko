from typing import List, Optional, Tuple

from dental_clinic.services.database import Database
from dental_clinic.models import Treatment


class TreatmentService:
	def __init__(self, db: Database) -> None:
		self.db = db

	def add_treatment(self, treatment: Treatment) -> int:
		return self.db.execute(
			"INSERT INTO treatments(patient_id, date, type, description, cost) VALUES(?,?,?,?,?)",
			(treatment.patient_id, treatment.date, treatment.type, treatment.description, treatment.cost),
		)

	def update_treatment(self, treatment: Treatment) -> None:
		assert treatment.id is not None
		self.db.execute(
			"""
			UPDATE treatments SET patient_id=?, date=?, type=?, description=?, cost=?, updated_at=datetime('now')
			WHERE id=?
			""",
			(treatment.patient_id, treatment.date, treatment.type, treatment.description, treatment.cost, treatment.id),
		)

	def delete_treatment(self, treatment_id: int) -> None:
		self.db.execute("DELETE FROM treatments WHERE id=?", (treatment_id,))

	def list_treatments_for_patient(self, patient_id: int) -> List[Treatment]:
		rows = self.db.query("SELECT * FROM treatments WHERE patient_id=? ORDER BY date DESC", (patient_id,))
		return [
			Treatment(
				id=r["id"], patient_id=r["patient_id"], date=r["date"], type=r["type"], description=r["description"], cost=r["cost"]
			)
			for r in rows
		]

	def revenue_summary_by_month(self) -> List[Tuple[str, float]]:
		rows = self.db.query(
			"SELECT substr(date,1,7) AS ym, SUM(cost) FROM treatments GROUP BY ym ORDER BY ym ASC"
		)
		return [(r["ym"], r[1] if r[1] is not None else 0.0) for r in rows]
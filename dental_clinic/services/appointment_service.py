from typing import List, Optional, Tuple

from services.database import Database
from models import Appointment


class AppointmentService:
	def __init__(self, db: Database) -> None:
		self.db = db

	def _overlaps(self, date: str, start_time: str, duration_minutes: int, doctor: str, exclude_id: Optional[int] = None) -> bool:
		# Convert HH:MM to minutes
		def to_minutes(t: str) -> int:
			parts = t.split(":")
			return int(parts[0]) * 60 + int(parts[1])

		start = to_minutes(start_time)
		end = start + int(duration_minutes)

		params: List = [date, doctor]
		sql = "SELECT id, time, duration_minutes FROM appointments WHERE date=? AND doctor=?"
		if exclude_id is not None:
			sql += " AND id<>?"
			params.append(exclude_id)

		rows = self.db.query(sql, tuple(params))
		for r in rows:
			other_start = to_minutes(r["time"]) 
			other_end = other_start + int(r["duration_minutes"]) 
			if not (end <= other_start or start >= other_end):
				return True
		return False

	def create_appointment(self, appt: Appointment) -> int:
		if self._overlaps(appt.date, appt.time, appt.duration_minutes, appt.doctor):
			raise ValueError("Overlapping appointment for this doctor at the selected time.")
		return self.db.execute(
			"""
			INSERT INTO appointments(patient_id, date, time, duration_minutes, doctor, notes)
			VALUES(?,?,?,?,?,?)
			""",
			(appt.patient_id, appt.date, appt.time, appt.duration_minutes, appt.doctor, appt.notes),
		)

	def update_appointment(self, appt: Appointment) -> None:
		assert appt.id is not None, "Appointment ID required"
		if self._overlaps(appt.date, appt.time, appt.duration_minutes, appt.doctor, exclude_id=appt.id):
			raise ValueError("Overlapping appointment for this doctor at the selected time.")
		self.db.execute(
			"""
			UPDATE appointments
			SET patient_id=?, date=?, time=?, duration_minutes=?, doctor=?, notes=?, updated_at=datetime('now')
			WHERE id=?
			""",
			(appt.patient_id, appt.date, appt.time, appt.duration_minutes, appt.doctor, appt.notes, appt.id),
		)

	def delete_appointment(self, appt_id: int) -> None:
		self.db.execute("DELETE FROM appointments WHERE id=?", (appt_id,))

	def list_appointments(self, upcoming_only: Optional[bool] = None) -> List[Appointment]:
		sql = "SELECT * FROM appointments"
		if upcoming_only is True:
			sql += " WHERE date >= date('now')"
		elif upcoming_only is False:
			sql += " WHERE date < date('now')"
		sql += " ORDER BY date ASC, time ASC"
		rows = self.db.query(sql)
		return [
			Appointment(
				id=r["id"],
				patient_id=r["patient_id"],
				date=r["date"],
				time=r["time"],
				duration_minutes=r["duration_minutes"],
				doctor=r["doctor"],
				notes=r["notes"],
			)
			for r in rows
		]

	def list_appointments_for_patient(self, patient_id: int) -> List[Appointment]:
		rows = self.db.query(
			"SELECT * FROM appointments WHERE patient_id=? ORDER BY date DESC, time DESC",
			(patient_id,),
		)
		return [
			Appointment(
				id=r["id"],
				patient_id=r["patient_id"],
				date=r["date"],
				time=r["time"],
				duration_minutes=r["duration_minutes"],
				doctor=r["doctor"],
				notes=r["notes"],
			)
			for r in rows
		]
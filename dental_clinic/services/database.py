import sqlite3
from typing import Any, Iterable, Optional
import threading


class Database:
	"""Thread-safe SQLite database wrapper with schema initialization."""

	def __init__(self, db_path: str) -> None:
		self.db_path = db_path
		self._local = threading.local()

	def _get_connection(self) -> sqlite3.Connection:
		conn = getattr(self._local, "conn", None)
		if conn is None:
			conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
			conn.row_factory = sqlite3.Row
			setattr(self._local, "conn", conn)
		return conn

	def initialize_schema(self) -> None:
		conn = self._get_connection()
		cur = conn.cursor()
		# Patients
		cur.execute(
			"""
			CREATE TABLE IF NOT EXISTS patients (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				name TEXT NOT NULL,
				age INTEGER,
				gender TEXT CHECK(gender IN ('Male','Female','Other')),
				phone TEXT,
				address TEXT,
				created_at TEXT DEFAULT (datetime('now')),
				updated_at TEXT DEFAULT (datetime('now'))
			);
			"""
		)
		# Appointments
		cur.execute(
			"""
			CREATE TABLE IF NOT EXISTS appointments (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				patient_id INTEGER NOT NULL,
				date TEXT NOT NULL,           -- YYYY-MM-DD
				time TEXT NOT NULL,           -- HH:MM in 24h
				duration_minutes INTEGER NOT NULL DEFAULT 30,
				doctor TEXT NOT NULL,
				notes TEXT,
				created_at TEXT DEFAULT (datetime('now')),
				updated_at TEXT DEFAULT (datetime('now')),
				FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE CASCADE
			);
			"""
		)
		# Indexes to help overlap checks and queries
		cur.execute("CREATE INDEX IF NOT EXISTS idx_appointments_date_doctor ON appointments(date, doctor)")
		cur.execute("CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_id)")

		# Treatments
		cur.execute(
			"""
			CREATE TABLE IF NOT EXISTS treatments (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				patient_id INTEGER NOT NULL,
				date TEXT NOT NULL,
				type TEXT NOT NULL,
				description TEXT,
				cost REAL NOT NULL DEFAULT 0,
				created_at TEXT DEFAULT (datetime('now')),
				updated_at TEXT DEFAULT (datetime('now')),
				FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE CASCADE
			);
			"""
		)

		# Invoices
		cur.execute(
			"""
			CREATE TABLE IF NOT EXISTS invoices (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				patient_id INTEGER NOT NULL,
				invoice_date TEXT NOT NULL,
				total REAL NOT NULL DEFAULT 0,
				paid REAL NOT NULL DEFAULT 0,
				FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE CASCADE
			);
			"""
		)
		cur.execute(
			"""
			CREATE TABLE IF NOT EXISTS invoice_items (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				invoice_id INTEGER NOT NULL,
				description TEXT NOT NULL,
				amount REAL NOT NULL,
				FOREIGN KEY(invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
			);
			"""
		)

		conn.commit()

	def execute(self, sql: str, params: Iterable[Any] = ()) -> int:
		conn = self._get_connection()
		cur = conn.cursor()
		cur.execute(sql, tuple(params))
		conn.commit()
		return cur.lastrowid

	def query(self, sql: str, params: Iterable[Any] = ()) -> list[sqlite3.Row]:
		conn = self._get_connection()
		cur = conn.cursor()
		cur.execute(sql, tuple(params))
		rows = cur.fetchall()
		return rows

	def scalar(self, sql: str, params: Iterable[Any] = ()) -> Optional[Any]:
		conn = self._get_connection()
		cur = conn.cursor()
		cur.execute(sql, tuple(params))
		row = cur.fetchone()
		return row[0] if row else None
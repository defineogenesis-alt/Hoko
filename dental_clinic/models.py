from dataclasses import dataclass
from typing import Optional


@dataclass
class Patient:
	id: Optional[int]
	name: str
	age: Optional[int]
	gender: Optional[str]
	phone: Optional[str]
	address: Optional[str]


@dataclass
class Appointment:
	id: Optional[int]
	patient_id: int
	date: str  # YYYY-MM-DD
	time: str  # HH:MM 24h
	duration_minutes: int
	doctor: str
	notes: Optional[str]


@dataclass
class Treatment:
	id: Optional[int]
	patient_id: int
	date: str
	type: str
	description: Optional[str]
	cost: float


@dataclass
class Invoice:
	id: Optional[int]
	patient_id: int
	invoice_date: str
	total: float
	paid: float


@dataclass
class InvoiceItem:
	id: Optional[int]
	invoice_id: int
	description: str
	amount: float
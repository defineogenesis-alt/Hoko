import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

try:
	import ttkbootstrap as ttkb
except Exception:
	ttkb = None

from services.database import Database
from services.patient_service import PatientService
from services.appointment_service import AppointmentService
from services.treatment_service import TreatmentService
from services.invoice_service import InvoiceService

from ui.patients_view import PatientsView
from ui.appointments_view import AppointmentsView
from ui.treatments_view import TreatmentsView
from ui.reports_view import ReportsView


class DentalClinicApp(tk.Tk):
	def __init__(self, db: Database, use_ttkbootstrap: bool = False) -> None:
		self._use_ttk = use_ttkbootstrap and ttkb is not None
		if self._use_ttk:
			super().__init__(className="Dental Clinic Management")
			self.style = ttkb.Style("cosmo")
		else:
			super().__init__(className="Dental Clinic Management")
			self.style = ttk.Style()

		self.title("Dental Clinic Management")
		self.geometry("1200x750")
		self.minsize(1000, 650)

		self.db = db
		self.patient_service = PatientService(db)
		self.appointment_service = AppointmentService(db)
		self.treatment_service = TreatmentService(db)
		self.invoice_service = InvoiceService(db)

		self._build_ui()

	def _build_ui(self) -> None:
		# Top navigation
		navbar = ttk.Frame(self)
		navbar.pack(side=tk.TOP, fill=tk.X)

		self.quick_search_var = tk.StringVar()
		quick_search = ttk.Entry(navbar, textvariable=self.quick_search_var)
		quick_search.pack(side=tk.LEFT, padx=8, pady=8)
		quick_btn = ttk.Button(navbar, text="Search", command=self._on_quick_search)
		quick_btn.pack(side=tk.LEFT, padx=(0, 8))

		btn_patients = ttk.Button(navbar, text="Patients", command=lambda: self._show_view("patients"))
		btn_appts = ttk.Button(navbar, text="Appointments", command=lambda: self._show_view("appointments"))
		btn_treat = ttk.Button(navbar, text="Treatments", command=lambda: self._show_view("treatments"))
		btn_reports = ttk.Button(navbar, text="Reports", command=lambda: self._show_view("reports"))
		for b in (btn_patients, btn_appts, btn_treat, btn_reports):
			b.pack(side=tk.LEFT, padx=4)

		# Container for views
		self.container = ttk.Frame(self)
		self.container.pack(fill=tk.BOTH, expand=True)

		self.views = {
			"patients": PatientsView(self.container, self.patient_service, self.treatment_service, self.invoice_service, on_open_appointments=lambda pid: self._show_view("appointments", pid)),
			"appointments": AppointmentsView(self.container, self.patient_service, self.appointment_service),
			"treatments": TreatmentsView(self.container, self.patient_service, self.treatment_service, self.invoice_service),
			"reports": ReportsView(self.container, self.patient_service, self.treatment_service),
		}
		for v in self.views.values():
			v.place(relx=0, rely=0, relwidth=1, relheight=1)

		self._show_view("patients")

	def _show_view(self, name: str, patient_id: Optional[int] = None) -> None:
		for key, view in self.views.items():
			if key == name:
				view.lift()
				if patient_id is not None and hasattr(view, "focus_patient"):
					try:
						view.focus_patient(patient_id)
					except Exception:
						pass
			else:
				view.lower()

	def _on_quick_search(self) -> None:
		text = self.quick_search_var.get().strip()
		patients_view: PatientsView = self.views["patients"]  # type: ignore
		patients_view.set_search(text)
		self._show_view("patients")
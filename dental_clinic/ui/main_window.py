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
from ui.icon_loader import load_icons


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

		# Load icons once and keep references
		self.icons = load_icons(self, size=18)

		self.quick_search_var = tk.StringVar()
		quick_search = ttk.Entry(navbar, textvariable=self.quick_search_var)
		quick_search.pack(side=tk.LEFT, padx=8, pady=8)
		quick_btn = ttk.Button(navbar, text="Search", image=self.icons.get("search"), compound=tk.LEFT, command=self._on_quick_search)
		quick_btn.pack(side=tk.LEFT, padx=(0, 8))

		btn_patients = ttk.Button(navbar, text="Patients", image=self.icons.get("patients"), compound=tk.LEFT, command=lambda: self._show_view("patients"))
		btn_appts = ttk.Button(navbar, text="Appointments", image=self.icons.get("appointments"), compound=tk.LEFT, command=lambda: self._show_view("appointments"))
		btn_treat = ttk.Button(navbar, text="Treatments", image=self.icons.get("treatments"), compound=tk.LEFT, command=lambda: self._show_view("treatments"))
		btn_reports = ttk.Button(navbar, text="Reports", image=self.icons.get("reports"), compound=tk.LEFT, command=lambda: self._show_view("reports"))
		for b in (btn_patients, btn_appts, btn_treat, btn_reports):
			b.pack(side=tk.LEFT, padx=4)

		# Theme switcher (ttkbootstrap only)
		if self._use_ttk:
			try:
				themes = sorted(set(self.style.theme_names()))
				self.theme_var = tk.StringVar(value="cosmo")
				theme_combo = ttk.Combobox(navbar, values=themes, textvariable=self.theme_var, width=14, state="readonly")
				theme_combo.pack(side=tk.RIGHT, padx=8)
				theme_combo.bind("<<ComboboxSelected>>", lambda e: self.style.theme_use(self.theme_var.get()))
			except Exception:
				pass

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

		# Provide icons to reports view for button images
		try:
			getattr(self.views["reports"], "set_icons")(self.icons)
		except Exception:
			pass

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
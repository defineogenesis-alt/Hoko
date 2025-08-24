import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from dental_clinic.models import Appointment, Patient
from dental_clinic.services.patient_service import PatientService
from dental_clinic.services.appointment_service import AppointmentService


class AppointmentsView(ttk.Frame):
	def __init__(self, parent, patient_service: PatientService, appointment_service: AppointmentService) -> None:
		super().__init__(parent)
		self.patient_service = patient_service
		self.appointment_service = appointment_service

		self._build_ui()
		self.refresh()

	def _build_ui(self) -> None:
		top = ttk.Frame(self)
		top.pack(fill=tk.X, padx=8, pady=8)

		add_btn = ttk.Button(top, text="Add", command=self._on_add)
		edit_btn = ttk.Button(top, text="Edit", command=self._on_edit)
		del_btn = ttk.Button(top, text="Delete", command=self._on_delete)
		for b in (add_btn, edit_btn, del_btn):
			b.pack(side=tk.RIGHT, padx=4)

		columns = ("id", "patient", "date", "time", "duration", "doctor", "notes")
		self.tree = ttk.Treeview(self, columns=columns, show="headings")
		for c in columns:
			self.tree.heading(c, text=c.title())
			self.tree.column(c, width=120, anchor=tk.W)
		self.tree.column("notes", width=260)
		self.tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

	def refresh(self) -> None:
		for i in self.tree.get_children(""):
			self.tree.delete(i)
		rows = self.appointment_service.list_appointments()
		patient_cache = {p.id: p.name for p in self.patient_service.list_patients()}
		for a in rows:
			self.tree.insert("", tk.END, values=(a.id, patient_cache.get(a.patient_id, a.patient_id), a.date, a.time, a.duration_minutes, a.doctor, a.notes or ""))

	def _on_add(self) -> None:
		self._open_form()

	def _on_edit(self) -> None:
		item = self.tree.focus()
		if not item:
			messagebox.showwarning("Edit Appointment", "Select an appointment to edit.")
			return
		v = self.tree.item(item, "values")
		# Need to map back to patient_id from name. Do a lookup.
		patients = self.patient_service.list_patients()
		patient_id = next((p.id for p in patients if p.name == v[1]), None)
		appt = Appointment(id=int(v[0]), patient_id=patient_id or 0, date=v[2], time=v[3], duration_minutes=int(v[4]), doctor=v[5], notes=v[6])
		self._open_form(appt)

	def _on_delete(self) -> None:
		item = self.tree.focus()
		if not item:
			messagebox.showwarning("Delete Appointment", "Select an appointment to delete.")
			return
		v = self.tree.item(item, "values")
		if messagebox.askyesno("Confirm", "Delete selected appointment?"):
			self.appointment_service.delete_appointment(int(v[0]))
			self.refresh()

	def _open_form(self, appt: Optional[Appointment] = None) -> None:
		dlg = tk.Toplevel(self)
		dlg.title("Appointment" + (" - Edit" if appt else " - Add"))
		dlg.grab_set()

		patients = self.patient_service.list_patients()
		patient_names = [p.name for p in patients]
		patient_name_to_id = {p.name: p.id for p in patients}

		patient_var = tk.StringVar(value=next((p.name for p in patients if p.id == appt.patient_id), "") if appt else "")
		date_var = tk.StringVar(value=appt.date if appt else "")
		time_var = tk.StringVar(value=appt.time if appt else "")
		duration_var = tk.StringVar(value=str(appt.duration_minutes) if appt else "30")
		doctor_var = tk.StringVar(value=appt.doctor if appt else "")
		notes_var = tk.StringVar(value=appt.notes if appt else "")

		form = ttk.Frame(dlg)
		form.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

		labels = ["Patient", "Date (YYYY-MM-DD)", "Time (HH:MM)", "Duration (min)", "Doctor", "Notes"]
		for i, label in enumerate(labels):
			ttk.Label(form, text=label).grid(row=i, column=0, sticky=tk.W, pady=4, padx=4)

		patient_combo = ttk.Combobox(form, values=patient_names, textvariable=patient_var, state="readonly")
		patient_combo.grid(row=0, column=1, sticky=tk.EW, pady=4, padx=4)
		entry_date = ttk.Entry(form, textvariable=date_var)
		entry_date.grid(row=1, column=1, sticky=tk.EW, pady=4, padx=4)
		entry_time = ttk.Entry(form, textvariable=time_var)
		entry_time.grid(row=2, column=1, sticky=tk.EW, pady=4, padx=4)
		entry_duration = ttk.Entry(form, textvariable=duration_var)
		entry_duration.grid(row=3, column=1, sticky=tk.EW, pady=4, padx=4)
		entry_doctor = ttk.Entry(form, textvariable=doctor_var)
		entry_doctor.grid(row=4, column=1, sticky=tk.EW, pady=4, padx=4)
		entry_notes = ttk.Entry(form, textvariable=notes_var)
		entry_notes.grid(row=5, column=1, sticky=tk.EW, pady=4, padx=4)

		form.columnconfigure(1, weight=1)

		btns = ttk.Frame(dlg)
		btns.pack(pady=8)
		ok = ttk.Button(btns, text="Save", command=lambda: on_save())
		cancel = ttk.Button(btns, text="Cancel", command=dlg.destroy)
		ok.pack(side=tk.LEFT, padx=6)
		cancel.pack(side=tk.LEFT)

		def on_save() -> None:
			try:
				pid = patient_name_to_id.get(patient_var.get())
				if not pid:
					raise ValueError("Select a patient")
				date = date_var.get().strip()
				time = time_var.get().strip()
				duration = int(duration_var.get().strip() or 30)
				doctor = doctor_var.get().strip()
				notes = notes_var.get().strip() or None
				if not date or not time or not doctor:
					raise ValueError("Date, Time, and Doctor are required")
				if appt:
					upd = Appointment(id=appt.id, patient_id=pid, date=date, time=time, duration_minutes=duration, doctor=doctor, notes=notes)
					self.appointment_service.update_appointment(upd)
				else:
					new_appt = Appointment(id=None, patient_id=pid, date=date, time=time, duration_minutes=duration, doctor=doctor, notes=notes)
					self.appointment_service.create_appointment(new_appt)
				dlg.destroy()
				self.refresh()
			except Exception as e:
				messagebox.showerror("Save Appointment", str(e))

	def focus_patient(self, patient_id: int) -> None:
		# Filter to this patient's appointments
		for i in self.tree.get_children(""):
			self.tree.delete(i)
		rows = self.appointment_service.list_appointments_for_patient(patient_id)
		patient = self.patient_service.get_patient(patient_id)
		name = patient.name if patient else str(patient_id)
		for a in rows:
			self.tree.insert("", tk.END, values=(a.id, name, a.date, a.time, a.duration_minutes, a.doctor, a.notes or ""))
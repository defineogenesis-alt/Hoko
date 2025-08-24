import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional

from models import Patient
from services.patient_service import PatientService
from services.treatment_service import TreatmentService
from services.invoice_service import InvoiceService


class PatientsView(ttk.Frame):
	def __init__(self, parent, patient_service: PatientService, treatment_service: TreatmentService, invoice_service: InvoiceService, on_open_appointments: Optional[Callable[[int], None]] = None) -> None:
		super().__init__(parent)
		self.patient_service = patient_service
		self.treatment_service = treatment_service
		self.invoice_service = invoice_service
		self.on_open_appointments = on_open_appointments

		self.search_var = tk.StringVar()
		self._build_ui()
		self.refresh()

	def _build_ui(self) -> None:
		top = ttk.Frame(self)
		top.pack(fill=tk.X, padx=8, pady=8)
		entry = ttk.Entry(top, textvariable=self.search_var)
		entry.pack(side=tk.LEFT)
		btn = ttk.Button(top, text="Search", command=self._on_search)
		btn.pack(side=tk.LEFT, padx=6)
		clear = ttk.Button(top, text="Clear", command=self._on_clear)
		clear.pack(side=tk.LEFT)

		add_btn = ttk.Button(top, text="Add", command=self._on_add)
		edit_btn = ttk.Button(top, text="Edit", command=self._on_edit)
		del_btn = ttk.Button(top, text="Delete", command=self._on_delete)
		appt_btn = ttk.Button(top, text="Appointments", command=self._on_open_appointments)
		for b in (add_btn, edit_btn, del_btn, appt_btn):
			b.pack(side=tk.RIGHT, padx=4)

		columns = ("id", "name", "age", "gender", "phone", "address")
		self.tree = ttk.Treeview(self, columns=columns, show="headings")
		for col in columns:
			self.tree.heading(col, text=col.title(), command=lambda c=col: self._sort_by(c))
			self.tree.column(col, width=120 if col != "address" else 220, anchor=tk.W)
		self.tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

		self._sort_dir = {c: True for c in columns}

	def _sort_by(self, column: str) -> None:
		items = [(self.tree.set(k, column), k) for k in self.tree.get_children("")]
		is_numeric = column in {"id", "age"}
		try:
			items.sort(key=lambda x: (float(x[0]) if x[0] != "" else -1) if is_numeric else x[0].lower(), reverse=self._sort_dir[column])
		except Exception:
			items.sort(key=lambda x: x[0], reverse=self._sort_dir[column])
		for index, (_, k) in enumerate(items):
			self.tree.move(k, "", index)
		self._sort_dir[column] = not self._sort_dir[column]

	def refresh(self) -> None:
		for i in self.tree.get_children(""):
			self.tree.delete(i)
		patients = self.patient_service.list_patients(self.search_var.get())
		for p in patients:
			self.tree.insert("", tk.END, values=(p.id, p.name, p.age or "", p.gender or "", p.phone or "", p.address or ""))

	def _on_search(self) -> None:
		self.refresh()

	def _on_clear(self) -> None:
		self.search_var.set("")
		self.refresh()

	def _on_add(self) -> None:
		self._open_form()

	def _on_edit(self) -> None:
		item = self.tree.focus()
		if not item:
			messagebox.showwarning("Edit Patient", "Please select a patient to edit.")
			return
		values = self.tree.item(item, "values")
		patient = Patient(id=int(values[0]), name=values[1], age=int(values[2]) if values[2] else None, gender=values[3] or None, phone=values[4] or None, address=values[5] or None)
		self._open_form(patient)

	def _on_delete(self) -> None:
		item = self.tree.focus()
		if not item:
			messagebox.showwarning("Delete Patient", "Please select a patient to delete.")
			return
		values = self.tree.item(item, "values")
		pid = int(values[0])
		if messagebox.askyesno("Confirm", "Delete selected patient? This removes related appointments and treatments."):
			self.patient_service.delete_patient(pid)
			self.refresh()

	def _open_form(self, patient: Optional[Patient] = None) -> None:
		dlg = tk.Toplevel(self)
		dlg.title("Patient" + (" - Edit" if patient else " - Add"))
		dlg.grab_set()

		name_var = tk.StringVar(value=patient.name if patient else "")
		age_var = tk.StringVar(value=str(patient.age) if patient and patient.age is not None else "")
		gender_var = tk.StringVar(value=patient.gender if patient else "")
		phone_var = tk.StringVar(value=patient.phone if patient else "")
		addr_var = tk.StringVar(value=patient.address if patient else "")

		form = ttk.Frame(dlg)
		form.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

		labels = ["Name", "Age", "Gender", "Phone", "Address"]
		vars = [name_var, age_var, gender_var, phone_var, addr_var]
		for i, (label, var) in enumerate(zip(labels, vars)):
			l = ttk.Label(form, text=label)
			l.grid(row=i, column=0, sticky=tk.W, pady=4, padx=4)
			entry = ttk.Entry(form, textvariable=var)
			entry.grid(row=i, column=1, sticky=tk.EW, pady=4, padx=4)
		form.columnconfigure(1, weight=1)

		btns = ttk.Frame(dlg)
		btns.pack(pady=8)
		ok = ttk.Button(btns, text="Save", command=lambda: on_save())
		cancel = ttk.Button(btns, text="Cancel", command=dlg.destroy)
		ok.pack(side=tk.LEFT, padx=6)
		cancel.pack(side=tk.LEFT)

		def on_save() -> None:
			name = name_var.get().strip()
			age_txt = age_var.get().strip()
			age = int(age_txt) if age_txt.isdigit() else None
			gender = gender_var.get().strip() or None
			phone = phone_var.get().strip() or None
			addr = addr_var.get().strip() or None
			if not name:
				messagebox.showerror("Validation", "Name is required")
				return
			if patient:
				upd = Patient(id=patient.id, name=name, age=age, gender=gender, phone=phone, address=addr)
				self.patient_service.update_patient(upd)
			else:
				pid = self.patient_service.create_patient(Patient(id=None, name=name, age=age, gender=gender, phone=phone, address=addr))
				# Select new patient possibly
			dlg.destroy()
			self.refresh()

	def _on_open_appointments(self) -> None:
		item = self.tree.focus()
		if not item:
			messagebox.showinfo("Appointments", "Select a patient first.")
			return
		pid = int(self.tree.item(item, "values")[0])
		if self.on_open_appointments:
			self.on_open_appointments(pid)

	def set_search(self, text: str) -> None:
		self.search_var.set(text)
		self.refresh()

	def focus_patient(self, patient_id: int) -> None:
		# Try to select patient in table
		for iid in self.tree.get_children(""):
			vals = self.tree.item(iid, "values")
			if int(vals[0]) == patient_id:
				self.tree.selection_set(iid)
				self.tree.focus(iid)
				self.tree.see(iid)
				break
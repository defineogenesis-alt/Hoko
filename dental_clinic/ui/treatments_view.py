import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional

from dental_clinic.models import Treatment, Patient
from dental_clinic.services.patient_service import PatientService
from dental_clinic.services.treatment_service import TreatmentService
from dental_clinic.services.invoice_service import InvoiceService


class TreatmentsView(ttk.Frame):
	def __init__(self, parent, patient_service: PatientService, treatment_service: TreatmentService, invoice_service: InvoiceService) -> None:
		super().__init__(parent)
		self.patient_service = patient_service
		self.treatment_service = treatment_service
		self.invoice_service = invoice_service

		self._build_ui()

	def _build_ui(self) -> None:
		top = ttk.Frame(self)
		top.pack(fill=tk.X, padx=8, pady=8)

		self.patient_combo_var = tk.StringVar()
		self._reload_patients()
		self.patient_combo = ttk.Combobox(top, textvariable=self.patient_combo_var, state="readonly")
		self.patient_combo["values"] = [p.name for p in self._patients]
		self.patient_combo.pack(side=tk.LEFT, padx=(0, 8))
		self.patient_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh())

		add_btn = ttk.Button(top, text="Add", command=self._on_add)
		edit_btn = ttk.Button(top, text="Edit", command=self._on_edit)
		del_btn = ttk.Button(top, text="Delete", command=self._on_delete)
		invoice_btn = ttk.Button(top, text="Create Invoice PDF", command=self._on_invoice_pdf)
		for b in (add_btn, edit_btn, del_btn, invoice_btn):
			b.pack(side=tk.RIGHT, padx=4)

		columns = ("id", "date", "type", "description", "cost")
		self.tree = ttk.Treeview(self, columns=columns, show="headings")
		for c in columns:
			self.tree.heading(c, text=c.title())
			self.tree.column(c, width=130 if c != "description" else 300, anchor=tk.W)
		self.tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

	def _reload_patients(self) -> None:
		self._patients = self.patient_service.list_patients()
		if self._patients:
			self.patient_combo_var.set(self._patients[0].name)

	def refresh(self) -> None:
		for i in self.tree.get_children(""):
			self.tree.delete(i)
		patient = self._get_selected_patient()
		if not patient:
			return
		treatments = self.treatment_service.list_treatments_for_patient(patient.id)
		for t in treatments:
			self.tree.insert("", tk.END, values=(t.id, t.date, t.type, t.description or "", f"{t.cost:.2f}"))

	def _get_selected_patient(self) -> Optional[Patient]:
		name = self.patient_combo_var.get()
		for p in self._patients:
			if p.name == name:
				return p
		return None

	def _on_add(self) -> None:
		patient = self._get_selected_patient()
		if not patient:
			messagebox.showinfo("Treatment", "Select a patient first.")
			return
		self._open_form(patient)

	def _on_edit(self) -> None:
		patient = self._get_selected_patient()
		if not patient:
			messagebox.showinfo("Treatment", "Select a patient first.")
			return
		item = self.tree.focus()
		if not item:
			messagebox.showwarning("Edit Treatment", "Select a treatment to edit.")
			return
		v = self.tree.item(item, "values")
		t = Treatment(id=int(v[0]), patient_id=patient.id, date=v[1], type=v[2], description=v[3], cost=float(v[4]))
		self._open_form(patient, t)

	def _on_delete(self) -> None:
		item = self.tree.focus()
		if not item:
			messagebox.showwarning("Delete Treatment", "Select a treatment to delete.")
			return
		v = self.tree.item(item, "values")
		if messagebox.askyesno("Confirm", "Delete selected treatment?"):
			self.treatment_service.delete_treatment(int(v[0]))
			self.refresh()

	def _open_form(self, patient: Patient, treatment: Optional[Treatment] = None) -> None:
		dlg = tk.Toplevel(self)
		dlg.title("Treatment" + (" - Edit" if treatment else " - Add"))
		dlg.grab_set()

		date_var = tk.StringVar(value=treatment.date if treatment else "")
		type_var = tk.StringVar(value=treatment.type if treatment else "")
		desc_var = tk.StringVar(value=treatment.description if treatment else "")
		cost_var = tk.StringVar(value=str(treatment.cost) if treatment else "0.00")

		form = ttk.Frame(dlg)
		form.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

		labels = ["Date (YYYY-MM-DD)", "Type", "Description", "Cost"]
		for i, label in enumerate(labels):
			ttk.Label(form, text=label).grid(row=i, column=0, sticky=tk.W, pady=4, padx=4)
		entry_date = ttk.Entry(form, textvariable=date_var)
		entry_date.grid(row=0, column=1, sticky=tk.EW, pady=4, padx=4)
		entry_type = ttk.Entry(form, textvariable=type_var)
		entry_type.grid(row=1, column=1, sticky=tk.EW, pady=4, padx=4)
		entry_desc = ttk.Entry(form, textvariable=desc_var)
		entry_desc.grid(row=2, column=1, sticky=tk.EW, pady=4, padx=4)
		entry_cost = ttk.Entry(form, textvariable=cost_var)
		entry_cost.grid(row=3, column=1, sticky=tk.EW, pady=4, padx=4)

		form.columnconfigure(1, weight=1)

		btns = ttk.Frame(dlg)
		btns.pack(pady=8)
		ok = ttk.Button(btns, text="Save", command=lambda: on_save())
		cancel = ttk.Button(btns, text="Cancel", command=dlg.destroy)
		ok.pack(side=tk.LEFT, padx=6)
		cancel.pack(side=tk.LEFT)

		def on_save() -> None:
			try:
				date = date_var.get().strip()
				type_ = type_var.get().strip()
				desc = desc_var.get().strip() or None
				cost = float(cost_var.get().strip() or 0)
				if not date or not type_:
					raise ValueError("Date and Type are required")
				if treatment:
					upd = Treatment(id=treatment.id, patient_id=patient.id, date=date, type=type_, description=desc, cost=cost)
					self.treatment_service.update_treatment(upd)
				else:
					new_t = Treatment(id=None, patient_id=patient.id, date=date, type=type_, description=desc, cost=cost)
					self.treatment_service.add_treatment(new_t)
				dlg.destroy()
				self.refresh()
			except Exception as e:
				messagebox.showerror("Save Treatment", str(e))

	def _on_invoice_pdf(self) -> None:
		patient = self._get_selected_patient()
		if not patient:
			messagebox.showinfo("Invoice", "Select a patient first.")
			return
		# Gather treatments in table for this patient as invoice items
		items = []
		for iid in self.tree.get_children(""):
			v = self.tree.item(iid, "values")
			desc = f"{v[1]} - {v[2]}"
			amount = float(v[4])
			items.append((desc, amount))
		if not items:
			messagebox.showinfo("Invoice", "No treatments to invoice.")
			return
		path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], initialfile=f"invoice_{patient.name}.pdf")
		if not path:
			return
		from datetime import date
		invoice_id = self.invoice_service.create_invoice(patient.id, items, date.today().isoformat())
		out = self.invoice_service.export_invoice_pdf(invoice_id, path, patient.name)
		messagebox.showinfo("Invoice", f"Saved PDF: {out}")
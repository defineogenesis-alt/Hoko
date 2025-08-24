import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from dental_clinic.services.patient_service import PatientService
from dental_clinic.services.treatment_service import TreatmentService
from dental_clinic.services.backup_service import backup_database, restore_database


class ReportsView(ttk.Frame):
	def __init__(self, parent, patient_service: PatientService, treatment_service: TreatmentService) -> None:
		super().__init__(parent)
		self.patient_service = patient_service
		self.treatment_service = treatment_service
		self._icons = None
		self._build_ui()

	def set_icons(self, icons: dict) -> None:
		self._icons = icons
		try:
			self.refresh_btn.configure(image=self._icons.get("search"), compound=tk.LEFT)
			self.backup_btn.configure(image=self._icons.get("backup"), compound=tk.LEFT)
			self.restore_btn.configure(image=self._icons.get("restore"), compound=tk.LEFT)
		except Exception:
			pass

	def _build_ui(self) -> None:
		top = ttk.Frame(self)
		top.pack(fill=tk.X, padx=8, pady=8)
		self.refresh_btn = ttk.Button(top, text="Refresh", command=self._render)
		self.refresh_btn.pack(side=tk.RIGHT, padx=4)
		self.backup_btn = ttk.Button(top, text="Backup DB", command=self._on_backup)
		self.restore_btn = ttk.Button(top, text="Restore DB", command=self._on_restore)
		self.backup_btn.pack(side=tk.RIGHT, padx=4)
		self.restore_btn.pack(side=tk.RIGHT, padx=4)

		self.canvas_container = ttk.Frame(self)
		self.canvas_container.pack(fill=tk.BOTH, expand=True)

		self._render()

	def _render(self) -> None:
		for w in self.canvas_container.winfo_children():
			w.destroy()
		# Lazy import to avoid requiring matplotlib for headless tests unless viewing
		import matplotlib
		matplotlib.use("Agg")
		from matplotlib.figure import Figure
		from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

		# Patients per month - using created_at in patients
		fig = Figure(figsize=(5, 3), dpi=100)
		ax1 = fig.add_subplot(121)
		ax2 = fig.add_subplot(122)

		# Patients per month
		rows = self.patient_service.db.query("SELECT substr(created_at,1,7) ym, COUNT(*) c FROM patients GROUP BY ym ORDER BY ym")
		x1 = [r["ym"] for r in rows]
		y1 = [r["c"] for r in rows]
		ax1.bar(x1, y1, color="#4e79a7")
		ax1.set_title("Patients / Month")
		ax1.tick_params(axis='x', rotation=45)

		# Revenue by month from treatments
		rev = self.treatment_service.revenue_summary_by_month()
		x2 = [r[0] for r in rev]
		y2 = [r[1] for r in rev]
		ax2.plot(x2, y2, marker='o', color="#f28e2b")
		ax2.set_title("Revenue / Month")
		ax2.tick_params(axis='x', rotation=45)

		fig.tight_layout()

		canvas = FigureCanvasTkAgg(fig, master=self.canvas_container)
		canvas.draw()
		widget = canvas.get_tk_widget()
		widget.pack(fill=tk.BOTH, expand=True)

	def _on_backup(self) -> None:
		path = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("SQLite DB", "*.db")], initialfile="dental_clinic_backup.db")
		if not path:
			return
		try:
			backup_database(self.patient_service.db, path)
			messagebox.showinfo("Backup", f"Database saved to {path}")
		except Exception as e:
			messagebox.showerror("Backup", str(e))

	def _on_restore(self) -> None:
		path = filedialog.askopenfilename(filetypes=[("SQLite DB", "*.db"), ("All", "*.*")])
		if not path:
			return
		if not messagebox.askyesno("Restore", "Restoring will overwrite current data. Continue?"):
			return
		try:
			restore_database(self.patient_service.db, path)
			messagebox.showinfo("Restore", "Database restored. Please restart the application.")
		except Exception as e:
			messagebox.showerror("Restore", str(e))
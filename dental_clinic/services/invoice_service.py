from typing import List, Tuple
from decimal import Decimal, ROUND_HALF_UP
import os

from dental_clinic.services.database import Database
from dental_clinic.models import Invoice, InvoiceItem


class InvoiceService:
	def __init__(self, db: Database) -> None:
		self.db = db

	def create_invoice(self, patient_id: int, items: List[Tuple[str, float]], invoice_date: str) -> int:
		"""Create invoice and items, compute total."""
		total = float(sum(Decimal(str(a)) for _, a in items))
		invoice_id = self.db.execute(
			"INSERT INTO invoices(patient_id, invoice_date, total, paid) VALUES(?,?,?,0)",
			(patient_id, invoice_date, total),
		)
		for desc, amount in items:
			self.db.execute(
				"INSERT INTO invoice_items(invoice_id, description, amount) VALUES(?,?,?)",
				(invoice_id, desc, float(Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))),
			)
		return invoice_id

	def list_invoice_items(self, invoice_id: int) -> List[InvoiceItem]:
		rows = self.db.query("SELECT * FROM invoice_items WHERE invoice_id=?", (invoice_id,))
		return [
			InvoiceItem(id=r["id"], invoice_id=r["invoice_id"], description=r["description"], amount=r["amount"]) for r in rows
		]

	def get_invoice(self, invoice_id: int) -> Invoice:
		row = self.db.query("SELECT * FROM invoices WHERE id=?", (invoice_id,))[0]
		return Invoice(
			id=row["id"], patient_id=row["patient_id"], invoice_date=row["invoice_date"], total=row["total"], paid=row["paid"]
		)

	def export_invoice_pdf(self, invoice_id: int, output_path: str, patient_name: str) -> str:
		from reportlab.lib.pagesizes import A4
		from reportlab.pdfgen import canvas
		from reportlab.lib.units import mm
		from reportlab.lib import colors

		invoice = self.get_invoice(invoice_id)
		items = self.list_invoice_items(invoice_id)

		os.makedirs(os.path.dirname(output_path), exist_ok=True)
		c = canvas.Canvas(output_path, pagesize=A4)
		width, height = A4

		y = height - 40 * mm
		c.setFont("Helvetica-Bold", 16)
		c.drawString(25 * mm, y, "Dental Clinic Invoice")
		y -= 10 * mm
		c.setFont("Helvetica", 10)
		c.drawString(25 * mm, y, f"Invoice ID: {invoice.id}")
		y -= 6 * mm
		c.drawString(25 * mm, y, f"Date: {invoice.invoice_date}")
		y -= 6 * mm
		c.drawString(25 * mm, y, f"Patient: {patient_name}")
		y -= 12 * mm

		# Table header
		c.setFont("Helvetica-Bold", 11)
		c.drawString(25 * mm, y, "Description")
		c.drawRightString(180 * mm, y, "Amount ($)")
		y -= 5 * mm
		c.setStrokeColor(colors.grey)
		c.line(25 * mm, y, 180 * mm, y)
		y -= 5 * mm

		c.setFont("Helvetica", 10)
		for item in items:
			if y < 30 * mm:
				c.showPage()
				y = height - 30 * mm
			c.drawString(25 * mm, y, item.description)
			c.drawRightString(180 * mm, y, f"{item.amount:.2f}")
			y -= 6 * mm

		# Total
		y -= 6 * mm
		c.setFont("Helvetica-Bold", 12)
		c.drawRightString(180 * mm, y, f"Total: ${invoice.total:.2f}")

		c.showPage()
		c.save()
		return output_path
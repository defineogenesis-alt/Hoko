import os
import sys

try:
	import ttkbootstrap as ttkb  # type: ignore[import-not-found]
	except_import = None
except Exception as e:  # Fallback when ttkbootstrap is unavailable
	except_import = e
	ttkb = None

import tkinter as tk
from tkinter import ttk, messagebox

from ui.main_window import DentalClinicApp
from services.database import Database


def main() -> None:
	base_dir = os.path.dirname(os.path.abspath(__file__))
	db_path = os.path.join(base_dir, "dental_clinic.db")

	database = Database(db_path)
	database.initialize_schema()

	# Prefer ttkbootstrap themed window when available
	if ttkb is not None:
		app = DentalClinicApp(database, use_ttkbootstrap=True)
	else:
		app = DentalClinicApp(database, use_ttkbootstrap=False)
	app.mainloop()


if __name__ == "__main__":
	main()
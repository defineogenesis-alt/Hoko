from typing import Dict
from PIL import Image, ImageDraw, ImageTk
import tkinter as tk


_DEF_COLORS = {
	"patients": "#4e79a7",
	"appointments": "#59a14f",
	"treatments": "#e15759",
	"reports": "#f28e2b",
	"search": "#9c755f",
	"backup": "#76b7b2",
	"restore": "#edc948",
}


def _new_canvas(size: int) -> Image.Image:
	img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
	return img


def _draw_patients(size: int, color: str) -> Image.Image:
	img = _new_canvas(size)
	d = ImageDraw.Draw(img)
	# Two simple heads and shoulders
	r = size // 5
	d.ellipse((size*0.18 - r, size*0.30 - r, size*0.18 + r, size*0.30 + r), outline=color, width=max(1, size//18))
	d.ellipse((size*0.52 - r, size*0.30 - r, size*0.52 + r, size*0.30 + r), outline=color, width=max(1, size//18))
	d.rounded_rectangle((size*0.07, size*0.50, size*0.63, size*0.85), radius=size//10, outline=color, width=max(1, size//18))
	return img


def _draw_calendar(size: int, color: str) -> Image.Image:
	img = _new_canvas(size)
	d = ImageDraw.Draw(img)
	pad = size*0.12
	d.rectangle((pad, pad*0.9, size-pad, size-pad), outline=color, width=max(1, size//18))
	d.line((pad, pad*1.6, size-pad, pad*1.6), fill=color, width=max(1, size//22))
	# Rings
	d.line((size*0.35, pad*0.5, size*0.35, pad*1.0), fill=color, width=max(1, size//18))
	d.line((size*0.65, pad*0.5, size*0.65, pad*1.0), fill=color, width=max(1, size//18))
	return img


def _draw_cross(size: int, color: str) -> Image.Image:
	img = _new_canvas(size)
	d = ImageDraw.Draw(img)
	w = max(2, size//6)
	cx = cy = size/2
	d.line((cx - size*0.32, cy, cx + size*0.32, cy), fill=color, width=w)
	d.line((cx, cy - size*0.32, cx, cy + size*0.32), fill=color, width=w)
	return img


def _draw_chart(size: int, color: str) -> Image.Image:
	img = _new_canvas(size)
	d = ImageDraw.Draw(img)
	pad = size*0.15
	# axes
	d.line((pad, size - pad, size - pad, size - pad), fill=color, width=max(1, size//20))
	d.line((pad, size - pad, pad, pad), fill=color, width=max(1, size//20))
	# line
	points = [
		(pad, size - pad*1.4),
		(size*0.45, size*0.55),
		(size*0.65, size*0.40),
		(size - pad, size*0.30),
	]
	d.line(points, fill=color, width=max(1, size//18), joint="curve")
	return img


def _draw_magnifier(size: int, color: str) -> Image.Image:
	img = _new_canvas(size)
	d = ImageDraw.Draw(img)
	r = size*0.28
	cx = cy = size*0.45
	d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=color, width=max(1, size//18))
	d.line((cx + r*0.6, cy + r*0.6, size*0.92, size*0.92), fill=color, width=max(1, size//18))
	return img


def _draw_backup(size: int, color: str) -> Image.Image:
	img = _new_canvas(size)
	d = ImageDraw.Draw(img)
	pad = size*0.18
	# box
	d.rectangle((pad, size*0.55, size-pad, size-pad), outline=color, width=max(1, size//18))
	# arrow up
	arrow = [
		(size*0.5, size*0.15), (size*0.75, size*0.40), (size*0.60, size*0.40), (size*0.60, size*0.62), (size*0.40, size*0.62), (size*0.40, size*0.40), (size*0.25, size*0.40)
	]
	d.line(arrow + [arrow[0]], fill=color, width=max(1, size//20))
	return img


def _draw_restore(size: int, color: str) -> Image.Image:
	img = _new_canvas(size)
	d = ImageDraw.Draw(img)
	pad = size*0.18
	# box
	d.rectangle((pad, size*0.15, size-pad, size*0.45), outline=color, width=max(1, size//18))
	# arrow down
	arrow = [
		(size*0.5, size*0.85), (size*0.75, size*0.60), (size*0.60, size*0.60), (size*0.60, size*0.38), (size*0.40, size*0.38), (size*0.40, size*0.60), (size*0.25, size*0.60)
	]
	d.line(arrow + [arrow[0]], fill=color, width=max(1, size//20))
	return img


_DRAWERS = {
	"patients": _draw_patients,
	"appointments": _draw_calendar,
	"treatments": _draw_cross,
	"reports": _draw_chart,
	"search": _draw_magnifier,
	"backup": _draw_backup,
	"restore": _draw_restore,
}


def load_icons(root: tk.Misc, size: int = 18) -> Dict[str, ImageTk.PhotoImage]:
	icons: Dict[str, ImageTk.PhotoImage] = {}
	for name, drawer in _DRAWERS.items():
		img = drawer(size, _DEF_COLORS.get(name, "#444"))
		icons[name] = ImageTk.PhotoImage(img, master=root)
	return icons
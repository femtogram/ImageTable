import math
import pangocairo
import pango
import cairo

import inputmanager

needs_update = False

radius = 20
pos = [3, -5]
min_pos = (3, -5)
max_pos = (17, 17)

help_on = False

ownerstr = 'help'

def draw(cr, width, height):
	global needs_update

	if inputmanager.owner == ownerstr or help_on:
		pos[0] = min(pos[0] + 5, max_pos[0])
		pos[1] = min(pos[1] + 5, max_pos[1])
	else:
		pos[0] = max(pos[0] - 5, min_pos[0])
		pos[1] = max(pos[1] - 5, min_pos[1])

	cr.translate(*pos)
	cr.rotate(0.3)
	cr.set_source_rgba(0.4, 0.4, 0.4, 0.8)
	cr.arc(0, 0, radius, 0, 2 * math.pi)
	cr.fill()
	cr.save()
	pc = pangocairo.CairoContext(cr)
	pc.set_antialias(cairo.ANTIALIAS_SUBPIXEL)

	layout = pc.create_layout()

	layout.set_font_description(pango.FontDescription('Sans 30'))
	layout.set_text('?')
	layout.set_alignment(pango.ALIGN_CENTER)
	cr.set_source_rgba(1, 1, 1, 0.4)
	tw, th = layout.get_pixel_size()
	cr.translate(-tw / 2, -th / 2)

	pc.update_layout(layout)
	pc.show_layout(layout)

	cr.restore()

	if tuple(pos) != min_pos and tuple(pos) != max_pos:
		needs_update = True
	else:
		needs_update = False

def check_mouse_over(widget, event):
	global needs_update

	if event.x <= pos[0] + radius and event.y <= pos[1] + radius:
		diff_x_sq = event.x - pos[0]
		diff_x_sq *= diff_x_sq

		diff_y_sq = event.y - pos[1]
		diff_y_sq *= diff_y_sq

		if diff_x_sq + diff_y_sq <= radius * radius:
			if tuple(pos) == min_pos:
				needs_update = True
			return ownerstr

	if help_on:
		return ownerstr

	if not help_on and tuple(pos) != min_pos:
		needs_update = True

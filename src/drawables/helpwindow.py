import pangocairo
import cairo
import pango

import helpicon
from utilities import text

needs_update = False

border = 45

description = \
'\tImageTable allows for simple image viewing of local \
file and clipboard images.'

help = (('<Action>', '<shortcut>'),
		('Help', 'h,/,?'),
		('Paste image into viewer', 'p,ctrl-v'),
		('Toggle window on top', 't'),
		('Display hex color at cursor','c'),
		('Zoom in', '+,='),
		('Zoom out', '-'))

def draw_help_text(cr, width, height, x_center, y, text_width, y_pos, help_item):
	cr.save()
	text.draw_font_left(cr, x_center - text_width / 2, y + y_pos * 20, 'Sans 10', help_item[0])
	text.draw_font_right(cr, x_center + text_width / 2, y + y_pos * 20, 'Sans 10', help_item[1])

	cr.restore()

def draw(cr, width, height):
	if helpicon.help_on:
		help_width = width - border * 2
		padding = 10

		cr.set_source_rgba(0.4, 0.4, 0.4, 0.95)
		cr.rectangle(border, 0, help_width, height)
		cr.fill()

		cr.set_source_rgba(1, 1, 1, 0.4)
		text.draw_font_left(cr, border + padding, 5, 'Sans 20', 'help')
		cr.set_source_rgba(1, 1, 1, 0.8)
		off_y = text.draw_font_left_wrap(cr, border + padding, 50, 'Sans 12', description, help_width - padding * 2)[1]
		print 'off_y'
		for i, val in enumerate(help):
			draw_help_text(cr, width, height, width / 2, 80 + off_y, help_width - padding * 2, i, val)

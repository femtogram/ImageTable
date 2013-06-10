import pangocairo
import cairo
import pango

def _draw_font(cr, x, y, font_name, text, align, wrap_width, rot_angle):
	cr.save()

	pc = pangocairo.CairoContext(cr)
	pc.set_antialias(cairo.ANTIALIAS_SUBPIXEL)

	layout = pc.create_layout()

	layout.set_font_description(pango.FontDescription(font_name))
	layout.set_text(text)
	if wrap_width:
		layout.set_wrap(pango.WRAP_WORD)
		layout.set_width(pango.SCALE * wrap_width)

	dim = layout.get_pixel_size()
	cr.translate(x, y)
	x = 0
	y = 0
	if align == 'right':
		x = -dim[0]
	if align == 'center':
		x = -dim[0] / 2
		y = -dim[1] / 2
	cr.rotate(rot_angle)
	cr.translate(x, y)
	pc.update_layout(layout)
	pc.show_layout(layout)

	cr.restore()

	return dim

def draw_font_left(cr, x, y, font_name, text):
	return _draw_font(cr, x, y, font_name, text, 'left', None, 0)

def draw_font_right(cr, x, y, font_name, text):
	return _draw_font(cr, x, y, font_name, text, 'right', None, 0)

def draw_font_center(cr, x, y, font_name, text):
	return _draw_font(cr, x, y, font_name, text, 'center', None, 0)

def draw_font_left_wrap(cr, x, y, font_name, text, wrap_width):
	return _draw_font(cr, x, y, font_name, text, 'left', wrap_width, 0)

def draw_font_right_wrap(cr, x, y, font_name, text, wrap_width):
	return _draw_font(cr, x, y, font_name, text, 'right', wrap_width, 0)

def draw_font_center_wrap(cr, x, y, font_name, text, wrap_width):
	return _draw_font(cr, x, y, font_name, text, 'center', wrap_width, 0)

def draw_font_center_rotate(cr, x, y, font_name, text, rot_angle):
	return _draw_font(cr, x, y, font_name, text, 'center', None, rot_angle)

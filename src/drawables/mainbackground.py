import cairo

needs_update = False

def draw(cr, width, height):
	global needs_update

	cr.rectangle(0, 0, width, height)
	cr.set_source_rgb(0.1, 0.1, 0.1)
	cr.fill()

	needs_update = False

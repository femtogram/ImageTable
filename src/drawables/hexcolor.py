import gtk
from utilities import text

needs_update = False

ownerstr = 'hexcolor'

hexcolor = None

def draw(cr, width, height):
	if not hexcolor:
		return
	cr.save()

	cr.translate(0, height - 12)
	cr.rectangle(0, 0, 56, 12)
	cr.set_source_rgba(0.4, 0.4, 0.4, 0.8)
	cr.fill()
	cr.set_source_rgba(1, 1, 1, 0.8)
	text.draw_font_left(cr, 2, 0, 'Courier 8', hexcolor)

	cr.restore()

def sethexcolor():
	global needs_update
	global hexcolor

	root_window = gtk.gdk.get_default_root_window()
	disp = root_window.get_screen().get_display()
	pointer_x, pointer_y = disp.get_pointer()[1:3]

	if not disp.get_window_at_pointer():
		return

	pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 1, 1)
	pixbuf = pixbuf.get_from_drawable(root_window, root_window.get_colormap(), pointer_x, pointer_y, 0, 0, 1, 1)
	tup = tuple(map(ord, pixbuf.get_pixels()[:3]))

	res = '0x'
	res += ''.join(['{0:0<2}'.format(hex(color)[2:]) for color in tup])
	if res != hexcolor:
		hexcolor = res
		needs_update = True

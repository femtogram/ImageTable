import imageloader
import gtk

needs_update = False

zoom = 1
pos_x = 0
pos_y = 0

screen_width = 640
screen_height = 480

ownerstr = 'mainimage'

def on_window_resize(widget):
	global screen_width
	global screen_height
	global needs_update
	
	# screen_width, screen_height = widget.get_size()
	needs_update = True

def zoom_in():
	global screen_width
	global screen_height

	zoom_direction(False, screen_width / 2, screen_height / 2)

def zoom_out():
	global screen_width
	global screen_height

	zoom_direction(True, screen_width / 2, screen_height / 2)

def zoom_direction(direction, center_x, center_y):
	global zoom
	global pos_x
	global pos_y
	global needs_update

	prev_zoom = zoom
	zoom *= (0.8 if direction else 1.2)
	s = zoom / prev_zoom
	pos_x = center_x - s * (center_x - pos_x)
	pos_y = center_y - s * (center_y - pos_y)

	needs_update = True

def draw(cr, width, height):
	global screen_width
	global screen_height

	screen_width = width
	screen_height = height
	if imageloader.image is not None:
		print imageloader.image
		draw_image(cr, imageloader.image, width, height)

def draw_image(cr, img, width, height):
	global zoom
	global pos_x
	global pos_y

	print 'pos: {', pos_x, ', ', pos_y, '}'

	tmpwidth = int(zoom * img.get_width())
	tmpheight = int(zoom * img.get_height())

	if pos_x < -tmpwidth:
		pos_x = -tmpwidth
	elif pos_x > width:
		pos_x = width
	if pos_y < -tmpheight:
		pos_y = -tmpheight
	elif pos_y > height:
		pos_y = height
	
	cr.translate(pos_x, pos_y)

	gdkcr = gtk.gdk.CairoContext(cr)
	if zoom < 1:
		tmpimg = img.scale_simple(tmpwidth, tmpheight, gtk.gdk.INTERP_NEAREST)
		gdkcr.set_source_pixbuf(tmpimg, 0, 0)
	else:
		gdkcr.scale(zoom, zoom)
		gdkcr.set_source_pixbuf(img, 0, 0)

	gdkcr.paint()

def center_image():
	global zoom
	global pos_x
	global pos_y
	global needs_update
	global screen_width
	global screen_height

	x_ratio = 1.0 * screen_width / imageloader.image.get_width()
	y_ratio = 1.0 * screen_height / imageloader.image.get_height()

	x_diff = screen_width - y_ratio * imageloader.image.get_width()
	y_diff = screen_height - x_ratio * imageloader.image.get_height()

	if x_diff < y_diff:
		print 'this one'
		zoom = x_ratio
		pos_x = 0
		pos_y = (screen_height - zoom * imageloader.image.get_height()) / 2

	else:
		print 'that other one'
		zoom = y_ratio
		pos_x = (screen_width - zoom * imageloader.image.get_width()) / 2
		pos_y = 0

	needs_update = True

def check_mouse_over(widget, event):
	return 'mainimage' if imageloader.image else 'mainbackground'

import math
import imageloader
from utilities import filechooser
from utilities import text
from drawables import mainimage

needs_update = False
ownerstr = 'menu'
state = True
center = (300, 300)
backgroundcolor = (0.2, 0.2, 0.2, 0.95)
bordercolor = (0.4, 0.4, 0.4, 0.8)
fontcolor = (0.8, 0.8, 0.8, 0.8)

menuitems = {('Open', filechooser.open_file_dialog), ('Zoom In', mainimage.zoom_in), ('Zoom Out', mainimage.zoom_out), ('Reset Image', mainimage.center_image)}

def draw(cr, width, height):
	print 'drawing rightclickmenu'
	if not state:
		return
	cr.save()
	cr.set_source_rgba(*backgroundcolor)
	cr.arc(center[0], center[1], 100, 0, 2 * math.pi)
	cr.fill()
	draw_sectors(cr)
	cr.set_source_rgba(*bordercolor)
	cr.arc(center[0], center[1], 100, 0, 2 * math.pi)
	cr.stroke()
	cr.restore()

def draw_sectors(cr):
	ang = 2 * math.pi / len(menuitems)
	for idx, item in enumerate(menuitems):
		cr.save()
		cr.set_source_rgba(*fontcolor)
		x = center[0] + 50 * math.cos(ang * idx)
		y = center[1] + 50 * math.sin(ang * idx)

		#TODO: FINISH THIS!!!
		text.draw_font_center_rotate(cr, x, y, 'Arial 12', item[0], ang * idx)
		print 'x', x, 'y', y, 'item', item[0]
		cr.restore()

def check_mouse_over(widget, event):
	pass

def click_on_navigator(event):
	pass

def enable(event):
	global center, state
	center = event.x, event.y
	state = True

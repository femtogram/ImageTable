import gtk

import imageloader
import inputmanager
import mainimage

needs_update = False

ownerstr = 'navigator'

min_trans = 10
max_trans = 200

border = 2
nav_height = 200
trans = min_trans
scalar = 1

prevbox = [0, 0]

def draw(cr, width, height):
	global nav_height
	global needs_update
	global trans
	global max_trans
	global scalar

	if imageloader.image:
		try:
			print 'trans', trans
			max_trans = imageloader.imglist[imageloader.index].preview.get_width()

			if inputmanager.owner == ownerstr:
				trans = min(trans + 40, max_trans)
			else:
				trans = max(trans - 40, min_trans)



			cr.save()
			cr.translate(width - trans, 30)
			cr.set_source_rgba(0.4, 0.4, 0.4, 0.8)

			cr.rectangle(-border, -border, max_trans + border, nav_height + 2 * border)
			cr.fill()

			gdkcr = gtk.gdk.CairoContext(cr)
			gdkcr.set_source_pixbuf(imageloader.imglist[imageloader.index].preview, 0, 0)
			gdkcr.paint()

			cr.rectangle(0, 0, max_trans, nav_height)
			cr.clip()

			cr.set_line_width(1.5)

			scalar = float(nav_height) / imageloader.image.get_height()

			print 'width, height', width, height

			x1 = -mainimage.pos_x * scalar / mainimage.zoom
			y1 = -mainimage.pos_y * scalar / mainimage.zoom
			prevbox[0] = width * scalar / mainimage.zoom
			prevbox[1] = height * scalar / mainimage.zoom

			cr.rectangle(x1, y1, *prevbox)

			cr.set_source_rgba(1, 0.3, 0, 0.8)
			cr.stroke()

			#print 'x1, y1, w, h', x1, y1, w, h
			cr.restore()

			print 'trans, max_trans', trans,max_trans

			if trans != max_trans and \
			   trans != min_trans:
				needs_update = True
				print 'proper updating'
			else:
				print 'no more updating'
				needs_update = False
		except (AttributeError):
			pass

def check_mouse_over(event):
	global needs_update

	if event.x > event.window.get_size()[0] - trans - border and \
	   event.y > 30 - border and event.y < 30 + nav_height + border:
	   if trans != max_trans:
	   		needs_update = True
	   return ownerstr
	elif trans != min_trans:
		needs_update = True
	#needs_update = False

def click_on_navigator(event):
	global needs_update

	s = mainimage.zoom / scalar
	print 'clicked on navigator', s

	#mainimage.pos_x = -(event.x - (event.window.get_size()[0] - 200 + max_trans / 2)) * s
	mainimage.pos_x = -(event.x - (event.window.get_size()[0] - trans + prevbox[0] / 2)) * s
	mainimage.pos_y = -(event.y - 30 - prevbox[1] / 2) * s
	needs_update = True
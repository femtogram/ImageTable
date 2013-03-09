import os
import pygtk
pygtk.require('2.0')
import math
import cairo
import gtk
import gobject
from threading import Thread
import sys
import pango
import pangocairo
import urllib
import urllib2
import sched
import time
import shutil

import inputmanager
import imageloader
import parsearguments
import drawables
from drawables import mainbackground
from drawables import backgroundtext
from drawables import mainimage
from drawables import imagemanager


screen = None
window = None

class Screen(gtk.DrawingArea):
	__gsignals__ = { 'expose-event' : 'override' }

	def __init__(self):
		super(Screen, self).__init__()

	def do_expose_event(self, event):
		cr = self.window.cairo_create()

		cr.rectangle(event.area.x, event.area.y,
				event.area.width, event.area.height)
		cr.clip()
		cr.set_antialias(cairo.ANTIALIAS_SUBPIXEL)

		self.draw(cr, *self.window.get_size())

	def start(self):
		self.t = Thread(target=self.redraw)
		self.t.setDaemon(True)
		self.t.start()

	def redraw(self):
		while True:
			for i in drawables.all:
				try:
					i.refresh()
				except (AttributeError, TypeError):
					pass

			for i in drawables.all:
				if i.needs_update:
					print i, 'needs update'
					self.queue_draw()
					i.needs_update = False
					break
			try:
				time.sleep(0.033)
			except AttributeError:
				break

	def draw(self, cr, width, height):
		print 'redrawing'
		for i in drawables.all:
			tmpheight = height
			cr.save()
			if not hasattr(i, 'fullwindow') and imagemanager.should_draw():
				tmpheight = height - imagemanager.winheight
				print 'newheight', height
				cr.rectangle(0, 0, width, tmpheight)
				cr.clip()
			i.draw(cr, width, tmpheight)
			cr.restore()

	def on_delete_event(self, widget, event):
		widget.on_destroy()

	def on_drag_data_received(self, widget, context, x, y, selection, target_type, timestamp):
		if target_type == 80:
			uris = [uri.strip('\r\n\x00') for uri in selection.data.split('\n')]
			#uri = selection.data.strip('\r\n\x00')
			#print 'uri', uri
			path = ''
			if uris[0].startswith('file://'):
				# TODO: Finish this part!
				for uri in uris:
					imageloader.load_from_uri(urllib.unquote(uri.strip('file:')))
				#imageloader.load_from_uri(urllib.unquote(uris[0].strip('file:')))
				# fullurl = quote(fullurl, safe="%/:=&?~#+!$,;'@()*[]")
			elif uris[0].startswith('http'):
				pass


class ImageWindow(gtk.Window):
	def __init__(self):
		super(ImageWindow, self).__init__()
		self.keep_above = False

	def run(self, widget):
		self.screen = widget
		dnd_list = [('text/uri-list', 0, 80)]

		self.drag_dest_set(gtk.DEST_DEFAULT_MOTION |
			gtk.DEST_DEFAULT_HIGHLIGHT | gtk.DEST_DEFAULT_DROP,
			dnd_list, gtk.gdk.ACTION_COPY)

		self.set_title('ImageTable')
		#TODO: set icon here
		self.set_default_size(640, 480) # should this be set in config file?

		
		self.connect('key_press_event', inputmanager.on_key_press)
		self.add_events(gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK)
		self.connect('button-press-event', inputmanager.on_mouse_down)
		self.connect('button-release-event', inputmanager.on_mouse_up)
		self.connect('motion-notify-event', inputmanager.on_mouse_move)
		self.connect('scroll-event', inputmanager.on_mouse_scroll)
		self.connect('delete-event', widget.on_delete_event)
		self.connect('drag_data_received', widget.on_drag_data_received)
		self.connect('check-resize', mainimage.on_window_resize)


		widget.show()
		self.add(widget)
		self.present()

		widget.start()

	def on_toggle_above(self):
		self.keep_above = not self.keep_above
		self.set_keep_above(self.keep_above)
		self.set_title('ImageTable' if not self.keep_above else 'ImageTable (Always on Top)')

	def on_destroy(self):
		self.destroy()
		gtk.main_quit()
		shutil.rmtree(imageloader.directory)

	#def on_key_press(self, widget, event):
	#	keyname = gtk.gdk.keyval_name(event.keyval)
	#	print(keyname, event.keyval)
	#TODO: this part should point to a keyboard shortcut manager

def run(Widget):
	global window

	gtk.gdk.threads_init()

	window = ImageWindow()
	window.run(Widget())

	gtk.main()

if __name__ == '__main__':
	for i in drawables.all:
		print i
	args = parsearguments.args
	run(Screen)


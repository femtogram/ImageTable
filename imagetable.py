#! /usr/bin/env python

'''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Copyright Kota Weaver http://www.kotaweaver.com/ 2012
'''

import os
import pygtk
pygtk.require('2.0')
import math
import cairo
import gtk
import gobject
from threading import Thread
import sys

import sched, time

class Screen(gtk.DrawingArea):
	__gsignals__ = { 'expose-event': 'override' }

	def __init__(self):
		super(Screen, self).__init__()
		self.mouse_down = False
		self.mouse_x = 0
		self.mouse_y = 0
		self.offset_x = 0;
		self.offset_y = 0;
		self.zoom = 1.0;
		self.trans = 10;
		self.loop_draw = True

		self.nav_mouse = False
		self.nav_window_height = 200
		self.nav_preview_width = 1
		self.nav_preview_height = 1

		if len(sys.argv) > 0:
			try:
				self.open_image_from_file(sys.argv[1])
			except:
				'Invalid image file.  Please enter in the URI of the image.'

		#self.s = sched.scheduler(time.time, time.sleep)
		self.t = Thread(target=self.redraw)
		self.t.start()

	def open_image_from_file(self, uri):
		print 'trying to open new image'
		self.img = gtk.gdk.pixbuf_new_from_file(uri)
		self.center_image()

	def redraw(self):
		while self.loop_draw:
			self.queue_draw()
			time.sleep(0.033)
		#self.s.enter(0.033, 1, self.redraw, ())
		#self.s.run()

	def do_expose_event(self, event):
		cr = self.window.cairo_create()

		cr.rectangle(event.area.x, event.area.y,
				event.area.width, event.area.height)
		cr.clip()

		self.draw(cr, *self.window.get_size())
	
	def on_mouse_down(self, widget, event):
		if event.button == 1:
			self.mouse_x = event.x
			self.mouse_y = event.y
			if not self.mouse_down and self.in_nav_window(self.mouse_x, self.mouse_y):
				self.nav_mouse = True
				if hasattr(self, 'img'):
					self.nav_offset(event)
			else:
				self.mouse_down = True
			print 'in nav?',self.in_nav_window(self.mouse_x, self.mouse_y)
			print 'mouse_down?',self.mouse_down

	
	def on_mouse_up(self, widget, event):
		self.mouse_down = False
		self.nav_mouse = False

	def on_scroll(self, widget, event):
		if hasattr(self, 'img'):
			prev_zoom = self.zoom
			self.zoom *= (0.9 if event.direction else 1.1)
			s = self.zoom / prev_zoom
			self.offset_x = event.x - s * (event.x - self.offset_x)
			self.offset_y = event.y - s * (event.y - self.offset_y)

	def nav_offset(self, mouse_event):
		s = (self.zoom * self.img.get_width()) / 200
		print self.nav_preview_width,self.nav_preview_height
		self.offset_x = -(mouse_event.x - (self.window_width - 200 + self.nav_preview_width / 2)) * s
		self.offset_y = -(mouse_event.y - 30 - self.nav_preview_height / 2) * s

		#s = 1 / (200.0 / self.img.get_width()) # / self.zoom
		#self.offset_x = -(mouse_event.x - (self.window_width - 100)) * s
		#self.offset_y = -(mouse_event.y - 30 - self.nav_window_height / 2) * s

	def on_mouse_move(self, widget, event):
		if self.in_nav_window(event.x, event.y) or self.nav_mouse:
			self.trans = 200
		
		else:
			self.trans = 10

		if self.mouse_down and hasattr(self, 'img'):
			delta_x = event.x - self.mouse_x
			delta_y = event.y - self.mouse_y

			self.mouse_x = event.x
			self.mouse_y = event.y

			self.offset_x += delta_x
			self.offset_y += delta_y

		if self.nav_mouse and hasattr(self, 'img'):
			self.nav_offset(event)

	def in_nav_window(self, mx, my):
		return (
					mx >= self.window_width - self.trans and
					mx <= self.window_width and
					my >= 30 and
					my <= self.nav_window_height + 30
			)

	def on_key_press(self, widget, event):
		keyname = gtk.gdk.keyval_name(event.keyval)
		if (
				event.keyval == 80 or event.keyval == 112 or
				event.keyval == 86 or event.keyval == 118
			):
			self.paste_image()

	def paste_image(self):
		print 'paste image'
		clipboard = gtk.clipboard_get(gtk.gdk.SELECTION_CLIPBOARD)
		tmpimg = clipboard.wait_for_image()
		if tmpimg != None:
			print 'has image in clipboard'
			self.img = tmpimg
			self.center_image()

	def center_image(self):
		x_ratio = 1.0 * self.window_width / self.img.get_width()
		y_ratio = 1.0 * self.window_height / self.img.get_height()

		x_diff = self.window_width - y_ratio * self.img.get_width()
		y_diff = self.window_height - x_ratio * self.img.get_height()

		if x_diff < y_diff:
			self.zoom = x_ratio
			self.offset_x = 0
			self.offset_y = (self.window_height - self.zoom * self.img.get_height()) / 2
		else:
			self.zoom = y_ratio
			self.offset_x = (self.window_width - self.zoom * self.img.get_width()) / 2
			self.offset_y = 0
	
	def draw_nav_window(self, cr, width, height):
		border = 2
		cr.save()
		cr.translate(width - self.trans, 30)
		cr.set_source_rgba(0.4, 0.4, 0.4, 0.8)
		if not hasattr(self, 'img'):
			self.nav_window_height = 200
			cr.rectangle(-border, -border, 200 + border, 200 + border)
			cr.fill()
		else:
			scalar = 200.0 / self.img.get_width()
			self.nav_window_height = scalar * self.img.get_height()
			cr.rectangle(-border, -border, 200 + border, self.nav_window_height + 2 * border)
			cr.fill()
			
			cr.save()
			cr.scale(scalar, scalar)
			gdkcr = gtk.gdk.CairoContext(cr)
			tmpimg = self.img
			tmpimg.add_alpha(False, 250, 250, 250)
			gdkcr.set_source_pixbuf(tmpimg, 0, 0)
			gdkcr.paint()
			cr.restore()

			cr.rectangle(0, 0, 200, scalar * self.img.get_height())
			cr.clip()

			cr.set_line_width(1.5)

			x1 = -self.offset_x * scalar / self.zoom
			y1 = -self.offset_y * scalar / self.zoom
			w = self.window_width * scalar / self.zoom
			h = self.window_height * scalar / self.zoom

			self.nav_preview_width = w
			self.nav_preview_height = h

			cr.rectangle(x1, y1, w, h)

			cr.set_source_rgba(1, 0.3, 0, 0.8)
			cr.stroke()
		cr.restore()

	def draw(self, cr, width, height):
		self.window_width = width
		self.window_height = height

		# draw stuff here
		cr.rectangle(0, 0, width,height)
		cr.set_source_rgb(0.1, 0.1, 0.1)
		cr.fill()
		
		if hasattr(self, 'img'):
			cr.save()
			cr.translate(self.offset_x, self.offset_y)
			cr.scale(self.zoom, self.zoom)
			gdkcr = gtk.gdk.CairoContext(cr)
			gdkcr.set_source_pixbuf(self.img, 0, 0)
			gdkcr.paint()
			cr.restore()

		self.draw_nav_window(cr, width, height)

	def on_delete_event(self, event, widget):
		self.loop_draw = False
		self.t.join(0.05)
		gtk.main_quit()

def get_resource_path(rel_path):
	return os.path.abspath(os.path.join(os.path.dirname(__file__), rel_path))

def run(Widget):
	gtk.gdk.threads_init()
	window = gtk.Window()
	window.connect('delete-event', gtk.main_quit)
	widget = Widget()


	window.set_title('ImageTable')
	window.set_icon_from_file(get_resource_path('imagetable_icon_256x256.png'))
	window.set_default_size(640, 480)
	
	window.connect('key_press_event', widget.on_key_press)
	window.add_events(gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK)
	window.connect('button-press-event', widget.on_mouse_down)
	window.connect('button-release-event', widget.on_mouse_up)
	window.connect('motion-notify-event', widget.on_mouse_move)
	window.connect('scroll-event', widget.on_scroll)
	window.connect('delete-event', widget.on_delete_event)

	widget.show()
	window.add(widget)
	window.present()
	gtk.main()

if __name__ == '__main__':
	run(Screen)

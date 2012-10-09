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
import pango
import pangocairo
import urllib2

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

		self.help_on = False
		self.help_circle_x = 3
		self.help_circle_y = -5
		self.help_circle_radius = 20
		self.help_has_mouse = False
		self.help = (('Help', 'h,/,?'),
		('Paste image into viewer', 'p,ctrl-v'),
		('Toggle window on top', 't'),
		('Zoom in', '+,='),
		('Zoom out', '-'))


		self.nav_expand = 0 # -1 means shrinking, 0 means static, 1 means expanding
		self.nav_has_mouse = False # check to see if the mouse is over the nav window
		self.nav_mouse = False # check to see if the mouse click is in nav window
		self.nav_window_height = 200
		self.nav_preview_width = 1
		self.nav_preview_height = 1
		self.color = '0x000000'

		self.window_width, self.window_height = [640, 480]
		
		if len(sys.argv) > 0:
			try:
				self.open_image_from_file(sys.argv[1])
			except:
				'Invalid image file.  Please enter in the URI of the image.'

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

	def load_image_from_url(self, url):
		response = urllib2.urlopen(url)
		loader = gtk.gdk.PixbufLoader()
		loader.write(response.read())
		loader.close()
		self.img = loader.get_pixbuf()
		self.center_image()

	def do_expose_event(self, event):
		cr = self.window.cairo_create()

		cr.rectangle(event.area.x, event.area.y,
				event.area.width, event.area.height)
		cr.clip()

		self.draw(cr, *self.window.get_size())

	def on_mouse_down(self, widget, event):
		# check if left mouse button
		if event.button == 1:
			self.mouse_x = event.x
			self.mouse_y = event.y
			if event.type == gtk.gdk._2BUTTON_PRESS and not self.help_on and not self.help_has_mouse and hasattr(self, 'img'):
				self.center_image()
			if not self.mouse_down and self.in_nav_window(self.mouse_x, self.mouse_y) and not self.help_on:
				self.nav_mouse = True
				if hasattr(self, 'img'):
					self.nav_offset(event)
			else:
				self.mouse_down = True

			if self.help_has_mouse:
				self.help_on = not self.help_on
	
	def on_mouse_up(self, widget, event):
		self.mouse_down = False
		self.nav_mouse = False

	def zoom_in(self):
		self.zoom_direction(False)

	def zoom_out(self):
		self.zoom_direction(True)

	def zoom_direction(self, direction):
		prev_zoom = self.zoom
		self.zoom *= (0.9 if direction else 1.1)
		s = self.zoom / prev_zoom
		self.offset_x = self.mouse_x - s * (self.mouse_x - self.offset_x)
		self.offset_y = self.mouse_y - s * (self.mouse_y - self.offset_y)

	def on_scroll(self, widget, event):
		if hasattr(self, 'img'):
			self.zoom_direction(event.direction)

	def nav_offset(self, mouse_event):
		s = (self.zoom * self.img.get_width()) / 200
		print self.nav_preview_width,self.nav_preview_height
		self.offset_x = -(mouse_event.x - (self.window_width - 200 + self.nav_preview_width / 2)) * s
		self.offset_y = -(mouse_event.y - 30 - self.nav_preview_height / 2) * s

	def on_mouse_move(self, widget, event):
		if self.in_nav_window(event.x, event.y) or self.nav_mouse:
			self.nav_has_mouse = True
		else:
			self.nav_has_mouse = False

		if self.in_help_icon(event.x, event.y):
			self.help_has_mouse = True
		else:
			self.help_has_mouse = False

		if self.mouse_down and hasattr(self, 'img'):
			delta_x = event.x - self.mouse_x
			delta_y = event.y - self.mouse_y

			self.offset_x += delta_x
			self.offset_y += delta_y

		if self.nav_mouse and hasattr(self, 'img'):
			self.nav_offset(event)
		
		self.mouse_x = event.x
		self.mouse_y = event.y

	def on_drag_data_received(self, widget, context, x, y, selection, target_type, timestamp):
		if target_type == 80:
			uri = selection.data.strip('\r\n\x00')
			print 'uri', uri
			path = ''
			if uri.startswith('file://'):
				self.open_image_from_file(uri.strip('file:'))
			elif uri.startswith('http'):
				self.load_image_from_url(uri)

	def in_nav_window(self, mx, my):
		return (
					mx >= self.window_width - self.trans and
					mx <= self.window_width and
					my >= 30 and
					my <= self.nav_window_height + 30
			)

	def in_help_icon(self, mx, my):
		x_diff_sq = mx - self.help_circle_x
		x_diff_sq *= x_diff_sq
		y_diff_sq = my - self.help_circle_y
		y_diff_sq *= y_diff_sq
		rad_sq = self.help_circle_radius * self.help_circle_radius

		return (
					mx >= 0 and
					my >= 0 and
					x_diff_sq + y_diff_sq <= rad_sq
			)

	def on_key_press(self, widget, event):
		keyname = gtk.gdk.keyval_name(event.keyval)
		if (
				event.keyval == ord('/') or event.keyval == ord('?') or
				event.keyval == ord('h') or event.keyval == ord('H')
			):
			self.help_on = not self.help_on
		if (
				event.keyval == 80 or event.keyval == 112 or
				event.keyval == 86 or event.keyval == 118
			):
			self.paste_image()
		if (
				event.keyval == ord('+') or event.keyval == ord('=') or
				event.keyval == 65451
			):
			self.zoom_in()
		if (
				event.keyval == ord('-') or event.keyval == 65453
			):
			self.zoom_out()


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

	def draw_help_icon(self, cr, width, height):
		cr.save()

		if self.help_has_mouse or self.help_on:
			self.help_circle_x = min(self.help_circle_x + 5, 17)
			self.help_circle_y = min(self.help_circle_y + 5, 17)
		else:
			self.help_circle_x = max(self.help_circle_x - 5, 3)
			self.help_circle_y = max(self.help_circle_y - 5, -5)
		cr.translate(self.help_circle_x, self.help_circle_y)
		cr.rotate(0.3)
		cr.set_source_rgba(0.4, 0.4, 0.4, 0.8)
		cr.arc(0, 0, self.help_circle_radius, 0, 2 * math.pi)
		cr.fill()
		cr.save() # for text
		pangocairo_context = pangocairo.CairoContext(cr)
		pangocairo_context.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
		
		layout = pangocairo_context.create_layout()

		layout.set_font_description(pango.FontDescription('Sans 30'))
		layout.set_text('?')
		layout.set_alignment(pango.ALIGN_CENTER)
		cr.set_source_rgba(1, 1, 1, 0.4)
		t_width, t_height = layout.get_pixel_size()
		cr.translate(-t_width / 2, -t_height / 2)
		pangocairo_context.update_layout(layout)
		pangocairo_context.show_layout(layout)

		cr.restore() # for text
		cr.restore()

		if self.help_on:
			self.draw_help_window(cr, width, height)

	def draw_help_text(self, cr, width, height, x_center, y, text_width, y_pos, help_item):
		cr.save()

		pangocairo_context = pangocairo.CairoContext(cr)
		pangocairo_context.set_antialias(cairo.ANTIALIAS_SUBPIXEL)

		layout = pangocairo_context.create_layout()

		layout.set_font_description(pango.FontDescription('Sans 10'))
		layout.set_text(help_item[0])
		cr.translate(x_center - text_width / 2, y + y_pos * 20)
		cr.set_source_rgba(1, 1, 1, 0.8)
		pangocairo_context.update_layout(layout)
		pangocairo_context.show_layout(layout)

		cr.restore()

		cr.save()
		pangocairo_context = pangocairo.CairoContext(cr)
		pangocairo_context.set_antialias(cairo.ANTIALIAS_SUBPIXEL)

		layout = pangocairo_context.create_layout()

		layout.set_font_description(pango.FontDescription('Sans 10'))
		layout.set_text(help_item[1])
		layout.set_alignment(pango.ALIGN_RIGHT)
		cr.translate(x_center + text_width / 2 - layout.get_pixel_size()[0], y + y_pos * 20)
		cr.set_source_rgba(1, 1, 1, 0.8)
		pangocairo_context.update_layout(layout)
		pangocairo_context.show_layout(layout)
		cr.restore()

	def draw_help_window(self, cr, width, height):
		cr.save()
		cr.translate(width / 2, 0)
		cr.set_source_rgba(0.4, 0.4, 0.4, 0.8)
		cr.rectangle(-150, 0, 300, height)
		cr.fill()
		cr.restore()
		for i, val in enumerate(self.help):
			self.draw_help_text(cr, width, height, width / 2, 5, 280, i, val)
	
	def draw_nav_window(self, cr, width, height):
		border = 2
		cr.save()
		cr.translate(width - self.trans, 30)
		cr.set_source_rgba(0.4, 0.4, 0.4, 0.8)
		if self.nav_has_mouse and self.trans < 200:
			self.trans = min(self.trans + 40, 200)
		elif not self.nav_has_mouse and self.trans > 10:
			self.trans = max(self.trans - 40, 10)

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

	def draw_hex_color(self, cr, width, height):
		if hasattr(self, 'img'):
			cr.save()

			cr.translate(0, height - 12)

			cr.save()

			cr.rectangle(0, 0, 56, 12)
			cr.set_source_rgba(0.4, 0.4, 0.4, 0.8)
			cr.fill()

			cr.restore()

			pangocairo_context = pangocairo.CairoContext(cr)
			pangocairo_context.set_antialias(cairo.ANTIALIAS_SUBPIXEL)

			layout = pangocairo_context.create_layout()

			layout.set_font_description(pango.FontDescription('Courier 8'))
			c = self.get_hex_color()
			self.color = c if c else self.color
			layout.set_text(self.color)
			cr.set_source_rgba(1, 1, 1, 0.8)
			pangocairo_context.update_layout(layout)
			pangocairo_context.show_layout(layout)

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

		self.draw_hex_color(cr, width, height)

		self.draw_help_icon(cr, width, height)

	def get_hex_color(self):
	    """Returns an (R, G, B) tuple at the current pointer location."""
	    
	    root_window = gtk.gdk.get_default_root_window()
	    disp = self.get_window().get_screen().get_display()
	    pointer_x, pointer_y = disp.get_pointer()[1:3]

	    if self.get_display().get_window_at_pointer():
	    	pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, 1, 1)
    		pixbuf = pixbuf.get_from_drawable(root_window, root_window.get_colormap(), pointer_x, pointer_y, 0, 0, 1, 1)
	    	tup = tuple(map(ord, pixbuf.get_pixels()[:3]))

	    	res = '0x'
	    	res += ''.join(['{0:0<2}'.format(hex(color)[2:]) for color in tup])
	    	return res
	    return None

	def on_delete_event(self, event, widget):
		self.loop_draw = False
		self.t.join(0.05)
		gtk.main_quit()

class ImWindow(gtk.Window):
	def __init__(self):
		super(ImWindow, self).__init__()
		self.keep_above = False

	def on_toggle_above(self):
		self.keep_above = not self.keep_above
		self.set_keep_above(self.keep_above)
		self.set_title('ImageTable' if not self.keep_above else 'ImageTable (Always on Top)')

	def on_key_press(self, widget, event):
		keyname = gtk.gdk.keyval_name(event.keyval)
		print(keyname, event.keyval)
		if event.keyval == ord('t') or event.keyval == ord('T'):
			self.on_toggle_above()
		else:
			self.get_children()[0].on_key_press(widget, event)

def get_resource_path(rel_path):
	return os.path.abspath(os.path.join(os.path.dirname(__file__), rel_path))

def run(Widget):
	dnd_list = [ ( 'text/uri-list', 0, 80) ]

	gtk.gdk.threads_init()
	window = ImWindow()
	window.connect('delete-event', gtk.main_quit)
	widget = Widget()

	window.drag_dest_set(gtk.DEST_DEFAULT_MOTION | 
				gtk.DEST_DEFAULT_HIGHLIGHT | gtk.DEST_DEFAULT_DROP,
				dnd_list, gtk.gdk.ACTION_COPY)

	window.set_title('ImageTable')
	window.set_icon_from_file(get_resource_path('imagetable_icon_256x256.png'))
	window.set_default_size(640, 480)
	
	window.connect('key_press_event', window.on_key_press)
	window.add_events(gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK)
	window.connect('button-press-event', widget.on_mouse_down)
	window.connect('button-release-event', widget.on_mouse_up)
	window.connect('motion-notify-event', widget.on_mouse_move)
	window.connect('scroll-event', widget.on_scroll)
	window.connect('delete-event', widget.on_delete_event)
	window.connect('drag_data_received', widget.on_drag_data_received)

	widget.show()
	window.add(widget)
	window.present()
	gtk.main()

if __name__ == '__main__':
	run(Screen)

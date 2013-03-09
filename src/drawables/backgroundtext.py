import os
import gtk
import pangocairo
import cairo
import pango

import imageloader
import utilities
from utilities import text

needs_update = False
print os.path.dirname(os.path.realpath(imageloader.__file__))
print type(os.path.dirname(os.path.realpath(imageloader.__file__)))
LOGO = gtk.gdk.pixbuf_new_from_file(os.path.join(os.path.dirname(os.path.realpath(imageloader.__file__)), 'logo_white.png'))

BACKGROUNDTEXT = \
"""ImageTable is a new take on the classic image viewer.

Drag and drop an image file in here.

You can also paste an image or url of an image in the clipboard with 'v' or 'p'.

Use 't' to keep the window always on top.

The 'c' key can be used to display the hex color under the cursor on the image."""

def draw(cr, width, height):
	global needs_update

	if imageloader.image is None:
		draw_background(cr, width, height)

	needs_update = False

def draw_background(cr, width, height):
	gdkcr = gtk.gdk.CairoContext(cr)
	gdkcr.set_source_pixbuf(LOGO, (width - LOGO.get_width()) / 2,  40)
	gdkcr.paint()

	cr.set_source_rgba(1, 1, 1, 1)
	text.draw_font_left_wrap(cr, width / 2 - 175, 150, 'Arial 12', BACKGROUNDTEXT, 350)

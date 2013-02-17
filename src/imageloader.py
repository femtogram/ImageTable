import urllib2
import pygtk
import gtk
from threading import Thread
import tempfile

from drawables import mainimage

needs_update = False

image = None

index = 0
imglist = list()
directory = tempfile.mkdtemp(prefix='imgtable_')

def draw(cr, width, height):
	'''
	shouldn't drwa anything.  this is used to be able to specify
	redrawing the window from within this module.
	'''
	pass

def next_img():
	global image
	global index
	global needs_update

	if index < len(imglist) - 1:
		index += 1
		imglist[index - 1].img = None
		image = gtk.gdk.pixbuf_new_from_file(imglist[index].uri).apply_embedded_orientation()
		needs_update = True

def prev_img():
	global image
	global index
	global needs_update

	if index > 0:
		index -= 1
		imglist[index + 1].img = None
		image = gtk.gdk.pixbuf_new_from_file(imglist[index].uri).apply_embedded_orientation()
		needs_update = True

def load_from_url(url):
	pass

def load_from_uri(uri):
	global image

	def _load(cont, uri):
		img = gtk.gdk.pixbuf_new_from_file(uri).apply_embedded_orientation()
		cont.generate_preview(img)

	cont = ImageContainer(uri=uri)
	
	t = Thread(target = _load, args=(cont, uri))
	t.start()

def load_from_clipboard():
	global image
	global needs_update
	print 'paste image'
	clipboard = gtk.clipboard_get(gtk.gdk.SELECTION_CLIPBOARD)
	tmpimg = clipboard.wait_for_image()
	if tmpimg != None:
		image = tmpimg
		mainimage.center_image()
		needs_update = True
		cont = ImageContainer()
		cont.store_image(image)
		cont.generate_preview(image)

class ImageContainer(object):
	uri = None
	preview = None
	done_saving = False

	def __init__(self, uri=False):
		global directory

		if uri:
			self.uri = uri
		else:
			self.uri = tempfile.mkstemp(dir=directory, suffix='.png')[1]
		self.index = len(imglist)
		imglist.append(self)

	def store_image(self, img):
		def _store():
			img.save(self.uri, 'png')
			self.done_saving = True
			print 'done storing'
		self.generate_preview(img)
		t = Thread(target=_store)
		t.start()
	
	def set_image(self):
		global image
		global needs_update
		global index
		
		print 'cont index:', self.index
		image = gtk.gdk.pixbuf_new_from_file(self.uri).apply_embedded_orientation()
		index = self.index
		print 'global index:', index
		needs_update = True

	def generate_preview(self, img):
		def scale():
			global needs_update

			if img.get_height() > img.get_width():
				self.preview = img.scale_simple(200, int(200.0 / img.get_width() * img.get_height()), gtk.gdk.INTERP_HYPER)
			else:
				self.preview = img.scale_simple(int (200.0 / img.get_height() * img.get_width()), 200, gtk.gdk.INTERP_HYPER)
			self.preview.add_alpha(False, 250, 250, 250)
			needs_update = True
		t = Thread(target=scale)
		t.start()

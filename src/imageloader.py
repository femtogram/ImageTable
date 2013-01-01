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
	shouldn't draw anything.  this is used to be able to specify
	redrawing the window from within this module.
	'''
	pass

def next_img():
	global image
	global index
	global imglist
	global needs_update

	if index < len(imglist) - 1:
		print 'next image'
		index += 1
		imglist[index - 1].img = None
		image = gtk.gdk.pixbuf_new_from_file(imglist[index].uri).apply_embedded_orientation()
		needs_update = True

def prev_img():
	global image
	global index
	global imglist
	global needs_update

	if index > 0:
		print 'previous image'
		index -= 1
		imglist[index + 1].img = None
		image = gtk.gdk.pixbuf_new_from_file(imglist[index].uri).apply_embedded_orientation()
		needs_update = True

def load_from_url(url):
	pass

def load_from_uri(uri):
	global image

	def _load():
		global image
		global needs_update

		image = gtk.gdk.pixbuf_new_from_file(uri).apply_embedded_orientation()
		mainimage.center_image()
		needs_update = True
		_load_image(image, uri)
	t = Thread(target=_load)
	t.daemon = True
	t.start()

def load_from_clipboard():
	global image
	global needs_update
	print 'paste image'
	clipboard = gtk.clipboard_get(gtk.gdk.SELECTION_CLIPBOARD)
	tmpimg = clipboard.wait_for_image()
	if tmpimg != None:
		print 'has image in clipboard'

		image = tmpimg
		mainimage.center_image()
		needs_update = True
		_load_image(image, None)
	'''
	def paste_image(self):
		print 'paste image'
		clipboard = gtk.clipboard_get(gtk.gdk.SELECTION_CLIPBOARD)
		tmpimg = clipboard.wait_for_image()
		if tmpimg != None:
			print 'has image in clipboard'
			self.img = tmpimg
			self.center_image()
	'''

def _load_image(img, uri):
	global index
	global imglist
	global needs_update

	cont = ImageContainer()
	imglist.append(cont)
	index = len(imglist) - 1
	t = Thread(target=cont.store_image, args=(img,uri))
	#cont.store_image(img)
	t.start()

	print 'INDEX:::::: ', index

class ImageContainer(object):
	uri = None
	preview = None
	done_saving = False

	def store_image(self, img, uri=False):
		global directory

		def store():
			img.save(self.uri, 'png')
			self.done_saving = True
			print 'done storing'

		self.generate_preview(img)
		#self.store_image(img)

		if uri:
			self.uri = uri
		else:
			self.uri = tempfile.mkstemp(dir=directory, suffix='.png')[1]
			#t = Thread(target=store)
			#t.start()
			store()

	def generate_preview(self, img):
		def scale():
			global needs_update

			if img.get_height() > img.get_width():
				self.preview = img.scale_simple(200, int (200.0 / img.get_width() * img.get_height()), gtk.gdk.INTERP_HYPER)
			else:
				self.preview = img.scale_simple(int (200.0 / img.get_height() * img.get_width()), 200, gtk.gdk.INTERP_HYPER)
			self.preview.add_alpha(False, 250, 250, 250)
			needs_update = True
		t = Thread(target=scale)
		t.start()

'''
class FileManager(object):
	def __init__(self):
		self.dir = tempfile.mkdtemp()

	def make_new_file(self, ext):
		return tempfile.mkstemp(dir=self.dir)

class URILoader(threading.Thread):
	def __init__(self, uri):
		self.uri = uri
		self.img = None

	def run(self):
		self.img = gtk.gdk.pixbuf_new_from_file(self.uri)

class URLLoader(threading.Thread):
	def __init__(self, url):
		self.url = url
		self.img = None

	def run(self):
		response = urllib2.urlopen(url)
		loader = gtk.gdk.PixbufLoader()
		loader.write(response.read())
		loader.close()
		self.img = loader.get_pixbuf()

class StoreImageFromURL(threading.Thread):
	def __init__(self, url):
		self.loader = URLLoader(url)

	def run(self):
		self.loader.run()
		self.loader.img

class StoreImage(threading.Thread):
	def __init__(self, url):
		self.uri = None
		self.url = url

	def get_uri(self):
		return self.uri

	def set_uri(self, uri):
		self.uri = uri

	#def run(self):
'''
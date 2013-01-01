import thread

class Image(object):
	def __init__(self):
		self.img = None
		self.preview = None
		self.uri = None
		self.loaded = False

	def load_from_uri(self, uri):
		thread.start_new_thread(self._load_from_uri, uri)

	def _load_from_uri(self, uri):

		self.img = gtk.gdk.pixbuf_new_from_file(uri)
		self.uri = uri

	def load_from_url(self, url):
		response = urllib2.urlopen(url)
		loader = gtk.gdk.PixbufLoader()
		loader.write(response.read())
		loader.close()

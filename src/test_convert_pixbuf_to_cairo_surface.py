import pygtk
import gtk
import urllib2
import cairo

response = urllib2.urlopen('http://24.media.tumblr.com/tumblr_l7rufjOIkR1qa2q59o1_500.png')
loader = gtk.gdk.PixbufLoader()
loader.write(response.read())
loader.close()
img = loader.get_pixbuf()


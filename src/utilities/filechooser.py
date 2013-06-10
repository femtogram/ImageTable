import pygtk
pygtk.require('2.0')
import gtk
import imageloader

def open_file_dialog():
	images = _file_dialog()
	for i in images:
		imageloader.load_from_uri(i)

def _file_dialog():
	dialog = gtk.FileChooserDialog('Open',
					None,
					gtk.FILE_CHOOSER_ACTION_OPEN,
					(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
	dialog.set_default_response(gtk.RESPONSE_OK)

	filter = gtk.FileFilter()
	filter.set_name("All files")
	filter.add_pattern("*")
	dialog.add_filter(filter)

	filter = gtk.FileFilter()
	filter.set_name('Images')
	filter.add_mime_type('image/png')
	filter.add_mime_type('image/jpeg')
	filter.add_mime_type('image/gif')
	filter.add_pattern('*.png')
	filter.add_pattern('*.jpg')
	filter.add_pattern('*.jpeg')
	filter.add_pattern('*.tif')
	dialog.add_filter(filter)

	dialog.set_select_multiple(True)

	response = dialog.run()
	ret_val = None
	if response == gtk.RESPONSE_OK:
		ret_val = dialog.get_filenames()
		print ret_val, 'selected'
	elif response == gtk.RESPONSE_CANCEL:
		print 'Closed, no files selected'
	dialog.destroy()
	return ret_val

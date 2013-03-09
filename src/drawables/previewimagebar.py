
class PreviewImageBar(object):
	def __init__(self, imglist, index=0, winheight=200):
		self.winheight = winheight
		self.imlist = list()
		self.generate_image_nodes(imglist)
		self.index = index

	def generate_image_nodes(self, imglist):
		for img in imglist:
			self.imlist.append(ImageNode(img))

	def draw(cr, width, height):
		pass

class ImageNode(object):
	def __init__(self, preview_image):
		self.width = width
		self.height = height
		self.pixbuf = preview_image

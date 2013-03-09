import math
import imageloader

fullwindow = True
needs_update = False
winheight = 200
line_width = 5
divider_pos = 0
start_index = 0
preview_img_pos = list()
mouse_over_index = 0

ownerstr = ('divider', 'manager', 'manager-background')

class PreviewImagePositions(object):
	def __init__(self, width, height, index):
		self.width = width
		self.height = height
		self.index = index

def should_draw():
	return len(imageloader.imglist) > 1

def draw_nib(cr, x, y):
	cr.save()
	cr.set_source_rgb(0.6, 0.6, 0.6)
	cr.arc(x, y, 1, 0, 2 * math.pi)
	cr.fill()
	cr.restore()

def draw_background_color(cr, y, width):
	cr.save()
	cr.set_source_rgb(0.13, 0.13, 0.13)
	cr.rectangle(0, y, width, winheight)
	cr.fill()
	cr.restore()

def draw_divider_line(cr, y, width):
	cr.save()
	cr.set_source_rgb(0.2, 0.2, 0.2)
	cr.set_line_width(line_width)
	cr.move_to(0, y)
	cr.line_to(width, y)
	cr.stroke()
	cr.restore()

def draw_image_icons(cr, width, height):
	global preview_img_pos

	tmpheight = 0
	if winheight < 60:
		tmpheight = 60
	elif winheight > 200:
		tmpheight = 200
	else:
		tmpheight = winheight
	cr.save()
	preview_img_pos = list()
	sum_width = imageloader.imglist[imageloader.index].get_preview_width(tmpheight - 20)
	preview_img_pos.append(PreviewImagePositions(sum_width, tmpheight - 20, imageloader.index))
	for i in range(1, len(imageloader.imglist)):
		if imageloader.index - i >= 0:
			tmp_width = imageloader.imglist[imageloader.index - i].get_preview_width(tmpheight - 20)
			preview_img_pos.insert(0, PreviewImagePositions(tmp_width, tmpheight - 20, imageloader.index - i))
			sum_width += tmp_width + 10
			if sum_width > width:
				break
		if imageloader.index + i < len(imageloader.imglist):
			tmp_width = imageloader.imglist[imageloader.index + i].get_preview_width(tmpheight - 20)
			preview_img_pos.append(PreviewImagePositions(tmp_width, tmpheight - 20, imageloader.index + i))
			sum_width += tmp_width + 10
			if sum_width > width:
				break
	pos = 10
	for idx, var in enumerate(preview_img_pos):
		imageloader.imglist[var.index].draw_preview(cr, width, height, pos, divider_pos + 10, var.width, var.height)
		pos += var.width + 10

	'''
	for i in range(start_index, len(imageloader.imglist)):
		#enumerate(imageloader.imglist):
		if pos > width - 2:
			break
		tmpwidth = imageloader.imglist[i].get_preview_width(tmpheight - 20)
		print 'index', i, 'tmpwidth', tmpwidth
		print 'pos', pos, 'divider_pos', divider_pos
		imageloader.imglist[i].draw_preview(cr, width, height, pos, divider_pos + 10, tmpwidth, tmpheight - 20) # add feature to highlight the one that is active
		pos += tmpwidth + 10
	'''
	cr.restore()

def draw(cr, width, height):
	if not should_draw():
		return
	global divider_pos
	divider_pos = height - winheight
	y_pos = divider_pos + line_width / 2
	draw_background_color(cr, y_pos, width)
	draw_divider_line(cr, y_pos, width)

	draw_image_icons(cr, width, height)
	for i in range(0, 7):
		draw_nib(cr, width / 2 - 15 + i * 5, y_pos)

def check_mouse_over_divider(event):
	return event.y > divider_pos and event.y < divider_pos + line_width

def update_winheight(widget, event):
	global winheight
	global needs_update
	tmpwinheight = widget.get_allocation().height - event.y
	if tmpwinheight < line_width:
		winheight = line_width
	elif tmpwinheight > widget.get_allocation().height - line_width / 2:
		winheight = widget.get_allocation().height - line_width / 2
	else:
		winheight = tmpwinheight
	needs_update = True
	

def check_mouse_over(widget, event):
	global needs_update
	global mouse_over_index

	isdrawn = should_draw()
	if isdrawn and check_mouse_over_divider(event):
		return ownerstr[0]
	if isdrawn and event.y > widget.get_allocation().height - winheight:
		x_pos = 10
		if event.y > widget.get_allocation().height - winheight + 10 and \
			event.y < widget.get_allocation().height - 10:
			for img in preview_img_pos:
				if event.x > x_pos and event.x < x_pos + img.width:
					mouse_over_index = img.index
					return ownerstr[1]
				x_pos += img.width + 10
		return ownerstr[2]

def on_click_preview(widget, event):
	imageloader.load_img_at_index(mouse_over_index)

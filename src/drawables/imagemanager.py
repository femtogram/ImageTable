import math
import imageloader

fullwindow = True
needs_update = False
winheight = 200
line_width = 5
divider_pos = 0
start_index = 0
positions = list()
mouse_over_index = 0

ownerstr = ('divider', 'manager', 'manager-background')

class PreviewImagePositions(object):
	def __init__(self, index, x, width):
		self.x = x
		self.width = width
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
	global positions

	tmpheight = 0
	if winheight < 60:
		tmpheight = 60
	elif winheight > 200:
		tmpheight = 200
	else:
		tmpheight = winheight
	
	positions = list()

	def image_positions(position, width, side, idx):
		posidx = 0
		cont = True
		print 'current index:', idx
		preview_width = imageloader.imglist[idx].get_preview_width(tmpheight - 20)

		next_idx = 0
		if side == 'left':
			position -= preview_width + 10
			if position <= 10:
				cont = False
			else:
				next_idx = idx - 1
		elif side == 'right':
			posidx = len(positions)
			position += positions[-1].width + 10
			if position >= width - preview_width + 10:
				cont = False
			else:
				next_idx = idx + 1
		positions.insert(posidx, PreviewImagePositions(idx, position, preview_width))
		if cont and next_idx >= 0 and next_idx < len(imageloader.imglist):
			image_positions(position, width, side, next_idx)

	position = (width - imageloader.imglist[imageloader.index].get_preview_width(tmpheight - 20)) / 2
	positions.append(PreviewImagePositions(imageloader.index, position, imageloader.imglist[imageloader.index].get_preview_width(tmpheight - 20)))
	print imageloader.index
	if imageloader.index != 0:
		image_positions(position, width, 'left', imageloader.index - 1)
	if imageloader.index != len(imageloader.imglist) - 1:
		image_positions(position, width, 'right', imageloader.index + 1)
	for idx, var in enumerate(positions):
		imageloader.imglist[var.index].draw_preview(cr, width, height, var.x, divider_pos + 10, var.width, tmpheight - 20)

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
			for img in positions:
				if event.x > img.x and event.x < img.x + img.width:
					mouse_over_index = img.index
					return ownerstr[1]
		return ownerstr[2]

def on_click_preview(widget, event):
	imageloader.load_img_at_index(mouse_over_index)

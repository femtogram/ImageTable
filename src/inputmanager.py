import gtk

import imageloader
from drawables import mainimage
from drawables import helpicon
from drawables import navigator
from drawables import hexcolor
from drawables import imagemanager
import drawables

down = False

'''
Possible values for owner:
	"help" <- help icon is locking
	"mainimage" <- main image is locking
	"navigator" <- navigation window is locking
'''
owner = None

mouse_prev = [0, 0]


'''

'''
class MouseManager(object):
	def __init__(self):
		pass

'''
	esc quits program
	t/T toggle up and down
	p/P/v/V pastes the image
	h/H/?/'/' opens help
	+ is zoom in
	- is zoom out
'''
def on_key_press(widget, event):
	keyname = gtk.gdk.keyval_name(event.keyval)
	print 'KEYPRESS', keyname

	if keyname == 'Escape':
		widget.on_destroy()
	if keyname.lower() == 't':
		widget.on_toggle_above()
	if keyname.lower() == 'c':
		hexcolor.sethexcolor()
	if keyname.lower() == 'p' or keyname.lower() == 'v':
		imageloader.load_from_clipboard()
	if event.keyval == gtk.keysyms.Right:
		imageloader.next_img()
		print 'blahuuh'
	if event.keyval == gtk.keysyms.Left:
		imageloader.prev_img()
	if keyname == 'plus' or keyname == 'equal' or keyname == 'KP_Add':
		mainimage.zoom_in()
	if keyname == 'minus' or keyname == 'KP_Subtract':
		mainimage.zoom_out()
	if keyname.lower() == 'h' or event.keyval == gtk.keysyms.slash or \
	   event.keyval == gtk.keysyms.question:
		helpicon.help_on = not helpicon.help_on
		helpicon.needs_update = True
		# fix bug where help icon doesn't close after hitting key using mouse.
	#TODO: keyboard input handling

def on_mouse_down(widget, event):
	global down
	global mouse_prev
	global owner

	print 'DOWN',event.button
	down = True

	mouse_prev = [event.x, event.y]
	#owner = 'mainimage'

	if owner == helpicon.ownerstr and event.button == 1:
		helpicon.help_on = not helpicon.help_on
		helpicon.needs_update = True
	
	if owner == imagemanager.ownerstr[1] and event.button == 1:
		imagemanager.on_click_preview(widget, event)

	print 'does event type match up with gtkgdk2button?', event.type == gtk.gdk._2BUTTON_PRESS
	print 'the current owner is', owner
	if owner == mainimage.ownerstr and event.type == gtk.gdk._2BUTTON_PRESS:
		'center that image'
		mainimage.center_image()

	if owner == navigator.ownerstr and down:
		navigator.click_on_navigator(event)
	elif owner == imagemanager.ownerstr[0] and down:
		imagemanager.update_winheight(widget, event)
	#TODO: mouse down event

def on_mouse_up(widget, event):
	global down
	global owner

	down = False
	#owner = 

	print 'UP',event.button
	down = False
	#TODO: mouse up event

def on_mouse_scroll(widget, event):
	print event.direction
	print event.x, event.y
	print type(mainimage)
	mainimage.zoom_direction(event.direction, event.x, event.y)
	#TODO: mouse scroll event

def on_mouse_move(widget, event):
	global mouse_prev

	print 'mouse pos: {', event.x, ', ', event.y, '}'

	if not down:
		check_mouse_over(widget, event)

	if owner == 'mainimage' and down:
		mainimage.pos_x += event.x - mouse_prev[0]
		mainimage.pos_y += event.y - mouse_prev[1]
		mainimage.needs_update = True

	if owner == navigator.ownerstr and down:
		navigator.click_on_navigator(event)
	
	if owner == imagemanager.ownerstr[0] and down:
		imagemanager.update_winheight(widget, event)

	mouse_prev = [event.x, event.y]
	
	#TODO: mouse move event

def check_mouse_over(widget, event):
	global owner

	for i in reversed(drawables.all):
		try:
			tmp = i.check_mouse_over(widget, event)
			if tmp:
				owner = tmp
				break
		except (AttributeError, TypeError):
			continue


'''
wikipedia's ducktyping ex:

try:
    mallard.quack()
except (AttributeError, TypeError):
    print("mallard can't quack()")
'''

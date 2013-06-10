import mainbackground
import backgroundtext
import mainimage
import helpicon
import navigator
import helpwindow
import hexcolor
import imagemanager
import rightclickmenu

all = list()

'''
	Note the significance of the ordering for the list 'all'.
	The back of the list is the top of the stack.
'''
all.append(mainbackground)
all.append(backgroundtext)
all.append(mainimage)
all.append(navigator)
all.append(helpicon)
all.append(helpwindow)
all.append(hexcolor)
all.append(imagemanager)
#all.append(rightclickmenu)

import argparse
import imageloader

from multiprocessing import Pool
from threading import Thread

parser = argparse.ArgumentParser()
parser.add_argument("openfile", nargs='*')

args = parser.parse_args()

_pool = list()

'''
if args.openfile:
	for i in args.openfile:
		_pool.append(Thread(target=lambda: imageloader.load_from_uri(i)))
		_pool[-1].start()
'''

if args.openfile:
	for i in args.openfile:
		imageloader.load_from_uri(i)
	imageloader.imglist[-1].set_image()

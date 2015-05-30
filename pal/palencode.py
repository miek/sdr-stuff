# Copyright 2014-2015 Mike Walters
#
# Heavily inspired by Clayton Smith's NTSC example:
#   https://github.com/argilo/sdr-examples/tree/master/ntsc

from PIL import Image
import struct
import sys

PIXEL_CLOCK = 13.5e6
LINE_TIME = 64e-6
SAMPLES_PER_LINE = PIXEL_CLOCK * LINE_TIME
SAMP_RATE = SAMPLES_PER_LINE * 50 * 625 / 2

LINE_COUNT = 625
HORIZ_RES = int(52e-6 * PIXEL_CLOCK)

SYNC_LEVEL = 0.0
BLANK_LEVEL = 0.3
BLACK_LEVEL = 0.3
WHITE_LEVEL = 1.0

HORIZ_SYNC_TIME = 4.7e-6
FRONT_PORCH_TIME = 1.65e-6
BACK_PORCH_TIME = 5.7e-6

def t2s(time):
  return int(round(time * PIXEL_CLOCK))

def gen_front_porch():
	return [BLANK_LEVEL] * t2s(FRONT_PORCH_TIME)

def gen_back_porch():
	return [BLANK_LEVEL] * t2s(BACK_PORCH_TIME)

def gen_horiz_sync():
	return [SYNC_LEVEL] * t2s(HORIZ_SYNC_TIME)

def gen_short_sync():
	return ([SYNC_LEVEL] * t2s(2.35e-6)) + ([BLANK_LEVEL] * t2s((LINE_TIME / 2) - 2.35e-6))

def gen_long_sync():
	return ([SYNC_LEVEL] * t2s((LINE_TIME / 2) - 4.7e-6)) + ([BLANK_LEVEL] * t2s(4.7e-6))

def gen_pixel(r, g, b):
	r /= 255.0
	g /= 255.0
	b /= 255.0
	return 0.3 * r + 0.59 * g + 0.11 * b

def gen_video(im, line_num):
	ret = []
	for x in range(702):
		pixel = im[x / 702.0 * 760, line_num]
		lum = gen_pixel(pixel[0], pixel[1], pixel[2])
		ret += [BLACK_LEVEL + (WHITE_LEVEL - BLACK_LEVEL) * lum]
	return ret


def gen_blank_line():
	return gen_horiz_sync() + gen_back_porch() + [BLACK_LEVEL] * 702 + gen_front_porch()

def gen_line(im, line_num):
	return gen_horiz_sync() + gen_back_porch() + gen_video(im, line_num) + gen_front_porch()

def gen_frame(im):
	frame = []

	# Field 1
	frame += gen_long_sync() * 5 + gen_short_sync() * 5
	for i in range(17):
		frame += gen_blank_line()
	for i in range(0, 576, 2):
		frame += gen_line(im, i)
	frame += gen_short_sync() * 5

	# Field 2
	frame += gen_long_sync() * 5 + gen_short_sync() * 5 + [BLACK_LEVEL] * (t2s(LINE_TIME / 2))
	for i in range(17):
		frame += gen_blank_line()
	for i in range(1, 576, 2):
		frame += gen_line(im, i)
	frame += gen_horiz_sync() + gen_back_porch() + [BLACK_LEVEL] * (t2s(LINE_TIME/2 - HORIZ_SYNC_TIME - BACK_PORCH_TIME)) + gen_short_sync() * 5

	return frame

def main():
	if len(sys.argv) < 2:
		print "Usage: %s <input_filename> [output_filename]" % sys.argv[0]
		return

	input_filename = sys.argv[1]
	output_filename = sys.argv[2] if len(sys.argv) > 2 else 'output.bin'

	f = open(output_filename, 'w')
	frame = gen_frame(Image.open(input_filename).load())
	f.write(struct.pack('%sf' % len(frame), *frame))
	f.close()

if __name__ == "__main__":
	main()

#!/usr/bin/python

from PIL import Image

import argparse
import os

parser = argparse.ArgumentParser(description='Convert texture to binary.')
parser.add_argument(
	'-i', '--input',
	metavar='input_filename',
	type=str,
	nargs=1,
	required=True,
	help='Filename of the image to convert.',
)
parser.add_argument(
	'-o', '--output',
	metavar='output_filename',
	type=str,
	nargs=1,
	required=True,
	help='Filename for the output image.',
)
parser.add_argument(
	'--tile-width',
	metavar='tile_width',
	type=str,
	nargs=1,
	required=False,
)
parser.add_argument(
	'--tile-height',
	metavar='tile_height',
	type=str,
	nargs=1,
	required=False,
)
parser.add_argument(
	'-f', '--flip-y',
	dest='flip_y',
	action='store_true',
)
parser.add_argument(
	'-n', '--name',
	metavar='name',
	type=str,
	nargs=1,
	required=True,
	help='Pascal_Case name for header file.',
)
parser.set_defaults(flip_y=False)

args = parser.parse_args()
in_filename = args.input[0]
out_filename = args.output[0]
flip_y = args.flip_y
name = args.name[0]
tile_width = args.tile_width[0]
tile_height = args.tile_height[0]

img = Image.open(in_filename, 'r')

width, height = img.width, img.height

# TODO -- options for different colour spaces - currently just doing 1 bit textures

image_data = []
mouse_map_data = []
for y in range(height):
	if flip_y:
		y = height - y - 1
	for x in range(width):
		r, g, b, a = img.getpixel((x, y))
		val = '0x{:02X}{:02X}{:02X}{:02X}'.format(a, b, g, r)
		image_data.append(val)
		mouse_map_data.append(1 if a else 0)

mouse_map_data.extend([0] * ((- (width * height)) % 8))
new_data = []
for n in range(0, len(mouse_map_data), 8):
	this_byte = mouse_map_data[n:n+8]
	acc = 0
	for i in range(8):
		acc += this_byte[i] * (1 << i)
	new_data.append(acc)
mouse_map_data = ['0x{:02X}'.format(s) for s in new_data]

output_template = '''
#ifndef SPRITE_SHEET_{name_upper}_H
#define SPRITE_SHEET_{name_upper}_H

#include "jfg/prelude.h"
#include "sprite_sheet.h"

extern Sprite_Sheet_Data SPRITE_SHEET_{name_upper};

#ifndef JFG_HEADER_ONLY
u32 SPRITE_SHEET_{name_upper}_IMAGE_DATA[] = {{
	{image_data}
}};

u8 SPRITE_SHEET_{name_upper}_MOUSE_MAP_DATA[] = {{
	{mouse_map_data}
}};

Sprite_Sheet_Data SPRITE_SHEET_{name_upper} = {{
	{{ {width}, {height} }},
	{{ {sprite_width}, {sprite_height} }},
	SPRITE_SHEET_{name_upper}_IMAGE_DATA,
	SPRITE_SHEET_{name_upper}_MOUSE_MAP_DATA

}};
#endif

#endif
'''.strip()

image_data = ',\n\t'.join([', '.join(image_data[n:n+8]) for n in range(0, len(image_data), 8)])
mouse_map_data = ',\n\t'.join([', '.join(mouse_map_data[n:n+12]) for n in range(0, len(mouse_map_data), 12)])

output = output_template.format(
	name_upper=name.upper(),
	name_pascal=name,
	data_length=width * height,
	width=width,
	height=height,
	image_data=image_data,
	mouse_map_data=mouse_map_data,
	sprite_width=tile_width,
	sprite_height=tile_height,
)

with open(out_filename, 'w') as outfile:
	outfile.write(output)

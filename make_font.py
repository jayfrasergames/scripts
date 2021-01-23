#!/usr/bin/python3

# from fontTools.ttLib import TTFont
import freetype
from PIL import Image

filename = 'Werbedeutsch Heavy.ttf'
all_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz01234567890'
draw_grid = False

font = freetype.Face(filename)
# font.set_encoding(freetype.FT_ENCODING_UNICODE)

width, height = 32, 32
output = Image.new('L', (width * 16, height * 16))

font.set_pixel_sizes(width, height)

if draw_grid:
	for y in range(16):
		for x in range(16):
			color = 0 if (x + y) % 2 else 64
			x_offset, y_offset = x * width, y * height
			for j in range(height):
				for i in range(width):
					output.putpixel((x_offset + i, y_offset + j), color)

baseline_offset = 0
cur_width, cur_height = width, height
while 1:
	font.set_pixel_sizes(cur_width, cur_height)
	max_height = 0
	for char in all_chars:
		font.load_char(char)
		glyph_height = font.glyph.bitmap.rows
		baseline_offset = max(baseline_offset, glyph_height - font.glyph.bitmap_top)
		max_height = max(max_height, font.glyph.bitmap_top)

	# two possibilities for choosing size
	# either try and get baseline offset to be equal to a border at the top and center
	# or try and get baseline offset + max height to be as close to the requested size as possible
	print(baseline_offset, baseline_offset + max_height)
	if baseline_offset + max_height <= height:
		baseline_offset += (height - (baseline_offset + max_height)) // 2
		break

	cur_height -= 1
	cur_width = round(cur_height * (width / height))
	print(f'trying size: {cur_width}x{cur_height}')


for index in range(256):
	# char = chr(index)
	char = index.to_bytes(1, 'big').decode('cp437')
	x, y = index % 16, index // 16
	left, top = x * width, y * height
	font.load_char(char)
	b = font.glyph.bitmap
	left += (width - b.width) // 2
	if char in all_chars:
		top += height - font.glyph.bitmap_top - baseline_offset
	else:
		top += (height - b.rows) // 2
	if b.rows > height or b.width > width:
		continue
	for j in range(b.rows):
		for i in range(b.width):
			output.putpixel((left + i, top + j), b.buffer[j * b.width + i])


output.save(f'charset_{width}x{height}.png')

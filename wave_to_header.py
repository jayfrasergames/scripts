#!/usr/bin/python3

import argparse
import os
import wave

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
	'-n', '--name',
	metavar='name',
	type=str,
	nargs=1,
	required=True,
	help='Pascal_Case name for header file.',
)

args = parser.parse_args()
in_filename = args.input[0]
out_filename = args.output[0]
name = args.name[0]

sound = wave.open(in_filename, 'rb')

wave_header_template = '''
#ifndef {name_upper}_H
#define {name_upper}_H

#include "jfg/prelude.h"

struct {name_pascal}_Header
{{
	u8   num_channels;
	u8   sample_width;
	u32  sample_rate;
	u32  num_samples;
	u8  *data;
}};

extern {name_pascal}_Header {name_upper}_HEADER;

extern u8 {name_upper}_DATA[{data_length}];


#ifndef JFG_HEADER_ONLY
{name_pascal}_Header {name_upper}_HEADER = {{
	{num_channels},
	{sample_width},
	{sample_rate},
	{num_samples},
	{name_upper}_DATA
}};

u8 {name_upper}_DATA [{data_length}] = {{
	{data}
}};
#endif

#endif
'''.strip()

data = sound.readframes(sound.getnframes() * sound.getnchannels() * sound.getsampwidth())

tmp = ['0x{:02X}'.format(b) for b in data]
acc = []
for n in range(0, len(tmp), 16):
	acc.append(', '.join(tmp[n:n+8]))
data_str = ',\n\t'.join(acc)

output = wave_header_template.format(
	name_upper=name.upper(),
	name_pascal=name,
	num_channels=sound.getnchannels(),
	sample_width=sound.getsampwidth(),
	sample_rate=sound.getframerate(),
	num_samples=sound.getnframes(),
	data_length=len(data),
	data=data_str,
)

with open(out_filename, 'w') as file:
	file.write(output)

#!/usr/bin/python3

import argparse
import os
import os.path
import wave

parser = argparse.ArgumentParser(description='Convert texture to binary.')
parser.add_argument(
	'-i', '--input-dir',
	metavar='input_dir',
	type=str,
	nargs=1,
	required=True,
	help='Directory of waves to convert.',
)
parser.add_argument(
	'-o', '--output-dir',
	metavar='output_dir',
	type=str,
	nargs=1,
	required=True,
	help='Directory to store converted headers.',
)

args = parser.parse_args()
input_dir = args.input_dir[0]
output_dir = args.output_dir[0]

wave_header_template = '''
#ifndef {name_upper}_H
#define {name_upper}_H

#include "jfg/prelude.h"
#include "assets.h"

extern Sound_Header {name_upper}_HEADER;

extern u8 {name_upper}_DATA[{data_length}];


#ifndef JFG_HEADER_ONLY
Sound_Header {name_upper}_HEADER = {{
	{num_channels},
	{sample_width},
	{sample_rate},
	{num_samples}
}};

u8 {name_upper}_DATA [{data_length}] = {{
	{data}
}};
#endif

#endif
'''.strip()

for in_file in os.listdir(input_dir):
	in_filename = os.path.join(input_dir, in_file)
	out_file = in_file.replace('.wav', '.data.h')
	out_filename = os.path.join(output_dir, out_file)

	try:
		in_file_modified_time = os.path.getmtime(in_filename)
		out_file_modidified_time = os.path.getmtime(out_filename)
		if in_file_modified_time < out_file_modidified_time:
			continue
	except:
		pass

	sound = wave.open(in_filename, 'rb')

	data = sound.readframes(sound.getnframes() * sound.getnchannels() * sound.getsampwidth())

	tmp = ['0x{:02X}'.format(b) for b in data]
	acc = []
	for n in range(0, len(tmp), 16):
		acc.append(', '.join(tmp[n:n+8]))
	data_str = ',\n\t'.join(acc)

	wave_name = in_file[:-4]

	output = wave_header_template.format(
		name_upper=wave_name.upper(),
		name_pascal=wave_name.title(),
		num_channels=sound.getnchannels(),
		sample_width=sound.getsampwidth(),
		sample_rate=sound.getframerate(),
		num_samples=sound.getnframes(),
		data_length=len(data),
		data=data_str,
	)

	out_file = in_file.replace('.wav', '.data.h')
	out_filename = os.path.join(output_dir, out_file)
	with open(out_filename, 'w') as file:
		file.write(output)

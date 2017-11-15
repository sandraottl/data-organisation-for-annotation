import subprocess
import argparse


def main():

	parser = argparse.ArgumentParser(description='Split a media file at the desired location')
	parser.add_argument('input', help='the file to split')
	parser.add_argument('splitpoint', help='point at which to split')

	args = vars(parser.parse_args())
	input_file = args['input']
	split_point = args['splitpoint']
	extension = input_file[-4:]
	output_1 = input_file[:-4]+'_part1'+extension
	output_2 = input_file[:-4]+'_part2'+extension
	command = ['ffmpeg', '-i', input_file, '-c', 'copy', '-ss', '00:00:00', '-t', split_point, output_1, '-c', 'copy', '-ss', split_point, output_2]
	subprocess.run(command)

if __name__=='__main__':
	main()
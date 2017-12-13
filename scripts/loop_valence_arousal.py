from valence_arousal import second_intervals
from os import walk
from os.path import splitext, join
import argparse
import re
import fnmatch


def _find_txt_files(folder):
    globexpression = '*.txt'
    reg_expr = re.compile(fnmatch.translate(globexpression), re.IGNORECASE)
    ignore_expr = '_elan_format.txt'
    txts = []
    for root, dirs, files in walk(folder, topdown=True):
        txts += [join(root, j) for j in files if re.match(reg_expr, j) and not j.endswith(ignore_expr)]
    return txts


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('folder', help='folder containing files to convert')
    args = vars(parser.parse_args())
    text_files = _find_txt_files(args['folder'])
    for text_file in text_files:
        output = splitext(text_file)[0] + '_elan_format.txt'
        second_intervals(text_file, output)
        print(text_file)


if __name__ == '__main__':
    main()
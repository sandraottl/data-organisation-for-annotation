import os
import re
from os.path import split, join, isfile, dirname
from os import listdir
import argparse


def rename(folder):
    child_regex = r'-S\d{3}_'
    session_regex = r'_(T|R)\d{2}'
    ext_regex = r'(eaf|pfsx)'
    filenames = [join(folder, file) for file in os.listdir(folder) if isfile(join(folder, file))]
    for filename in filenames:
        child = re.search(child_regex, filename).group(0).split('-')[1]
        session = re.search(session_regex, filename).group(0).split('_')[1]
        ext = re.search(ext_regex, filename).group(1)
        os.rename(filename, join(dirname(filename), 'Dragana_' + child + session + '.' + ext))


def main():
    parser = argparse.ArgumentParser(description='Rename files in folder.')
    parser.add_argument('folder', help='folder containing projects to be renamed')
    args = vars(parser.parse_args())
    rename(args['folder'])


if __name__ == '__main__':
    main()
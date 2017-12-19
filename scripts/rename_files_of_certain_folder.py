import os
import re
from os.path import join, isfile, dirname, basename
import argparse


def rename_dragana(folder):
    child_regex = r'-S\d{3}_'
    session_regex = r'_(T|R)\d{2}'
    ext_regex = r'(eaf|pfsx)'
    filenames = [join(folder, file) for file in os.listdir(folder) if isfile(join(folder, file))]
    for filename in filenames:
        child = re.search(child_regex, filename).group(0).split('-')[1]
        session = re.search(session_regex, filename).group(0).split('_')[1]
        ext = re.search(ext_regex, filename).group(1)
        os.rename(filename, join(dirname(filename), 'Dragana_' + child + session + '.' + ext))


def rename_del_tier(folder):  # remove first 14 characters
    filenames = [join(folder, file) for file in os.listdir(folder) if isfile(join(folder, file))]
    for filename in filenames:
        new_basename = basename(filename)[14:]
        new_filename = join(dirname(filename), new_basename)
        os.rename(filename, new_filename)


def main():
    parser = argparse.ArgumentParser(description='Rename files in folder.')
    parser.add_argument('folder', help='folder containing projects to be renamed')
    args = vars(parser.parse_args())
    rename_del_tier(args['folder'])


if __name__ == '__main__':
    main()

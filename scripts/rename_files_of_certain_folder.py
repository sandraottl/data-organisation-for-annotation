import os
import re
from os.path import join, isfile, dirname, basename
import argparse
import fnmatch
from os import walk


def _find_projects(folder):
    globexpression = '*.csv'
    reg_expr = re.compile(fnmatch.translate(globexpression), re.IGNORECASE)
    # ignore_expr = '.pfsx'
    txts = []
    for root, dirs, files in walk(folder, topdown=True):
        txts += [join(root, j) for j in files if re.match(reg_expr, j)]  # and not j.endswith(ignore_expr)
    return txts


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


def remove_first_8_characters(folder):
    filenames = [join(folder, file) for file in os.listdir(folder) if isfile(join(folder, file))]
    for filename in filenames:
        new_basename = basename(filename)[8:]
        new_filename = join(dirname(filename), new_basename)
        os.rename(filename, new_filename)


def rename_majority(folder):
    filenames = _find_projects(folder)
    child_regex = r'S\d{3}'
    session_regex = r'_(T|R)\d{2}'
    ext_regex = r'(csv)'
    for filename in filenames:
        child = re.search(child_regex, filename).group(0)
        session = re.search(session_regex, filename).group(0)
        ext = re.search(ext_regex, filename).group(1)
        os.rename(filename, join(dirname(filename), child + session + '_fleisskappa_djm' + '.' + ext))


def main():
    parser = argparse.ArgumentParser(description='Rename files in folder.')
    parser.add_argument('folder', help='folder containing projects to be renamed')
    args = vars(parser.parse_args())
    rename_majority(args['folder'])


if __name__ == '__main__':
    main()

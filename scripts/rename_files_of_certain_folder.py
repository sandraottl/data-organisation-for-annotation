import os
import re
from os.path import join, isfile, dirname, basename
import argparse
import fnmatch
from os import walk


def _find_projects(folder):
    globexpression = '*'
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


def remove_first_6_characters(folder):  # 7
    filenames = [join(folder, file) for file in os.listdir(folder) if isfile(join(folder, file))]
    for filename in filenames:
        new_basename = basename(filename)[7:]
        new_filename = join(dirname(filename), new_basename)
        os.rename(filename, new_filename)


def base_8_characters(folder):
    filenames = _find_projects(folder)
    for filename in filenames:
        base = basename(filename)[:8]
        ext = basename(filename)[-4:]
        new_basename = base + '_1234Mix' + ext
        new_filename = join(dirname(filename), new_basename)
        os.rename(filename, new_filename)


def cut_Anita_out_of_name(folder):
    filenames = _find_projects(folder)
    regex = r'B\d{3}_(T|R)\d{2}R{0,1}'
    for filename in filenames:
        new_name = re.search(regex, filename).group(0)
        new_filename = new_name + '.csv'
        os.rename(filename, join(dirname(filename), new_filename))


def rename_majority(folder):
    filenames = _find_projects(folder)
    child_regex = r'S\d{3}'
    session_regex = r'_(T|R)\d{2}R{0,1}'
    ext_regex = r'(csv)'
    for filename in filenames:
        child = re.search(child_regex, filename).group(0)
        session = re.search(session_regex, filename).group(0)
        ext = re.search(ext_regex, filename).group(1)
        os.rename(filename, join(dirname(filename), child + session + '_fleisskappa.' + ext))


def main():
    parser = argparse.ArgumentParser(description='Rename files in folder.')
    parser.add_argument('folder', help='folder containing projects to be renamed')
    args = vars(parser.parse_args())
    rename_majority(args['folder'])
    #base_8_characters(args['folder'])
    #cut_Anita_out_of_name(args['folder'])


if __name__ == '__main__':
    main()

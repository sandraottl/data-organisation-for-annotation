import csv
import re
import argparse
import fnmatch

from os import walk
from os.path import join, basename


def _find_projects(folder):
    globexpression = '*'
    reg_expr = re.compile(fnmatch.translate(globexpression), re.IGNORECASE)
    # ignore_expr = '.pfsx'
    txts = []
    for root, dirs, files in walk(folder, topdown=True):
        txts += [join(root, j) for j in files if re.match(reg_expr, j)]  # and not j.endswith(ignore_expr)
    return txts


def write_into_one(folder, outfile):
    filenames = _find_projects(folder)
    with open(outfile, 'w', newline='') as outfile:
        writer = csv.writer(outfile, delimiter=';')
        for filename in filenames:
            with open(filename, 'r') as file:
                number = file.readline()
                new_filename = basename(filename)[:8]
                writer.writerow((new_filename, number))


def main():
    parser = argparse.ArgumentParser(description='Write fleiss kappa values into one file.')
    parser.add_argument('folder', help='folder containing single fleiss kappa files')
    parser.add_argument('outfile', help='file containing all fleiss kappa values')
    args = vars(parser.parse_args())
    write_into_one(args['folder'], args['outfile'])


if __name__ == '__main__':
    main()

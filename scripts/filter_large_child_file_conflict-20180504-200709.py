import csv
import argparse
import fnmatch
import re
from os.path import join, basename
from os import walk


def ms_to_s(mseconds, seconds, header=True):
    with open(seconds, 'w', newline='') as sec:
        writer = csv.writer(sec, delimiter=';')
        if header:
            first_line = ['session', 'start', 'end', 'tier 0', 'tier 1', 'tier 2']
            writer.writerow(first_line)
        with open(mseconds, 'r') as ms:
            reader = csv.reader(ms, delimiter=',')
            for line in reader:
                writer.writerow((str(line[0]), str(int(line[1]) / 1000), str(int(line[2]) / 1000), str(line[3]), str(line[4]), str(line[5])))


def add_tier2_child_labels(infile, outfile, header=True):
    with open(outfile, 'w', newline='') as outf:
        writer = csv.writer(outf, delimiter=';')
        if header:
            first_line = ['session', 'start', 'end', 'tier 0', 'tier 1', 'tier 2']
            writer.writerow(first_line)
        with open(infile, 'r') as inf:
            reader = csv.reader(inf, delimiter=';')
            next(reader)
            for line in reader:
                if (line[3] == 'child' or line[3] == 'child+therapist' or line[3] == 'child+adult' or line[3] == 'child+zeno' or line[3] == 'child+noise' or line[3] == '2+') and len(line) == 4:
                    writer.writerow((line[0], line[1], line[2], line[3], '', 'not specific to ASC'))
                elif (line[3] == 'child' or line[3] == 'child+therapist' or line[3] == 'child+adult' or line[3] == 'child+zeno' or line[3] == 'child+noise' or line[3] == '2+') and len(line) == 5:
                    writer.writerow((line[0], line[1], line[2], line[3], line[4], 'not specific to ASC'))
                elif len(line) == 4:
                    writer.writerow((line[0], line[1], line[2], line[3], '', ''))
                elif len(line) == 5:
                    writer.writerow((line[0], line[1], line[2], line[3], line[4], ''))
                else:
                    writer.writerow((line[0], line[1], line[2], line[3], line[4], line[5]))


def filter_out_short_ones(infile, outfile, header=True):
    with open(outfile, 'w', newline='') as outf:
        writer = csv.writer(outf, delimiter=';')
        if header:
            first_line = ['session', 'start', 'end', 'tier 0', 'tier 1', 'tier 2']
            writer.writerow(first_line)
        with open(infile, 'r') as inf:
            reader = csv.reader(inf, delimiter=';')
            next(reader)
            for line in reader:
                if (float(line[2]) - float(line[1])) > 0.5:
                    writer.writerow((line[0], line[1], line[2], line[3], line[4], line[5]))


def filter_out_labels_without_tier1_tier2(infile, outfile, header=True):
    with open(outfile, 'w', newline='') as outf:
        writer = csv.writer(outf, delimiter=';')
        if header:
            first_line = ['session', 'start', 'end', 'tier 0', 'tier 1', 'tier 2']
            writer.writerow(first_line)
        with open(infile, 'r') as inf:
            reader = csv.reader(inf, delimiter=';')
            next(reader)
            for line in reader:
                if (line[3] == 'child' or line[3] == 'child+therapist' or line[3] == 'child+adult' or line[3] == 'child+zeno'):
                    if line[4] != '' and line[5] != '':
                        writer.writerow((line[0], line[1], line[2], line[3], line[4], line[5]))
                else:
                    writer.writerow((line[0], line[1], line[2], line[3], line[4], line[5]))


def filter_out_non_child_lines(infile, outfile):
    with open(outfile, 'w', newline='') as outf:
        writer = csv.writer(outf, delimiter=';')
        with open(infile, 'r') as inf:
            reader = csv.reader(inf, delimiter=';')
            first_line = next(reader)
            writer.writerow(first_line)
            for line in reader:
                if ('child' in line[3]) or (line[3] == '2+'):
                    writer.writerow(line)


def _find_csv_files(folder):
    globexpression = '*.csv'
    reg_expr = re.compile(fnmatch.translate(globexpression), re.IGNORECASE)
    ignore_expr1 = '_fleiss.csv'
    ignore_expr2 = '_majority.csv'
    txts = []
    for root, dirs, files in walk(folder, topdown=True):
        txts += [join(root, j) for j in files if re.match(reg_expr, j) and not j.endswith(ignore_expr1) and not j.endswith(ignore_expr2)]  # 
    return txts


def main():
    parser = argparse.ArgumentParser(description='Convert millisecond start and stop values of a labels file into seconds.')
    parser.add_argument('infolder', help='start and stop in milliseconds')
    parser.add_argument('outfolder', help='start and stop in seconds')
    parser.add_argument('--header', action='store_true')
    args = vars(parser.parse_args())
    #ms_to_s(args['infiel'], args['outfile'], args['header']
    #add_tier2_child_labels(args['infile'], args['outfile'], args['header'])
    #filter_out_short_ones(args['infile'], args['outfile'], args['header'])
    #filter_out_labels_without_tier1_tier2(args['infile'], args['outfile'], args['header'])
    for file in _find_csv_files(args['infolder']):
        filter_out_non_child_lines(file, join(args['outfolder'], basename(file)))


if __name__ == '__main__':
    main()

import csv
import pandas as pd
import argparse
import re
import fnmatch
from bisect import bisect_left
from os.path import basename, join
from os import walk
from tqdm import tqdm

# infile = 'U:\SandraOttl\VA-annotations\B001_R01_arousal.txt'
# elanfile = 'U:\SandraOttl\VA-annotations\B001_R01_labels.txt'
# outfile = 'U:\SandraOttl\VA-annotations\B001_R01_arousal_out.txt'
VA_list = sorted([-1, -0.5, 0, 0.5, 1])
# df = pd.read_csv(infile, sep='\t', names=['time', 'value'])
# print(df[(df['time']>100000000000)]['value'].empty)


def takeClosest(myList, myNumber):
    pos = bisect_left(myList, myNumber)
    if pos == 0:
        return myList[0]
    if pos == len(myList):
        return myList[-1]
    before = myList[pos - 1]
    after = myList[pos]
    if after - myNumber < myNumber - before:
        return after
    else:
        return before


def speech_intervals(infile, elanfile, outfile):
    with open(elanfile, 'r') as ef:
        with open(outfile, 'w', newline='') as of:
            df = pd.read_csv(infile, sep=',', names=['time', 'value'])
            reader_elan = csv.reader(ef, delimiter=',')
            writer = csv.writer(of, delimiter=';')
            for line in reader_elan:
                start = float(line[0])
                stop = float(line[1])
                # if line[2]=='c':
                value = (df[(df['time'] < stop) & (df['time'] > start)]['value'].mean(axis=0)) / 1000
                label = takeClosest(VA_list, value)
                writer.writerow([start, stop, label])


def second_intervals(infile, outfile, target='arousal'):
    with open(outfile, 'w', newline='') as of:
        #try:
        df = pd.read_csv(infile, sep=',')
        # df['time'] = df['time'].apply(lambda x: x.replace(',', '.'))
        writer = csv.writer(of, delimiter=';')
        for i in range(1000000000000):
            start = i
            stop = i + 1
            series = df[(df['time'] < stop) & (df['time'] > start)][target]
            # print(series)
            if series.empty:
                break
            value = (series.mean(axis=0)) / 1000
            label = takeClosest(VA_list, value)
            writer.writerow([start, stop, label])
    # except:
        #     df = pd.read_csv(infile, sep=',', names=['time', 'value'], decimal=',')
        #     # df['time'] = df['time'].apply(lambda x: x.replace(',', '.'))
        #     writer = csv.writer(of, delimiter=';')
        #     for i in range(1000000000000):
        #         start = i
        #         stop = i + 1
        #         series = df[(df['time'] < stop) & (df['time'] > start)]['value']
        #         # print(series)
        #         if series.empty:
        #             break
        #         value = (series.mean(axis=0)) / 1000
        #         label = takeClosest(VA_list, value)
        #         writer.writerow([start, stop, label])


def _find_csv_files(folder):
    globexpression = '*.csv'
    reg_expr = re.compile(fnmatch.translate(globexpression), re.IGNORECASE)
    ignore_expr1 = '_fleiss.csv'
    ignore_expr2 = '_majority.csv'
    txts = []
    for root, dirs, files in walk(folder, topdown=True):
        txts += [join(root, j) for j in files if re.match(reg_expr, j) and not j.endswith(ignore_expr1) and not j.endswith(ignore_expr2)]  # 
    return txts


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert arousal/valence annotations into elan format.')
    parser.add_argument('infolder', help='folder containing files containing arousal/valence annotations')
    parser.add_argument('outfolder', help='folder containing files containing labels in elan format')
    # parser.add_argument('-elanfile', help='file containting elan annotations')

    args = parser.parse_args()
    tier45_files = _find_csv_files(args.infolder)
    for file in tqdm(tier45_files):
        second_intervals(file, join(args.outfolder, basename(file)))

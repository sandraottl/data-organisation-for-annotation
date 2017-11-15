import csv
import os
import argparse
from shutil import copyfile


def remove_overlaps(infile, outfile, tmp_1='tmp_1.txt', tmp_2='tmp_2.txt'):
    copyfile(infile, tmp_1)
    for _ in range(5):
        with open(tmp_1, 'r', newline='') as ff:
            with open(tmp_2, 'w', newline='') as cf:
                try:
                    pass
                except StopIteration as e:
                    pass
                reader = csv.reader(ff, delimiter='\t')
                writer = csv.writer(cf, delimiter='\t')
                first_line = next(reader)
                while True:
                    try:
                        if not first_line:
                            break
                        start_time_first = float(first_line[0])
                        stop_time_first = float(first_line[1])
                        label_first = str(first_line[2])
                        second_line = next(reader)
                        if not second_line:
                            break
                        start_time_second = float(second_line[0])
                        stop_time_second = float(second_line[1])
                        label_second = str(second_line[2])
                        label = 'o'
                        if (stop_time_first > start_time_second):
                            if label_first == label_second:
                                label = label_first
                            if (label_first=='t' and label_second=='c') or (label_second=='t' and label_first=='c'):
                                label = '1'
                            if (label_first=='c' and label_second=='a') or (label_first=='a' and label_second=='c'):
                                label = '2'
                            if (label_first=='c' and label_second=='z') or (label_first=='z' and label_second=='c'):
                                label = '3'
                            if (label_first=='t' and label_second=='a') or (label_first=='a' and label_second=='t'):
                                label = '4'
                            if (label_first=='t' and label_second=='z') or (label_first=='z' and label_second=='t'):
                                label = '5'
                            if (label_first=='a' and label_second=='z') or (label_first=='z' and label_second=='a'):
                                label = '6'
                            #
                            if (label_first=='1') and (label_second=='a' or label_second=='z'):
                                label = '7'
                            if (label_first=='2') and (label_second=='t' or label_second=='z'):
                                label = '7'
                            if (label_first=='3') and (label_second=='a' or label_second=='t'):
                                label = '7'
                            if (label_first=='4') and (label_second=='c' or label_second=='z'):
                                label = '7'
                            if (label_first=='5') and (label_second=='a' or label_second=='c'):
                                label = '7'
                            if (label_first=='6') and (label_second=='t' or label_second=='c'):
                                label = '7'
                            # other way around
                            if (label_second=='1') and (label_first=='a' or label_first=='z'):
                                label = '7'
                            if (label_second=='2') and (label_first=='t' or label_first=='z'):
                                label = '7'
                            if (label_second=='3') and (label_first=='a' or label_first=='t'):
                                label = '7'
                            if (label_second=='4') and (label_first=='c' or label_first=='z'):
                                label = '7'
                            if (label_second=='5') and (label_first=='a' or label_first=='c'):
                                label = '7'
                            if (label_second=='6') and (label_first=='t' or label_first=='c'):
                                label = '7'
                            #
                            if (label_first=='1') and (label_second=='t' or label_second=='c'):
                                label = '1'
                            if (label_first=='2') and (label_second=='a' or label_second=='c'):
                                label = '2'
                            if (label_first=='3') and (label_second=='z' or label_second=='c'):
                                label = '3'
                            if (label_first=='4') and (label_second=='t' or label_second=='a'):
                                label = '4'
                            if (label_first=='5') and (label_second=='t' or label_second=='z'):
                                label = '5'
                            if (label_first=='6') and (label_second=='a' or label_second=='z'):
                                label = '6'
                            # other way around
                            if (label_second=='1') and (label_first=='t' or label_first=='c'):
                                label = '1'
                            if (label_second=='2') and (label_first=='a' or label_first=='c'):
                                label = '2'
                            if (label_second=='3') and (label_first=='z' or label_first=='c'):
                                label = '3'
                            if (label_second=='4') and (label_first=='t' or label_first=='a'):
                                label = '4'
                            if (label_second=='5') and (label_first=='t' or label_first=='z'):
                                label = '5'
                            if (label_second=='6') and (label_first=='a' or label_first=='z'):
                                label = '6'
                            #
                            if (label_first=='1') and (label_second=='2' or label_second=='3' or label_second=='4' or label_second=='5' or label_second=='6'):
                                label = '7'
                            if (label_first=='2') and (label_second=='1' or label_second=='3' or label_second=='4' or label_second=='5' or label_second=='6'):
                                label = '7'
                            if (label_first=='3') and (label_second=='2' or label_second=='1' or label_second=='4' or label_second=='5' or label_second=='6'):
                                label = '7'
                            if (label_first=='4') and (label_second=='2' or label_second=='3' or label_second=='1' or label_second=='5' or label_second=='6'):
                                label = '7'
                            if (label_first=='5') and (label_second=='2' or label_second=='3' or label_second=='4' or label_second=='1' or label_second=='6'):
                                label = '7'
                            if (label_first=='6') and (label_second=='2' or label_second=='3' or label_second=='4' or label_second=='5' or label_second=='1'):
                                label = '7'
                            # other way around
                            if (label_second=='1') and (label_first=='2' or label_first=='3' or label_first=='4' or label_first=='5' or label_first=='6'):
                                label = '7'
                            if (label_second=='2') and (label_first=='1' or label_first=='3' or label_first=='4' or label_first=='5' or label_first=='6'):
                                label = '7'
                            if (label_second=='3') and (label_first=='2' or label_first=='1' or label_first=='4' or label_first=='5' or label_first=='6'):
                                label = '7'
                            if (label_second=='4') and (label_first=='2' or label_first=='3' or label_first=='1' or label_first=='5' or label_first=='6'):
                                label = '7'
                            if (label_second=='5') and (label_first=='2' or label_first=='3' or label_first=='4' or label_first=='1' or label_first=='6'):
                                label = '7'
                            if (label_second=='6') and (label_first=='2' or label_first=='3' or label_first=='4' or label_first=='5' or label_first=='1'):
                                label = '7'
                            #
                            if (label_first=='7') or (label_second=='7'):
                                label = '7'
                            writer.writerow([start_time_first, stop_time_second, label])
                            second_line = next(reader)
                        else:
                            writer.writerow(first_line)
                        first_line = second_line
                    except StopIteration:
                        break
                tmp_1, tmp_2 = tmp_2, tmp_1
    tmp_files = [os.path.abspath(tmp_1), os.path.abspath(tmp_2)]
    most_recent = sorted(tmp_files, key=os.path.getmtime)[-1]
    copyfile(most_recent, outfile)
    os.remove(tmp_1)
    os.remove(tmp_2)

def main():
    parser = argparse.ArgumentParser(description='Remove overlaps of an audacity label text file.')
    parser.add_argument('input', help='file containing audacity labels with overlaps')
    parser.add_argument('output', help='destination for audacity labels file without overlaps')

    args = vars(parser.parse_args())
    remove_overlaps(args['input'], args['output'])

if __name__ == '__main__':
    main()
import csv
import argparse
import random


TIER_LABELS = {0: ['t', 'c', 'a', 'z', '1', '2', '3', '4', '5', '6', '7', 'None'], 1: ['speech', 'non-speech', 'speech-like', 'shouting', 'unsure', 'None'], 2: ['echolalia (immediate)', 'echolalia (delayed)', 'Another ASC Vocal Behaviour', 'not specific to ASC', 'unsure (echolalia)', 'unsure (ASC behaviour)', ' ', '-s', 'irregualr intonation', 'None']}


def majority_vote(first, second, third, outfile):
    with open(first, 'r') as first, open(second, 'r') as second, open(third, 'r') as third, open(outfile, 'w', newline='') as outfile:
        reader_first = csv.reader(first, delimiter='\t')
        reader_second = csv.reader(second, delimiter='\t')
        reader_third = csv.reader(third, delimiter='\t')
        writer = csv.writer(outfile, delimiter='\t')
        line_second = next(reader_second)
        line_third = next(reader_third)
        for line in reader_first:
            print(line, line_second, line_third)
            if (((line[0] == line_second[0]) and (line_second[0] == line_third[0])) and ((line[1] == line_second[1]) and (line_second[1] == line_third[1]))):  # all intervals the same
                if ((line[2] == line_second[2]) and (line_second[2] == line_third[2])) or (line[2] == line_second[2]) or (line[2] == line_third[2]):
                    writer.writerow(line)
                    line_second = next(reader_second)
                    line_third = next(reader_third)
                elif (line_second[2] == line_third[2]):
                    writer.writerow((line[0], line[1], line_second[2]))
                    line_second = next(reader_second)
                    line_third = next(reader_third)
                else:
                    poss=[line[2], line_second[2], line_third[2]]
                    writer.writerow((line[0], line[1], random.choice(poss)))
                    line_second = next(reader_second)
                    line_third = next(reader_third)
            else:
                print('Not the same intervals')
                break



            # elif ((line[0] < line_second[0]) and (line[1] < line_second[1])) or ((line[0] < line_third[0]) and (line[1] < line_third[1])):  # first file earlier
            #     writer.writerow(line)
            #     next(reader_second)
            #     next(reader_third)
            # elif (line_second[0] < line[0]) and (line_second[1] < line[1]):  # second file earlier than first file
            #     if line_second == line_third:  # second and third all the same
            #         writer.writerow(line_second)
            #         next(reader_second)
            #         next(reader_third)
            #     elif (line_second[0] == line_third[0]) and (line_second[1] == line_third[1]) and (line_second[2] != line_third[2]):
            #         poss=[line_second[2], line_third[2]]
            #         writer.writerow((line_second[0], line_second[1], random.choice(poss)))
            #         next(reader_second)
            #         next(reader_third)
            #     elif (line_second[0] < line_third[0]) and (line_second[1] < line_third[1]):  # second earlier than first and third
            #         writer.writerow(line_second)
            #         next(reader_second)
            #         next(reader_third)
            #     elif (line_third[0] < line_second[0]) and (line_third[1] < line_second[1]):  # third earlier than second
            #         writer.writerow()


def main():
    parser = argparse.ArgumentParser(description='Computes one set of labels from three label files.')
    parser.add_argument('first', help='first file')
    parser.add_argument('second', help='second file')
    parser.add_argument('third', help='third file')
    parser.add_argument('outfile', help='file with combined labels')
    args = vars(parser.parse_args())
    majority_vote(args['first'], args['second'], args['third'], args['outfile'])


if __name__ == '__main__':
    main()

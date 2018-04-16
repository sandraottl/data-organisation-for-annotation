import csv
import argparse


def write_into_one(tier0, tier1, tier2, session, outfile, header=False):
    out = []
    with open(outfile, 'a', newline='') as outfile:
        writer = csv.writer(outfile, delimiter=';')
        if header:
            first_line = ['session', 'start', 'end', 'tier 0', 'tier 1', 'tier 2']
            writer.writerow(first_line)
        # tier 0 labels
        with open(tier0, 'r') as zero:
            reader_zero = csv.reader(zero, delimiter='\t')
            for line in reader_zero:
                out.append({'start': line[0], 'stop': line[1], 'labels': [line[2]]})
        # tier 1 labels
        with open(tier1, 'r') as one:
            reader_one = csv.reader(one, delimiter=';')
            for line in reader_one:
                for i, element in enumerate(out):
                    if element['start'] == line[0] and element['stop'] == line[1]:
                        out[i]['labels'].append(line[2])
                        break
        # tier 2 labels
        with open(tier2, 'r') as two:
            reader_two = csv.reader(two, delimiter=';')
            for line in reader_two:
                for j, element in enumerate(out):
                    if element['start'] == line[0] and element['stop'] == line[1]:
                        out[j]['labels'].append(line[2])
                        break
        for el in out:
            writer.writerow([session, el['start'], el['stop']] + [label for label in el['labels']])


def main():
    parser = argparse.ArgumentParser(description='Write all labels into one file.')
    parser.add_argument('tier0', help='labels for tier0')
    parser.add_argument('tier1', help='labels for tier1')
    parser.add_argument('tier2', help='labels for tier2')
    parser.add_argument('session', help='session number (1,2,3,4,5,6)')
    parser.add_argument('outfile', help='file containing all sessions')
    parser.add_argument('--header', action='store_true')
    args = vars(parser.parse_args())
    write_into_one(args['tier0'], args['tier1'], args['tier2'], args['session'], args['outfile'], args['header'])


if __name__ == '__main__':
    main()

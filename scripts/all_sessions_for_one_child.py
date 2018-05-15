import csv
import argparse
import re
import fnmatch
from tqdm import tqdm
from os.path import basename, join
from os import walk
from decimal import Decimal


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
                out.append({'start': Decimal(line[0]), 'stop': Decimal(line[1]), 'labels': [line[2]]})
        # tier 1 labels
        with open(tier1, 'r') as one:
            reader_one = csv.reader(one, delimiter=';')
            for line in reader_one:
                for i, element in enumerate(out):
                    if element['start'] == Decimal(line[0]) and element['stop'] == Decimal(line[1]):
                        out[i]['labels'].append(line[2])
                        break
        # tier 2 labels
        with open(tier2, 'r') as two:
            reader_two = csv.reader(two, delimiter=';')
            for line in reader_two:
                for j, element in enumerate(out):
                    if element['start'] == Decimal(line[0]) and element['stop'] == Decimal(line[1]):
                        out[j]['labels'].append(line[2])
                        break
        for el in out:
            writer.writerow([session, el['start'], el['stop']] + [label for label in el['labels']])


def quantised_labels(infile, interval=Decimal('0.001'), delimiter='\t'):
    with open(infile, 'r') as infile:
        reader = csv.reader(infile, delimiter=delimiter)
        #with open(outfile, 'w') as outfile:
            #writer = csv.writer(outfile, delimiter=',')
        output = []
        try:
            line = next(reader)
        except StopIteration:
            output.append('None')
            return output
        for i in range(10000000000):
            if int(Decimal(line[0]) / interval) <= i < int(Decimal(line[1]) / interval):
                output.append(line[2])
                #writer.writerow([i / 10, line[2]])
            elif i >= int(Decimal(line[1]) / interval):    
                try:
                    line = next(reader)
                except StopIteration:
                    break
                if int(Decimal(line[0]) / interval) <= i < int(Decimal(line[1]) / interval):
                    output.append(line[2])
                    #writer.writerow([i / 10, line[2]])
                else:
                    output.append('None')
                    #writer.writerow([i / 10, 'None'])
            else:
                output.append('None')
                #writer.writerow([i / 10, 'None'])
    #print(output[499444:499460])
    return output


def pad_to_n(a, N):
    a += ['None'] * (N - len(a))
    return a


def write_into_one_quantised(tier0, tier1, tier2, session):
    interval = Decimal('0.001')
    current_annotation = None
    annotations = []
    tiers = (tier0, tier1, tier2)
    max_length = max(map(len, tiers))
    tiers = list(map(lambda x: pad_to_n(x, max_length), tiers))
    for i, (tier0_label, tier1_label, tier2_label) in enumerate(zip(*tiers)):
        if not current_annotation:
            current_annotation = {}
            current_annotation['session'] = session
            current_annotation['start'] = i * interval
            current_annotation['end'] = (i + 1) * interval
            current_annotation['tier 0'] = tier0_label
            current_annotation['tier 1'] = tier1_label
            current_annotation['tier 2'] = tier2_label
        elif [current_annotation['tier 0'], current_annotation['tier 1'], current_annotation['tier 2']] == [tier0_label, tier1_label, tier2_label]:
            current_annotation['end'] = (i + 1) * interval
        else:
            if (not [current_annotation['tier 0'], current_annotation['tier 1'], current_annotation['tier 2']] == ['None', 'None', 'None']) and (current_annotation['end'] - current_annotation['start']) >= 0.5:
                annotations.append(current_annotation.copy())
            current_annotation['session'] = session
            current_annotation['start'] = i * interval
            current_annotation['end'] = (i + 1) * interval
            current_annotation['tier 0'] = tier0_label
            current_annotation['tier 1'] = tier1_label
            current_annotation['tier 2'] = tier2_label
    if (not [current_annotation['tier 0'], current_annotation['tier 1'], current_annotation['tier 2']] == ['None', 'None', 'None']) and (current_annotation['end'] - current_annotation['start']) >= 0.5:
        annotations.append(current_annotation.copy())
    return annotations


def _find_csv_files(folder):
    globexpression = '*.csv'
    reg_expr = re.compile(fnmatch.translate(globexpression), re.IGNORECASE)
    ignore_expr1 = '_fleiss.csv'
    ignore_expr2 = '_majority.csv'
    txts = []
    for root, dirs, files in walk(folder, topdown=True):
        txts += [join(root, j) for j in files if re.match(reg_expr, j) and not j.endswith(ignore_expr1) and not j.endswith(ignore_expr2)]  # 
    return txts


def child_and_session_dict(tier0_files, tier1_files, tier2_files):
    child_regex = r'S\d{3}'
    session_regex = r'(T|R)\d{2}'
    sessions_dict = {}
    for tier0_file in tier0_files:
        child_name = re.search(child_regex, basename(tier0_file)).group(0)
        session_name = re.search(session_regex, basename(tier0_file)).group(0)
        tier1_file = [file for file in tier1_files if child_name in basename(file) and session_name in basename(file)][0]
        tier2_file = [file for file in tier2_files if child_name in basename(file) and session_name in basename(file)][0]
        if child_name in sessions_dict:
            sessions_dict[child_name][session_name] = [tier0_file, tier1_file, tier2_file]
        else:
            sessions_dict[child_name] = {session_name: [tier0_file, tier1_file, tier2_file]}
    return sessions_dict


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


def main_regex():
    parser = argparse.ArgumentParser(description='Write all labels into one file.')
    parser.add_argument('tier0', help='folder for labels for tier0')
    parser.add_argument('tier1', help='folder for labels for tier1')
    parser.add_argument('tier2', help='folder for labels for tier2')
    parser.add_argument('outputfolder', help='folder for file containing all sessions')
    args = parser.parse_args()
    tier0_files  = _find_csv_files(args.tier0)
    tier1_files  = _find_csv_files(args.tier1)
    tier2_files  = _find_csv_files(args.tier2)
    child_dict = child_and_session_dict(tier0_files, tier1_files, tier2_files)
    for child in tqdm(sorted(child_dict)):
    #child = 'B012'
        with open(join(args.outputfolder, child + '_overview.csv'), 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, ['session', 'start', 'end', 'tier 0', 'tier 1', 'tier 2'], delimiter=';')
            writer.writeheader()
            for session_name in tqdm(sorted(child_dict[child])):
                print(child_dict[child][session_name])
                quantised_tier0 = quantised_labels(child_dict[child][session_name][0], delimiter='\t')
                quantised_tier1 = quantised_labels(child_dict[child][session_name][1], delimiter=';')
                quantised_tier2 = quantised_labels(child_dict[child][session_name][2], delimiter=';')
                combined_annotations = write_into_one_quantised(quantised_tier0, quantised_tier1, quantised_tier2, session=session_name)
                writer.writerows(combined_annotations)



if __name__ == '__main__':
    main_regex()


# python .\all_sessions_for_one_child.py Y:\SandraOttl\de-enigma\annotations\de-enigma_audio_annotation_package\serbia\extracted_labels\tier0 Y:\SandraOttl\de-enigma\annotations\de-enigma_audio_annotation_package\serbia\goldstandard\tier_1_speech-type\2-latest-version Y:\SandraOttl\de-enigma\annotations\de-enigma_audio_annotation_package\serbia\goldstandard\tier_2_speech-type_ASC\2-latest-version Y:\SandraOttl\de-enigma\all_sessions_of_one_child\Serbia
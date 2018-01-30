import csv
import numpy as np
import argparse
import re
import fnmatch
from os.path import basename, join
from os import walk
from decimal import Decimal
from numpy import argmax
from scipy.signal import medfilt


TIER_LABELS = {0: ['t', 'c', 'a', 'z', '1', '2', '3', '4', '5', '6', '7', 'None'], 1: ['speech', 'non-speech', 'speech-like', 'shouting', 'shouting (speech)', 'shouting (non-speech)', 'unsure', 'unsure (echolalia)', 'None'], 2: ['echolalia (immediate)', 'echolalia (delayed)', 'Another ASC Vocal Behaviour', 'not specific to ASC', 'unsure (echolalia)', 'unsure (ASC behaviour)', ' ', '-s', 'irregualr intonation', 'None']}


def quantised_labels(infile, interval):
    with open(infile, 'r') as infile:
        reader = csv.reader(infile, delimiter='\t')
        #with open(outfile, 'w') as outfile:
            #writer = csv.writer(outfile, delimiter=',')
        output = []
        line = next(reader)
        for i in range(1000000):
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
    return output


def combine_annotators(annotators, tier):
    labels = TIER_LABELS[tier]
    min_length = min(map(len, annotators))
    mat = np.zeros((min_length, len(labels)))
    for i in range(min_length):
        for j, label in enumerate(labels):
            for annotator in annotators:
                if annotator[i] == label:
                    mat[i][j] += 1
    return mat


def majority_vote(mat, interval, tier):
    # majority = medfilt(argmax(mat, axis=1)).astype(int)
    majority = argmax(mat, axis=1)
    print(majority)
    current_annotation = None
    annotations = []
    for i, entry in enumerate(majority):
        entry = TIER_LABELS[tier][entry]
        if not current_annotation:
            current_annotation = {}
            current_annotation['start'] = i * interval
            current_annotation['stop'] = (i + 1) * interval
            current_annotation['label'] = entry
        elif current_annotation['label'] == entry:
            current_annotation['stop'] = (i + 1) * interval
        else:
            if not current_annotation['label'] == 'None':
                annotations.append(current_annotation.copy())
            current_annotation['start'] = i * interval
            current_annotation['stop'] = (i + 1) * interval
            current_annotation['label'] = entry
    return annotations


DEBUG = False
def computeKappa(mat):
    """ Computes the Kappa value
        @param n Number of rating per subjects (number of human raters)
        @param mat Matrix[subjects][categories]
        @return The Kappa value """
    n = checkEachLineCount(mat)   # PRE : every line count must be equal to n
    N = len(mat)
    k = len(mat[0])
    
    if DEBUG:
        print (str(n) + " raters.")
        print (str(N) + " subjects.")
        print (str(k) + " categories.")
    
    # Computing p[]
    p = [0.0] * k
    for j in range(k):
        p[j] = 0.0
        for i in range(N):
            p[j] += mat[i][j]
        p[j] /= N*n
    if DEBUG: print ("p = " + str(p))
    
    # Computing P[]    
    P = [0.0] * N
    for i in range(N):
        P[i] = 0.0
        for j in range(k):
            P[i] += mat[i][j] * mat[i][j]
        P[i] = (P[i] - n) / (n * (n - 1))
    if DEBUG: print ("P = " + str(P))
    
    # Computing Pbar
    Pbar = sum(P) / N
    if DEBUG: print ("Pbar = " + str(Pbar))
    
    # Computing PbarE
    PbarE = 0.0
    for pj in p:
        PbarE += pj * pj
    if DEBUG: print ("PbarE = " + str(PbarE))
    
    kappa = (Pbar - PbarE) / (1 - PbarE)
    if DEBUG: print ("kappa = " + str(kappa))
    
    return kappa


def checkEachLineCount(mat):
    """ Assert that each line has a constant number of ratings
        @param mat The matrix checked
        @return The number of ratings
        @throws AssertionError If lines contain different number of ratings """
    n = sum(mat[0])
    
    assert all(sum(line) == n for line in mat[1:]), "Line count != %d (n value)." % n
    return n


def _find_csv_files(folder):
    globexpression = '*.csv'
    reg_expr = re.compile(fnmatch.translate(globexpression), re.IGNORECASE)
    ignore_expr1 = '_fleiss.csv'
    ignore_expr2 = '_majority.csv'
    txts = []
    for root, dirs, files in walk(folder, topdown=True):
        txts += [join(root, j) for j in files if re.match(reg_expr, j) and not j.endswith(ignore_expr1) and not j.endswith(ignore_expr2)]  # 
    return txts


def session_names(folder):
    files = _find_csv_files(folder)
    session_name_regex = r'_S\d{3}_(T|R)\d{2}'
    sessions_dict = {}
    for file in files:
        # print(file)
        session_name = re.search(session_name_regex, file).group(0)
        if session_name in sessions_dict:
            sessions_dict[session_name].append(file)
        else:
            sessions_dict[session_name] = [file]
    return sessions_dict


def main_fleiss_kappa():  # 
    parser = argparse.ArgumentParser(description='Compute Fleiss Kappa of three annotation files.')
    # parser.add_argument('annotators', nargs='+', help='files containing (audacity) labels from 3 different annotators for the same project')
    parser.add_argument('input', help='folder containing all annotation files')
    parser.add_argument('-interval', type=Decimal, help='quantisation interval in seconds', default=Decimal('0.1'))
    parser.add_argument('-tier', help='tier type (0, 1, 2)', type=int, default=2)
    # parser.add_argument('output', help='output file destination')
    args = vars(parser.parse_args())
    session_names_dict = session_names(args['input'])
    for session_name in session_names_dict:
        annotation_files = session_names_dict[session_name]
        print(annotation_files)
        annotators = [quantised_labels(annotator, args['interval']) for annotator in annotation_files]
    # annotators = [quantised_labels(annotator, args['interval']) for annotator in args['annotators']]
    # print(list(map(len, annotators)))
        mat = combine_annotators(annotators, args['tier'])
        fleiss_kappa = computeKappa(mat)
        print(session_name, fleiss_kappa)
        # with open(args['output'], 'w', newline='') as output:
        #     output.write(str(fleiss_kappa))
        annotator_name_regex = r'^([a-zA-Z]*)_'
        annotator_names = '_'.join([re.search(annotator_name_regex, filename).group(1) for filename in map(basename, annotation_files)])
        outfile_name = join(args['input'], annotator_names + session_name + '_fleiss.csv')
        with open(outfile_name, 'w', newline='') as outfile:
            outfile.write(str(fleiss_kappa))


def main_majority_vote():  # 
    parser = argparse.ArgumentParser(description='Create Majority Vote of three annotation files.')
    parser.add_argument('input', help='folder containing all annotation files')
    parser.add_argument('-interval', type=Decimal, help='quantisation interval in seconds', default=Decimal('0.001'))
    parser.add_argument('-tier', help='tier type (0, 1, 2)', type=int, default=1)
    args = vars(parser.parse_args())
    session_names_dict = session_names(args['input'])
    for session_name in session_names_dict:
        annotation_files = session_names_dict[session_name]
        print(annotation_files)
        annotators = [quantised_labels(annotator, args['interval']) for annotator in annotation_files]
        mat = combine_annotators(annotators, args['tier'])
        majority = majority_vote(mat, args['interval'], args['tier'])
        annotator_name_regex = r'^([a-zA-Z]*)_'
        annotator_names = '_'.join([re.search(annotator_name_regex, filename).group(1) for filename in map(basename, annotation_files)])
        outfile_name = join(args['input'], annotator_names + session_name + '_majority.csv')
        with open(outfile_name, 'w', newline='') as outfile:
            writer = csv.writer(outfile, delimiter=';')
            for el in majority:
                writer.writerow((el['start'], el['stop'], el['label']))


if __name__ == '__main__':
    main_majority_vote()




#first = labels_for_each_second('Y:\SandraOttl\de-enigma/fleiss_kappa/test_B002_T02_labels_aud.txt', 0.1)
#second = labels_for_each_second('Y:\SandraOttl\de-enigma/fleiss_kappa/test_B002_T02_labels_aud.txt', 0.1)

#annotators = [first] + [second]

#print(combine_annotators(annotators))

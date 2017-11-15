import csv
from decimal import Decimal
import numpy as np
import argparse


TIER_LABELS = {0: ['t', 'c', 'a', 'z', '1', '2', '3', '4', '5', '6', '7', 'None'], 1: ['speech', 'non-speech', 'speech-like', 'shouting', 'unsure', 'None'], 2: ['echolalia (immediate)', 'echolalia (delayed)', 'Another ASC Vocal Behaviour', 'not specific to ASC', 'unsure (echolalia)', 'unsure (ASC behaviour)', ' ', '-s', 'irregualr intonation', 'None']}


def quantised_labels(infile, interval):
    with open(infile, 'r') as infile:
        reader = csv.reader(infile, delimiter='\t')
        #with open(outfile, 'w') as outfile:
            #writer = csv.writer(outfile, delimiter=',')
        output = []
        line = next(reader)
        for i in range(1000000):
            if int(float(line[0]) / interval) <= i < int(float(line[1]) / interval):
                output.append(line[2])
                #writer.writerow([i / 10, line[2]])
            elif i >= int(float(line[1]) / interval):    
                try:
                    line = next(reader)
                except StopIteration:
                    break
                if int(float(line[0]) / interval) <= i < int(float(line[1]) / interval):
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
    mat = np.zeros((min_length,len(labels)))
    for i in range(min_length):
        for j, label in enumerate(labels):
            for annotator in annotators:
                if annotator[i] == label:
                    mat[i][j] += 1
    return mat


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


def main():
    parser = argparse.ArgumentParser(description='Insert audacity labels into an existing elan file on a specific tier.')
    parser.add_argument('annotators_tier0', nargs='+', help='files containing (audacity) labels from different annotators for the same project\'s tier 0')
    parser.add_argument('annotators_tier1', nargs='+', help='files containing (audacity) labels from different annotators for the same project\'s tier 1')
    parser.add_argument('annotators_tier2', nargs='+', help='files containing (audacity) labels from different annotators for the same project\'s tier 2')
    parser.add_argument('output', help='location of the output file')
    parser.add_argument('-interval', help='quantisation interval in seconds', default=0.1)
    #parser.add_argument('-tier', help='tier type (0, 1, 2)', type=int, default=0)
    args = vars(parser.parse_args())
    with open(args['output'], 'w') as output:
        annotators = [quantised_labels(annotator, args['interval']) for annotator in args['annotators_tier0']]
        mat_0 = combine_annotators(annotators, 0)
        output.writerow(['Fleiss Kappa for Tier 0: ', computeKappa(mat_0)])
        annotators = [quantised_labels(annotator, args['interval']) for annotator in args['annotators_tier1']]
        mat_1 = combine_annotators(annotators, 1)
        output.writerow(['Fleiss Kappa for Tier 1: ', computeKappa(mat_1)])
        annotators = [quantised_labels(annotator, args['interval']) for annotator in args['annotators_tier2']]
        mat_2 = combine_annotators(annotators, 2)
        output.writerow(['Fleiss Kappa for Tier 2: ', computeKappa(mat_2)])


if __name__ == '__main__':
    main()




#first = labels_for_each_second('Y:\SandraOttl\de-enigma/fleiss_kappa/test_B002_T02_labels_aud.txt', 0.1)
#second = labels_for_each_second('Y:\SandraOttl\de-enigma/fleiss_kappa/test_B002_T02_labels_aud.txt', 0.1)

#annotators = [first] + [second]

#print(combine_annotators(annotators))

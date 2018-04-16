import fnmatch
import argparse
import re
import csv
from tqdm import tqdm
from collections import namedtuple
from os import walk
from os.path import join, basename, splitext

Annotation = namedtuple('Annotation', ['start', 'stop', 'label'])


def _find_projects(folder):
    globexpression = '*'
    reg_expr = re.compile(fnmatch.translate(globexpression), re.IGNORECASE)
    txts = []
    for root, dirs, files in walk(folder, topdown=True):
        txts += [join(root, j) for j in files if re.match(reg_expr, j)]
    return txts


def get_session(filename):
    session_regex = r'(B|S)\d{3}_(T|R)\d{2}R{0,1}'
    session = re.search(session_regex, filename).group(0)
    return session


def get_annotator(filename):
    session = get_session(filename)
    tier_regex = r'Tier\d_'
    filename = re.sub(tier_regex, '', filename)
    filename = filename.replace(session, '')
    filename = filename.replace('_', '')
    annotator = splitext(filename)[0]
    return annotator


def insert(annotations, start, stop, label):
    if not annotations:
        annotations = [Annotation(start, stop, label)]
        return annotations
    for i, annotation in enumerate(annotations):

        if annotation.start > start and annotation.stop > stop:
            annotations.insert(i, Annotation(start, stop, label))
            return annotations
        elif annotation.start < start and annotation.stop == stop:
            annotations.insert(i, Annotation(annotation.start, start, annotation.label))
            new_label = annotation.label + '; ' + label
            annotations[i+1] = Annotation(start, stop, new_label)
            return annotations
        elif annotation.start < start and annotation.stop > stop:
            annotations.insert(i, Annotation(annotation.start, start, annotation.label))
            new_label = annotation.label + '; ' + label
            annotations[i+1] = Annotation(start, stop, new_label)
            annotations.insert(i + 2, Annotation(stop, annotation.stop, annotation.label))
            return annotations
        elif annotation.start == start and annotation.stop == stop:
            new_label = annotation.label + '; ' + label
            annotations[i] = Annotation(start, stop, new_label)
            return annotations
        elif annotation.start == start and annotation.stop > stop:
            new_label = annotation.label + '; ' + label
            annotations[i+1] = Annotation(start, stop, new_label)
            annotations.insert(i + 2, Annotation(stop, annotation.stop, annotation.label))
            return annotations
        elif annotation.start > start and annotation.stop < stop:
            annotations.insert(i, Annotation(start, annotation.start, label))
            new_label = annotation.label + '; ' + label
            annotations[i+1] = Annotation(annotation.start, annotation.stop, new_label)
            annotations.insert(i + 2, Annotation(annotation.stop, stop, label))
            return annotations
        elif annotation.start > start and annotation.stop == stop:
            annotations.insert(i, Annotation(start, annotation.start, label))
            new_label = annotation.label + '; ' + label
            annotations[i+1] = Annotation(annotation.start, annotation.stop, new_label)
            return annotations
        elif annotation.start == start and annotation.stop < stop:
            new_label = annotation.label + '; ' + label
            annotations[i+1] = Annotation(annotation.start, annotation.stop, new_label)
            annotations.insert(i + 2, Annotation(annotation.stop, stop, label))
            return annotations
    annotations.append(Annotation(start, stop, label))
    return annotations


def combine(folder, outfolder):
    filenames = _find_projects(folder)
    sessions = dict()
    for filename in filenames:
        session = get_session(basename(filename))
        if session in sessions:
            sessions[session] += [filename]
        else:
            sessions[session] = [filename]
    for session in tqdm(sessions):
        with open(join(outfolder, session + '.csv'), 'w', newline='') as o:
            writer = csv.writer(o, delimiter='\t')
            annotations = list()
            for file in sessions[session]:
                annotator = get_annotator(basename(file))
                with open(file, 'r') as f:
                    reader = csv.reader(f, delimiter='\t')
                    for line in reader:
                        start = float(line[0])
                        stop = float(line[1])
                        label = annotator + ': ' + line[2]
                        annotations = insert(annotations, start, stop, label)
            for annotation in annotations:
                writer.writerow(annotation)



def main():
    parser = argparse.ArgumentParser(description='Combine tier 3 annotations of different annotators.')
    parser.add_argument('folder', help='folder containing projects to be combined')
    parser.add_argument('outfolder', help='folder containing combined projects')
    args = vars(parser.parse_args())
    combine(args['folder'], args['outfolder'])


if __name__ == '__main__':
    main()

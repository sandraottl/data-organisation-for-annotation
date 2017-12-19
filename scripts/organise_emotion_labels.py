import csv
from os.path import splitext
import argparse
import pandas as pd
import numpy as np
from tqdm import tqdm
import re


def check(first_file, second_file, outfile):
    with open(first_file, 'r') as first, open(second_file, 'r') as second, open(outfile, 'w', newline='') as outfile:
        reader_first = csv.reader(first, delimiter=';')
        reader_second = csv.reader(second, delimiter=';')
        writer = csv.writer(outfile, delimiter=';')
        for line in reader_first:
            #line[1] = splitext(line[1])[0]
            line = ','.join(line)
            if not (line in map(','.join, reader_second)):
                writer.writerow(line.split(','))


def remove_duplicates(file, outfile):
    with open(file, 'r') as file, open(outfile, 'w', newline='') as outfile:
        writer = csv.writer(outfile, delimiter=';')
        writer.writerow(('UserID', 'AudioData', 'Answer', 'RemovedNeutral'))
        df = pd.read_csv(file, delimiter=';')
        df = df.drop_duplicates()
        user_ids = sorted(set(df['UserID']))
        neutrals_removed = 0
        for user_id in user_ids:
            user_frame = mask(df, 'UserID', [user_id])
            audio_data = sorted(set(user_frame['AudioData']))
            for data in audio_data:
                audio_data_frame = mask(user_frame, 'AudioData', [data])
                shape_before_removal = audio_data_frame.shape[0] 
                if shape_before_removal > 1:
                    audio_data_frame = audio_data_frame[audio_data_frame['Answer'] != 'neutral']
                audio_data_list = audio_data_frame.values.tolist()
                removed_neutral = shape_before_removal > audio_data_frame.shape[0]
                if removed_neutral:
                    neutrals_removed += 1
                    print('Removed {} neutral answers.'.format(neutrals_removed))
                for d in audio_data_list:
                    d.append(removed_neutral)
                    writer.writerow(d)


def mask(df, column, values):
    mask = np.in1d(df[column].values, values)
    return df[mask]


def correct_filenames(old_file, map_file, outfile, missing):
    with open(old_file, 'r') as old_file, open(map_file, 'r', encoding='utf-8') as map_file, open(outfile, 'a', newline='') as outfile, open(missing, 'a', newline='') as missing:
        reader_old = csv.reader(old_file, delimiter=';')
        writer_out = csv.writer(outfile, delimiter=';')
        writer_missing = csv.writer(missing, delimiter=';')
        for line in tqdm(reader_old):
            name = splitext(line[2])[0].split('/')[1]
            #print(name)
            found_match = False
            reader_map = csv.reader(map_file, delimiter=';')
            for line_map in reader_map:
                if (name.strip() == splitext(line_map[0])[0].strip()):
                    writer_out.writerow((line[0], line_map[1], line[3]))
                    found_match = True
            if not found_match:
                writer_missing.writerow(line)
            map_file.seek(0)


def merge_files(infile, outfile):
    with open(infile, 'r') as infile, open(outfile, 'a', newline='') as outfile:
        reader = csv.reader(infile, delimiter=';')
        writer = csv.writer(outfile, delimiter=';')
        next(reader)
        for line in reader:
            line[2] = splitext(line[2])[0]
            writer.writerow(line)


def rename_lines(infile, outfile, remaining):
    with open(infile, 'r') as infile, open(outfile, 'w', newline='') as outfile, open(remaining, 'w', newline='') as remaining:
        reader = csv.reader(infile, delimiter=';')
        writer_out = csv.writer(outfile, delimiter=';')
        writer_remaining = csv.writer(remaining, delimiter=';')
        next(reader)
        prob_regex = r'Prob(.){2}'
        gender_regex = r'_(m|f)_'
        filename_regex = r'\d{3}'
        for line in reader:
            old_name = line[2]
            prob = re.search(prob_regex, old_name)
            gender = re.search(gender_regex, old_name)
            filename = re.search(filename_regex, old_name)
            if prob and gender and filename:
                new_name = '_'.join((gender.group(1), prob.group(0), 'Games', filename.group(0)))
                writer_out.writerow((line[0], new_name, line[3]))
            else:
                writer_remaining.writerow(line)


def convert(label):
    labels = ['neutral', 'fear', 'anger', 'sadness', 'surprise', 'happiness', 'disgust']
    arousal_w = [0, 0.8, 0.8, -0.4, 0.9, 0.15, 0.5]
    valence_w = [0, -0.2, -0.4, -0.8, 0.1, 0.95, -0.65]
    if label not in labels:
        return 'unsupported emotion', 'unsupported emotion'
    ind = labels.index(label)
    arousal = arousal_w[ind]
    valence = valence_w[ind]
    return arousal, valence


def append_arousal_valance(infile, outfile):
    with open(infile, 'r') as infile, open(outfile, 'w', newline='') as outfile:
        reader = csv.reader(infile, delimiter=';')
        writer = csv.writer(outfile, delimiter=';')
        writer.writerow(next(reader) + ['Arousal', 'Valence'])
        for line in reader:
            arousal_valence = convert(line[2])
            line += arousal_valence
            writer.writerow(line)


def count_file_instances(infile, outfile):
    with open(infile, 'r') as infile, open(outfile, 'w', newline='') as outfile:
        reader = csv.reader(infile, delimiter=';')
        writer = csv.writer(outfile, delimiter=';')
        writer.writerow(['Proband', 'Task', 'Instances'])
        data_dict = {}
        prob_regex = r'Prob(.){2}'
        task_regex = r'(Games|Pictures|Story|Question)'
        for line in reader:
            name = line[1]
            prob = re.search(prob_regex, name)
            task = re.search(task_regex, name)
            prob_name = prob.group(0)
            task_name = task.group(0)
            if prob_name in data_dict:
                if task_name in data_dict[prob_name]:
                    data_dict[prob_name][task_name] += 1
                else:
                    data_dict[prob_name][task_name] = 1
            else:
                data_dict[prob_name] = {}
                data_dict[prob_name][task_name] = 1
        for pn in data_dict:
            for t in data_dict[pn]:
                writer.writerow([pn, t, data_dict[pn][t]])


def count_instances(infile, outfile):
    with open(infile, 'r') as infile, open(outfile, 'w', newline='') as outfile:
        reader = csv.reader(infile, delimiter=';')
        writer = csv.writer(outfile, delimiter=';')
        writer.writerow(['Proband', 'Task', 'Instances'])
        data_dict = {}
        prob_regex = r'Prob(.){2}'
        task_regex = r'(Games|Pictures|Story|Question)'
        for line in reader:
            name = line[1]
            prob = re.search(prob_regex, name)
            task = re.search(task_regex, name)
            prob_name = prob.group(0)
            task_name = task.group(0)
            if prob_name in data_dict:
                if task_name in data_dict[prob_name]:
                    data_dict[prob_name][task_name].add(name)
                else:
                    data_dict[prob_name][task_name] = set()
            else:
                data_dict[prob_name] = {}
                data_dict[prob_name][task_name] = set()
        for pn in data_dict:
            for t in data_dict[pn]:
                writer.writerow([pn, t, len(data_dict[pn][t])])


def main_check():
    parser = argparse.ArgumentParser(description='Write all lines that are in the first file but not in the second file into the third file.')
    parser.add_argument('first_file', help='first file (containing lines to check if they are in the second file)')
    parser.add_argument('second_file', help='second file')
    parser.add_argument('outfile', help='destination for lines that are not in the second file but in the first file')
    args = vars(parser.parse_args())
    check(args['first_file'], args['second_file'], args['outfile'])


def main_remove_duplicates():  # _remove_duplicates
    parser = argparse.ArgumentParser(description='Remove all duplicates.')
    parser.add_argument('file', help='file')
    parser.add_argument('outfile', help='destination for file without duplicates')
    args = vars(parser.parse_args())
    remove_duplicates(args['file'], args['outfile'])


def main_correct_filenames():  # 
    parser = argparse.ArgumentParser(description='Find the correct names of the old file using the map file and write those into the outfile. If no new name can be found in the map file, this line is written into a file containing the missing names.')
    parser.add_argument('old_file', help='file containing names to be changed')
    parser.add_argument('map_file', help='file containing correct names for old names')
    parser.add_argument('outfile', help='destination for lines containg the correct name')
    parser.add_argument('missing', help='destination for lines of names that are not in the map file')
    args = vars(parser.parse_args())
    correct_filenames(args['old_file'], args['map_file'], args['outfile'], args['missing'])


def main_merge_files():  # _merge_files
    parser = argparse.ArgumentParser(description='Appends first file to second file.')
    parser.add_argument('infile', help='file to be appended')
    parser.add_argument('outfile', help='file to that the other file is appended')
    args = vars(parser.parse_args())
    merge_files(args['infile'], args['outfile'])


def main_rename_lines():  # 
    parser = argparse.ArgumentParser(description='Appends renamed lines of first file to second file nad write other ones in third file.')
    parser.add_argument('infile', help='lines to be renamed')
    parser.add_argument('outfile', help='file to that the renamed lines are appended')
    parser.add_argument('remaining', help='file to that the not renamed lines are appended')
    args = vars(parser.parse_args())
    rename_lines(args['infile'], args['outfile'], args['remaining'])


def main_append_arousal_valence():  # 
    parser = argparse.ArgumentParser(description='Appends arousal and valence values.')
    parser.add_argument('infile', help='file to be changed')
    parser.add_argument('outfile', help='file with arousal and valence values')
    args = vars(parser.parse_args())
    append_arousal_valance(args['infile'], args['outfile'])


def main():  # 
    parser = argparse.ArgumentParser(description='Create table with counted instances.')
    parser.add_argument('infile', help='file to be counted')
    parser.add_argument('outfile', help='file obtaining counted instances per proband and task')
    args = vars(parser.parse_args())
    # count_file_instances(args['infile'], args['outfile'])
    count_instances(args['infile'], args['outfile'])


if __name__ == '__main__':
    main()

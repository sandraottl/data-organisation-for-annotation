import soundfile as sf
from os.path import join, isdir, basename, abspath, isfile
from os import listdir
import csv
import shutil
import argparse
import xml.etree.ElementTree as ET


#INPUT_PATH = 'U:\SandraOttl\de-enigma/timestamp-task/belgrade_1\S001_R01'
ns = {'ns0': 'http://audacity.sourceforge.net/xml/'}

def get_wav_length(wav_file):
    data, samplerate = sf.read(wav_file)
    length = len(data) / samplerate
    return length


def get_timestamp_length(timestamp_file):
    with open(timestamp_file, newline='') as file:
        reader = csv.reader(file, delimiter=';')
        first_line = next(reader)
        for line in reader:
            pass
        last_line = line
    start_time = first_line[0]
    stop_time = last_line[0]
    timestamp_length = (int(stop_time) - int(start_time)) / 10**7
    return timestamp_length


def get_audacity_length(aud_file):
    tree = ET.parse(aud_file)
    root = tree.getroot()
    wavetrack = root.find('ns0:wavetrack', ns)
    sampling_rate = int(wavetrack.attrib['rate'])
    sequence = wavetrack.find('ns0:waveclip', ns).find('ns0:sequence', ns)
    sample_no = int(sequence.attrib['numsamples'])
    return sample_no / sampling_rate

def find_audacity_projects(path):
    audacity_projects = [join(path, project) for project in listdir(path) if project.endswith('.aup') and isfile(join(path, project))]
    sub_dirs = [join(path, directory) for directory in listdir(path) if isdir(join(path, directory))]
    for sub_dir in sub_dirs:
        audacity_projects += find_audacity_projects(sub_dir)
    return audacity_projects

def main():
    parser = argparse.ArgumentParser(description='Find correct timestamp file for project folder.')
    parser.add_argument('folder', help='project folder')
    
    args = vars(parser.parse_args())
    INPUT_PATH = abspath(args['folder'])
    ns = {'ns0': 'http://audacity.sourceforge.net/xml/'}


    file_list = [join(INPUT_PATH, file) for file in listdir(INPUT_PATH) if file.startswith('file') and file.endswith('.txt')]
    length_dict = {file_name: get_timestamp_length(file_name) for file_name in file_list}
    with open(join(INPUT_PATH, 'lengths.txt'), 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        for k,v in length_dict.items():
            writer.writerow([k,v])

    audacity_length = get_audacity_length(find_audacity_projects(INPUT_PATH)[0])
    print('Audacity length: {}'.format(str(audacity_length)))
    with open(join(INPUT_PATH, 'lengths.txt'), 'r', newline='') as file:
        reader = csv.reader(file, delimiter=';')
        first_line = next(reader)
        difference = abs(float(first_line[1]) - audacity_length)
        closest_match = first_line[0]
        for line in reader:
            new_difference = abs(float(line[1]) - audacity_length)
            if new_difference < difference:
                difference = new_difference
                closest_match = line[0]

        if difference <= 2:
            shutil.copyfile(closest_match, join(INPUT_PATH, basename(INPUT_PATH)+'_timestamps.txt'))
            print(INPUT_PATH+': found matching timestamp file. Length difference: {}s'.format(str(difference)))
        else:
            print(INPUT_PATH+': needs manual timestamp matching.')

if __name__ == '__main__':
   main()


#print(get_timestamp_length('U:\SandraOttl\de-enigma/timestamp-task/belgrade_1\S001_R01/file5874.txt'))
import xml.etree.ElementTree as ET
import csv
import argparse
from os.path import join
from os import listdir

ns = {'aud': "http://audacity.sourceforge.net/xml/"}


def calc_offset(elan_timestamps, audacity_timestamps):
    with open(elan_timestamps) as elan:
        reader = csv.reader(elan, delimiter=',')
        # skip header
        next(reader)
        elan_timestamp = float(next(reader)[2])
    with open(audacity_timestamps) as aud:
        reader = csv.reader(aud, delimiter=';')
        audacity_timestamp = float(next(reader)[0])
    offset = (-1) * ((elan_timestamp - audacity_timestamp) / 10000)  # ms
    return int(offset)  # audacity-elan


def shift_labels(elan, audacity_folder, offset):
    audacity = join(audacity_folder, 'audacity_goldstandard_S059_T02.txt')  # audacity_labels
    with open(elan, 'r', newline='') as el, open(audacity, 'w', newline='', encoding='utf-8') as aud:
        reader = csv.reader(el, delimiter='\t')
        writer = csv.writer(aud, delimiter='\t')
        counter = 0
        for line in reader:
            counter += 1
            start = int(float(line[0]) * 1000) - offset
            stop = int(float(line[1]) * 1000) - offset
            label = line[2]
            writer.writerow((start, stop, label))
        return counter


def shift_labels_2(elan, child, session, offset):
    audacity = 'Y:\SandraOttl\de-enigma/annotations\de-enigma_audio_annotation_package/british/time_alligned_uau/tier_0_diarisation/B0' + child + '/audacity_labels_B0' + child + '_' + session + '.txt'  # audacity_labels_location
    with open(elan, 'r', newline='') as el, open(audacity, 'w', newline='', encoding='utf-8') as aud:
        reader = csv.reader(el, delimiter='\t')
        writer = csv.writer(aud, delimiter='\t')
        counter = 0
        for line in reader:
            counter += 1
            start = (int(float(line[0]) * 1000) - int(float(offset) * 1000)) / 1000
            stop = (int(float(line[1]) * 1000) - int(float(offset) * 1000)) / 1000
            label = line[2]
            writer.writerow((start, stop, label))
        return counter


def insert_elan_annotations_into_audacity(audacity_folder, counter):
    audacity_project_path = [join(audacity_folder, file) for file in listdir(audacity_folder) if file.endswith('.aup')][0]
    audacity_label_file_path = join(audacity_folder, 'audacity_goldstandard_S022_T01.txt')  # audacity_labels
    with open(audacity_label_file_path, 'r', encoding='utf-8') as labels:
        reader = csv.reader(labels, delimiter='\t')
        ET.register_namespace('', 'http://audacity.sourceforge.net/xml/')
        tree = ET.parse(audacity_project_path)
        root = tree.getroot()
        labeltrack = ET.SubElement(root, 'labeltrack', attrib={'name': 'Label Track', 'numlabels': str(counter), 'height': '250', 'minimized': '0', 'isSelected': '1'})
        for line in reader:
            label = line[2]
            start_time = max(0, int(line[0]) / 1000)
            stop_time = max(0, int(line[1]) / 1000)
            if not (start_time == 0 and stop_time == 0):
                ET.SubElement(labeltrack, 'label', attrib={'t': str(start_time), 't1': str(stop_time), 'title': str(label)})
        tree.write(audacity_project_path, encoding='utf-8', xml_declaration=True)


def main():
    parser = argparse.ArgumentParser(description='Insert elan gold standard labels into an existing audacity.')
    parser.add_argument('elan', help='elan annotations file (gold standard)')
    parser.add_argument('audacity_folder', help='folder containing existing audacity project')
    parser.add_argument('elan_timestamps', help='elan timestamps')
    parser.add_argument('audacity_timestamps', help='audacity timestamps')
    args = vars(parser.parse_args())
    offset = calc_offset(args['elan_timestamps'], args['audacity_timestamps'])
    #counter = shift_labels(args['elan'], args['audacity_folder'], offset)
    print('created audacity labels file')
    #insert_elan_annotations_into_audacity(args['audacity_folder'], counter)
    #print('done')


def main_with_offset():
    parser = argparse.ArgumentParser(description='Insert elan gold standard labels into an existing audacity.')
    parser.add_argument('elan', help='elan annotations file')
    parser.add_argument('child', help='existing audacity project (two digits)')
    parser.add_argument('session', help='existing audacity project (two digits)')
    parser.add_argument('offsetElan', help='offset of elan')
    parser.add_argument('offsetAud', help='offset of audacity')
    args = vars(parser.parse_args())
    offset = float(args['offsetElan']) - float(args['offsetAud'])
    counter = shift_labels_2(args['elan'], args['child'], args['session'], offset)
    print('created audacity labels file')
    #insert_elan_annotations_into_audacity(args['audacity_folder'], counter)
    #print('done')


if __name__ == '__main__':
    main_with_offset()

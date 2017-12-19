import xml.etree.ElementTree as ET
from os import listdir
from os.path import join
import argparse
import csv
from tqdm import tqdm
#from utils import find_by_glob
#from tqdm import tqdm

cv_map_child = {'c': {'text': 'child', 'cv_id': 'cveid0'}, 't': {'text': 'therapist', 'cv_id': 'cveid2'}, 'a': {'text': 'adult', 'cv_id': 'cveid4'}, 'z': {'text': 'Zeno', 'cv_id': 'cveid20'}, '1': {'text': 'child+therapist', 'cv_id': 'cveid1'}, '2': {'text': 'child+adult', 'cv_id': 'cveid3'}, '3': {'text': 'child+zeno', 'cv_id': 'cveid5'}, '4': {'text': 'therapist+adult', 'cv_id': 'cveid10'}, '5': {'text': 'therapist+zeno', 'cv_id': 'cveid15'}, '6': {'text': 'adult+zeno', 'cv_id': 'cveid16'}, '7': {'text': '2+', 'cv_id': 'cveid6'}}
cv_map_AV = {'-1': {'text': '-1', 'cv_id': 'cveid0'}, '-0.5': {'text': '-0.5', 'cv_id': 'cveid4'}, '0': {'text': '0', 'cv_id': 'cveid6'}, '0.5': {'text': '0.5', 'cv_id': 'cveid9'}, '1': {'text': '1', 'cv_id': 'cveid11'}}
# cv_map_1 = {'speech': {'text': 'speech', 'cv_id': 'cveid0'}, 'non-speech': {'text': 'non-speech', 'cv_id': 'cveid2'}, 'speech-like': {'text': 'speech-like', 'cv_id': 'cveid1'}, 'shouting': {'text': 'shouting', 'cv_id': 'cveid4'}, 'unsure': {'text': 'unsure', 'cv_id': 'cveid3'}}
cv_map_1 = {'speech': {'text': 'speech', 'cv_id': 'cveid0'}, 'non-speech': {'text': 'non-speech', 'cv_id': 'cveid2'}, 'speech-like': {'text': 'speech-like', 'cv_id': 'cveid1'}, 'shouting (speech)': {'text': 'shouting (speech)', 'cv_id': 'cveid4'}, 'shouting (non-speech)': {'text': 'shouting (non-speech)', 'cv_id': 'cveid3'}, 'shouting (speech-like)': {'text': 'shouting (speech-like)', 'cv_id': 'cveid11'}, 'unsure': {'text': 'unsure', 'cv_id': 'cveid7'}}
cv_map_2 = {'echolalia (immediate)': {'text': 'echolalia (immediate)', 'cv_id': 'cveid0'}, 'echolalia (delayed)': {'text': 'echolalia (delayed)', 'cv_id': 'cveid9'}, 'Another ASC Vocal Behaviour': {'text': 'Another ASC Vocal Behaviour', 'cv_id': 'cveid1'}, 'irregualr intonation': {'text': 'irregualr intonation', 'cv_id': 'cveid2'}, 'not specific to ASC': {'text': 'not specific to ASC', 'cv_id': 'cveid8'}, 'unsure (echolalia)': {'text': 'unsure (echolalia)', 'cv_id': 'cveid5'}, 'unsure (ASC behaviour)': {'text': 'unsure (ASC behaviour)', 'cv_id': 'cveid7'}}


def create_dict(el_tree, tier_name):
    root = el_tree.getroot()
    controlled_vocabulary = [cv for cv in root.findall('CONTROLLED_VOCABULARY') if cv.get('CV_ID').startswith(tier_name)][0]
    cv_dict = {}
    for cv_entry in controlled_vocabulary.findall('CV_ENTRY_ML'):
        value = cv_entry.get('CVE_ID')
        key = cv_entry[0].text
        cv_dict[key] = value
    return cv_dict




def calc_offset(video, audio):
    with open(video, newline='') as vid:
        reader = csv.reader(vid, delimiter=',')
        # skip header
        next(reader)
        video_timestamp = float(next(reader)[3])
    with open(audio, newline='') as aud:
        reader = csv.reader(aud, delimiter=';')
        audio_timestamp = float(next(reader)[0])
    offset = (video_timestamp - audio_timestamp) / 10000  # ms
    return offset


def insert_audacity_annotations_into_elan_deprecated(audacity, elan, tier_name, offset):
    # next line for gold standard
    tier_name = 'Tier ' + tier_name
    with open(audacity, 'r') as aud:
        reader_aud = csv.reader(aud, delimiter=';')  # sometimes \t
        tree = ET.parse(elan)
        root = tree.getroot()
        for line in reader_aud:
            label = line[2]
            start_time = max(0, int(float(line[0]) * 1000 - offset))
            stop_time = max(0, int(float(line[1]) * 1000 - offset))
            if not (start_time==0 and stop_time==0):
                time_order = root.find('TIME_ORDER')
                num_time_stamps = len(list(time_order))
                ts1 = 'ts' + str(num_time_stamps + 1)
                ts2 = 'ts' + str(num_time_stamps + 2)
                ET.SubElement(time_order, 'TIME_SLOT', attrib={'TIME_SLOT_ID': ts1, 'TIME_VALUE': str(start_time)})
                ET.SubElement(time_order, 'TIME_SLOT', attrib={'TIME_SLOT_ID': ts2, 'TIME_VALUE': str(stop_time)})
                if (tier_name == 'Tier 4') or (tier_name == 'Tier 5'):
                    cv_map = cv_map_AV
                elif (tier_name == 'Tier 1'):
                    cv_map = cv_map_1
                elif (tier_name == 'Tier 2'):
                    cv_map = cv_map_2
                else:
                    cv_map = cv_map_child
                tier = [tier for tier in root.findall('TIER') if tier.attrib['TIER_ID'].startswith(tier_name)][0]
                num_annotations = len(list(tier))
                annotation = ET.SubElement(tier, 'ANNOTATION')
                alignable_annotation = ET.SubElement(annotation, 'ALIGNABLE_ANNOTATION', attrib={'ANNOTATION_ID': 'a' + str(num_annotations + 1), 'CVE_REF': cv_map[label]['cv_id'], 'TIME_SLOT_REF1': ts1, 'TIME_SLOT_REF2': ts2})  # cv_map
                annotation_value = ET.SubElement(alignable_annotation, 'ANNOTATION_VALUE')
                annotation_value.text = cv_map[label]['text']  # cv_map
        tree.write(elan, encoding='utf-8', xml_declaration=True)

def insert_audacity_annotations_into_elan(audacity, elan, tier_name, offset):
    # next line for gold standard
    tier_name = 'Tier ' + tier_name
    with open(audacity, 'r') as aud:
        reader_aud = csv.reader(aud, delimiter=';')  # sometimes \t
        tree = ET.parse(elan)
        cv_map = create_dict(tree, tier_name)
        root = tree.getroot()
        for line in reader_aud:
            label = line[2]
            start_time = max(0, int(float(line[0]) * 1000 - offset))
            stop_time = max(0, int(float(line[1]) * 1000 - offset))
            if not (start_time==0 and stop_time==0):
                time_order = root.find('TIME_ORDER')
                num_time_stamps = len(list(time_order))
                ts1 = 'ts' + str(num_time_stamps + 1)
                ts2 = 'ts' + str(num_time_stamps + 2)
                ET.SubElement(time_order, 'TIME_SLOT', attrib={'TIME_SLOT_ID': ts1, 'TIME_VALUE': str(start_time)})
                ET.SubElement(time_order, 'TIME_SLOT', attrib={'TIME_SLOT_ID': ts2, 'TIME_VALUE': str(stop_time)})
                tier = [tier for tier in root.findall('TIER') if tier.attrib['TIER_ID'].startswith(tier_name)][0]
                num_annotations = len(list(tier))
                annotation = ET.SubElement(tier, 'ANNOTATION')
                alignable_annotation = ET.SubElement(annotation, 'ALIGNABLE_ANNOTATION', attrib={'ANNOTATION_ID': 'a' + str(num_annotations + 1), 'CVE_REF': cv_map[label], 'TIME_SLOT_REF1': ts1, 'TIME_SLOT_REF2': ts2})  # cv_map
                annotation_value = ET.SubElement(alignable_annotation, 'ANNOTATION_VALUE')
                annotation_value.text = label  # cv_map
        tree.write(elan, encoding='utf-8', xml_declaration=True)


def delete_labels_of_tier(elan, tier_name):
    tier_name = 'Tier ' + str(tier_name)
    tree = ET.parse(elan)
    root = tree.getroot()
    tier = [tier for tier in root.findall('TIER') if tier.get('TIER_ID').startswith(tier_name)][0]
    for element in list(tier):
        tier.remove(element)
    tree.write(elan, encoding='utf-8', xml_declaration=True)



def main_insert_aud_in_elan():
    parser = argparse.ArgumentParser(description='Insert audacity labels into an existing elan file on a specific tier.')
    parser.add_argument('audacity', help='file containing audacity labels')
    parser.add_argument('-audacity_timestamps', help='file containing timestamps of audacity file', default=None)
    parser.add_argument('elan', help='existing elan file')
    parser.add_argument('-elan_timestamps', help='file containing timestamps of elan file', default=None)
    parser.add_argument('-tier', help='specific tier in the elan file on which to insert the audacity labels', default='Tier 0')

    args = vars(parser.parse_args())
    if args['elan_timestamps'] and args['audacity_timestamps']:
    	offset = calc_offset(args['elan_timestamps'], args['audacity_timestamps'])
    else: offset = 0
    insert_audacity_annotations_into_elan(args['audacity'], args['elan'], args['tier'], offset)


def main_insert_gold_standard():
    parser = argparse.ArgumentParser(description='Insert elan gold standard labels into an existing elan file on a specific tier.')
    parser.add_argument('audacity', help='elan annotations file (gold standard)')
    parser.add_argument('elan', help='existing elan file')
    parser.add_argument('tier', help='specific tier in the elan file on which to insert the audacity labels')
    args = vars(parser.parse_args())
    delete_labels_of_tier(args['elan'], args['tier'])
    print('deleted all labels of tier ' + args['tier'])
    offset = 0
    insert_audacity_annotations_into_elan(args['audacity'], args['elan'], args['tier'], offset)


def main_batch_insert_gold_standard():
    parser = argparse.ArgumentParser(description='Insert elan gold standard labels into an existing elan file on a specific tier.')
    parser.add_argument('audacity', help='folder with elan annotations file (gold standard)')
    parser.add_argument('elan', help='folder with existing elan files')
    parser.add_argument('tier', help='specific tier in the elan file on which to insert the audacity labels')
    args = vars(parser.parse_args())
    eafs = sorted([join(args['elan'], file) for file in listdir(args['elan']) if file.endswith('.eaf')])
    csvs = sorted([join(args['audacity'], file) for file in listdir(args['audacity']) if file.endswith('.csv')])
    for csv, elan in tqdm(zip(csvs,eafs)):
        delete_labels_of_tier(elan, args['tier'])
        print('deleted all labels of tier ' + args['tier'])
        offset = 0
        insert_audacity_annotations_into_elan(csv, elan, args['tier'], offset)


if __name__ == '__main__':
    main_batch_insert_gold_standard()
import xml.etree.ElementTree as ET
import argparse
import csv

cv_map = {'c': {'text': 'child', 'cv_id': 'cveid0'}, 't': {'text': 'therapist', 'cv_id': 'cveid2'}, 'a': {'text': 'adult', 'cv_id': 'cveid4'}, 'z': {'text': 'Zeno', 'cv_id': 'cveid20'}, '1': {'text': 'child+therapist', 'cv_id': 'cveid1'}, '2': {'text': 'child+adult', 'cv_id': 'cveid3'}, '3': {'text': 'child+zeno', 'cv_id': 'cveid5'}, '4': {'text': 'therapist+adult', 'cv_id': 'cveid10'}, '5': {'text': 'therapist+zeno', 'cv_id': 'cveid15'}, '6': {'text': 'adult+zeno', 'cv_id': 'cveid16'}, '7': {'text': '2+', 'cv_id': 'cveid6'}}


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


def insert_audacity_annotations_into_elan(audacity, elan, tier_name, offset):
    with open(audacity, 'r') as aud:
        tree = ET.parse(elan)
        root = tree.getroot()
        for line in aud:
            args = line.split("\t")
            label = args[2].strip()
            start_time = max(0, int(float(args[0]) * 1000 - offset))
            stop_time = max(0, int(float(args[1]) * 1000 - offset))
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
                alignable_annotation = ET.SubElement(annotation, 'ALIGNABLE_ANNOTATION', attrib={'ANNOTATION_ID': 'a' + str(num_annotations + 1), 'CVE_REF': cv_map[label]['cv_id'], 'TIME_SLOT_REF1': ts1, 'TIME_SLOT_REF2': ts2})
                annotation_value = ET.SubElement(alignable_annotation, 'ANNOTATION_VALUE')
                annotation_value.text = cv_map[label]['text']
        tree.write(elan)

def main():
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


if __name__ == '__main__':
    main()
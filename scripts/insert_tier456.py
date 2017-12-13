import xml.etree.ElementTree as ET
import argparse
from utils import find_by_glob
from os.path import splitext
from shutil import copy
from tqdm import tqdm


# cv_map_AV = {'-1': {'text': '-1', 'cv_id': 'cveid0'}, '-0.5': {'text': '-0.5', 'cv_id': 'cveid4'}, '0': {'text': '0', 'cv_id': 'cveid6'}, '0.5': {'text': '0.5', 'cv_id': 'cveid9'}, '1': {'text': '1', 'cv_id': 'cveid11'}}
# cv_map_6 = {'L': {'text': 'laugh', 'cv_id': 'cveid0'}, 'C': {'text': 'cry', 'cv_id': 'cveid2'}, }


def insert_tiers(source, target):
    tree = ET.parse(source)
    root = tree.getroot()
    target_tree = ET.parse(target)
    target_root = target_tree.getroot()
    for element in root:
        matching_elements = target_root.findall(element.tag)
        insert_location = list(target_root).index(matching_elements[-1]) + 1
        target_root.insert(insert_location, element)
    #cv2 = [cv for cv in target_root.findall('CONTROLLED_VOCABULARY') if cv.get('CV_ID').startswith('Tier 2')][0]
    #cv_entry = [entry for entry in cv2.findall('CV_ENTRY_ML') if entry.get('CVE_ID') == 'cveid3'][0]
    #description = cv_entry[0]
    #description.set('DESCRIPTION', '9 - Unsure how to categorise this label - possible ASC behaviour')
    target_tree.write(target, encoding='utf-8', xml_declaration=True)
    pfsx_path = splitext(target)[0] + '.pfsx'
    copy('pfsx.pfsx', pfsx_path)


def main():
    parser = argparse.ArgumentParser(description='Inserts tier 4,5 and 6 into an existing elan project.')
    parser.add_argument('source', help='file containing to be inserted controlled vocabulary and tiers')
    parser.add_argument('folder', help='folder with project files containing all tiers')
    args = vars(parser.parse_args())
    for eaf in tqdm(find_by_glob('*.eaf', args['folder'])):
        insert_tiers(args['source'], eaf)


if __name__ == '__main__':
    main()

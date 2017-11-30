import soundfile as sf
import re
from os.path import join, isdir, basename, abspath, isfile
from os import listdir
import csv
import shutil
import argparse
import xml.etree.ElementTree as ET

ns = {'ns0': 'http://audacity.sourceforge.net/xml/'}


def get_timestamp_length(timestamp_file):
    with open(timestamp_file, newline='') as file:
        reader = csv.reader(file, delimiter=',')
        header = next(reader)
        timestamp_cols = [i for i, field in enumerate(header) if field.endswith('Time_Stamp')]
        first_line = next(reader)
        for line in reader:
            pass
        last_line = line
    start_time = first_line[timestamp_cols[0]]
    stop_time = last_line[timestamp_cols[0]]
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


def wav_len(file):
    info = sf.info(file)
    return info.duration

session_regexp = r'^[A-Z0-9]{3,4}_[A-Z0-9]{3}'
wav_directory = 'Y:/SandraOttl/de-enigma/ELAN/SSA/Media/Audio'
cut_path = 'Y:\SandraOttl\de-enigma/timestamps/task\ELAN-video-timestamps\Serbia/after_cut'
uncut_path = 'Y:\SandraOttl\de-enigma/timestamps/task\ELAN-video-timestamps\Serbia/before_cut'
cut_timestamps = listdir(cut_path)
uncut_timestamps = listdir(uncut_path)
with open('lens.csv', 'w') as output:
    writer = csv.writer(output)
    for wav in listdir(wav_directory):
        session_name = re.match(session_regexp, wav).group(0)
        true_len = wav_len(join(wav_directory, wav))
        cut_timestamp = [timestamp for timestamp in cut_timestamps if timestamp.startswith(session_name)]
        cut_len, uncut_len = None, None
        if cut_timestamp:
            cut_len = get_timestamp_length(join(cut_path, cut_timestamp[0]))
        
        uncut_timestamp = [timestamp for timestamp in uncut_timestamps if timestamp.startswith(session_name)]
        if uncut_timestamp:
            uncut_len = get_timestamp_length(join(uncut_path, uncut_timestamp[0]))

        line = [session_name, uncut_len, cut_len]
        if cut_len and uncut_len:
            cut = abs(cut_len-true_len) < abs(uncut_len-true_len)
        elif cut_len and not uncut_len:
            cut = True
        elif not cut_len and uncut_len:
            cut = False
        line.append(cut)
        print(line)
        writer.writerow(line)
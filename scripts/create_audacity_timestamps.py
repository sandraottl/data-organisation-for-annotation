import xml.etree.ElementTree as ET
from datetime import datetime
from os.path import splitext

#audacity = 'Y:\SandraOttl\de-enigma\missing_ts\B003_R03/Audio_2016-11-03_14-23-39.968.aup'
ns = {'aud': "http://audacity.sourceforge.net/xml/"}


def create_audacity_timestmaps(audacity):
    timestamps = splitext(audacity)[0] + '.txt'
    with open(audacity, 'r') as aud, open(timestamps, 'w') as output:
        tree = ET.parse(aud)
        root = tree.getroot()
        projname = root.get('projname')[6:-5]
        endtime = datetime.strptime(projname, '%Y-%m-%d_%H-%M-%S.%f').timestamp() * 1000  # ms
        wavetrack = root.find('aud:wavetrack', ns)
        rate = int(wavetrack.get('rate'))
        sequence = wavetrack[0][0]
        numsamples = int(sequence.get('numsamples'))
        duration = numsamples / rate * 1000  # ms
        starttime = (endtime - duration) * 10000
        output.write(starttime)


def main():
    parser = argparse.ArgumentParser(description='Create audacity timestamps from audacity project name and duration.')
    parser.add_argument('audacity', help='audacity file')

    args = vars(parser.parse_args())
    create_audacity_timestmaps(args['audacity'])


if __name__ == '__main__':
    main()
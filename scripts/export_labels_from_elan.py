import os
import argparse
import re
import fnmatch

from collections import namedtuple
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from os.path import join, dirname, splitext, relpath
from os import walk


Annotation = namedtuple("Annotation", ["start", "end", "tiers", "ANNOTATION_ID", "CVE_REF"])


def parseAnnotationsFromEafFile(eafFilepath: str) -> list:
    xmlRoot = parseXML(eafFilepath)
    timeSlots = {
        str(x.attrib["TIME_SLOT_ID"]): int(x.attrib["TIME_VALUE"])
        for x in xmlRoot.iter('TIME_SLOT')
    }
    tierAnnotations = []
    for numTier in range(4):
        for tier in xmlRoot.iter("TIER"):
            if ("Tier %d" % numTier) in tier.attrib["LINGUISTIC_TYPE_REF"]:
                tierAnnotations.append([
                    Annotation(
                        timeSlots[x.attrib["TIME_SLOT_REF1"]],
                        timeSlots[x.attrib["TIME_SLOT_REF2"]],
                        [x[0].text],
                        x.attrib["ANNOTATION_ID"],
                        x.attrib["CVE_REF"]
                    )
                    for x in tier.iter("ALIGNABLE_ANNOTATION")
                    if "CVE_REF" in x.keys()
                ])
    annotations = tierAnnotations[0]
    for tierAnnotation in tierAnnotations[1:]:
        for a in tierAnnotation:
            for b in annotations:
                if b.start == a.start and b.end == a.end:
                    b.tiers.extend(a.tiers if a.tiers else [""])
    return annotations


def parseXML(filepath: str) -> Element:
    return ElementTree.parse(filepath).getroot()


def annotationsToAudacityStr(annotations: list, tiers=[3]) -> str:
    def toStr(x: Annotation, i: int) -> str:
        return "\t".join([str(x.start / 1000.), str(x.end / 1000.), x.tiers[i]])
    return "\n".join([toStr(a, t) for a in annotations for t in tiers if t < len(a.tiers)])


def convertEafToCsv(eafFilepath: str, csvFilepath: str, annotationsToStrFunction) -> None:
    print("Converting", eafFilepath, "to", csvFilepath, "...")
    annotations = parseAnnotationsFromEafFile(eafFilepath)
    csvString = annotationsToStrFunction(annotations)
    os.makedirs(dirname(csvFilepath), exist_ok=True)
    with open(csvFilepath, "w") as f:
        f.write(csvString)


def _find_projects(folder):
    globexpression = '*.eaf'
    reg_expr = re.compile(fnmatch.translate(globexpression), re.IGNORECASE)
    # ignore_expr = '.pfsx'
    txts = []
    for root, dirs, files in walk(folder, topdown=True):
        txts += [join(root, j) for j in files if re.match(reg_expr, j)]  #  and not j.endswith(ignore_expr)
    return txts


def main():
    parser = argparse.ArgumentParser(description='Extract labels from elan projects in given folder.')
    parser.add_argument('folder', help='folder containing elan projects')
    parser.add_argument('outfolder', help='folder containing elan labels projects')
    args = vars(parser.parse_args())
    eaf_files = _find_projects(args['folder'])
    for project in eaf_files:
        output = join(args['outfolder'], splitext(relpath(project, start=args['folder']))[0] + '.csv')
        convertEafToCsv(project, output, annotationsToAudacityStr)


if __name__ == '__main__':
    main()
import re
import fnmatch
from os.path import join
from os import walk


def find_by_glob(glob, folder):
    globexpression = glob
    reg_expr = re.compile(fnmatch.translate(globexpression), re.IGNORECASE)
    elements = []
    for root, dirs, files in walk(folder, topdown=True):
        elements += [join(root, j) for j in files if re.match(reg_expr, j)]
    return elements

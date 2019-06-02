import argparse
from os.path import join
from lib.io.map import War3Map
from lib.extract_towers import extract_towers
from lib.extract_jass import extract_jass
from lib.extract_other import extract_other

JASS_FILE = 'jass.txt'
JASS_IGNORE_FILE = 'jass_ignore.txt'
TOWERS_FILE = 'tower.txt'
OTHER_FILE = 'other.txt'
OTHER_LOG_FILE = 'other_log.txt'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-oe', '--old_en')
    parser.add_argument('-oc', '--old_cn')
    parser.add_argument('-n', '--new')
    parser.add_argument('-o', '--output')

    args = parser.parse_args()
    old_en = args.old_en
    old_cn = args.old_cn
    new = args.new
    output = args.output

    old_en_map = War3Map(old_en)
    old_cn_map = War3Map(old_cn)
    new_map = War3Map(new)
    
    # towers
    extract_towers(old_en_map, old_cn_map, new_map, join(output, TOWERS_FILE))
    # jass
    extract_jass(old_en_map, old_cn_map, new_map, join(output, JASS_FILE), join(output, JASS_IGNORE_FILE))
    # others
    extract_other(old_en_map, old_cn_map, new_map, join(output, OTHER_FILE), join(output, OTHER_LOG_FILE))

import argparse
from lib.io import War3Map
from lib.io import UnitTextFile

parser = argparse.ArgumentParser()
parser.add_argument('-b','--base',type=str,help='The directory to the map.')
parser.add_argument('-i','--input',type=str,help='The input file')
args = parser.parse_args()
if not args.base:
    args.base = r'../map'
if not args.input:
    args.input = r'tl.txt'

ytd = War3Map(args.base)
txt = UnitTextFile(args.input)
for unit in txt.unit_list:
    st = ytd.unit_collection[unit.id].string_text
    print(unit.id)
    for attr in unit.attr_dict:
        print(attr)
        assert attr in st.attr_dict
        st.attr_dict[attr][1] = unit.attr_dict[attr][1]

for prefix in ytd.unit_text_file_collection:
    string, func = ytd.unit_text_file_collection[prefix]
    string.write_back()

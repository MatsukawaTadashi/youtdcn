import argparse
from lib.io import War3Map
from lib.io import UnitTextFile

parser = argparse.ArgumentParser()
# parser.add_argument('-b','--base',type=str,required=True,help='The directory to the map.')
# parser.add_argument('-i','--input',type=str,required=True,help='The input file')
args = parser.parse_args()
args.base = r'../map'
args.input = r'cn.txt'

ytd = War3Map(args.base)
txt = UnitTextFile(args.input)
for unit in txt.unit_list:
    ytd.unit_collection[unit.id].string.text = unit.text

for prefix in ytd.unit_text_file_collection:
    ytd.unit_text_file_collection[prefix][0].write_back()

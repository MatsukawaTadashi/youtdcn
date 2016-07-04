import argparse
from lib.io import map
from lib.io import unit_txt

parser = argparse.ArgumentParser()
#parser.add_argument('-b','--base',type=str,required=True,help='The directory to the map.')
#parser.add_argument('-i','--input',type=str,required=True,help='The input file')
args = parser.parse_args()
args.base = r'../map'
args.input = r'cn.txt'

ytd = map(args.base)
txt = unit_txt(args.input)
for unit in txt.units:
    ytd.unit_dict[unit.id].string.text = unit.text

for prefix in ytd.unit_txts:
    ytd.unit_txts[prefix][0].write_back()

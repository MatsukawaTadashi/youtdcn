import argparse
from replace_jass import extract_string

parser = argparse.ArgumentParser()
parser.add_argument('-b','--base',type=str,help='The directory to the map.')
parser.add_argument('-i','--input',type=str,help='The input file')
args = parser.parse_args()
if not args.base:
    args.base = r'../map/scripts/war3map.j'
if not args.input:
    args.input = r'jass_cn.txt'

with open(args.base, 'r', encoding='utf8') as ifile:
    text = ifile.read()

strs = extract_string(args.input)
assert len(strs) % 2 == 0
for i in range(len(strs) // 2):
    text = text.replace(strs[i * 2], strs[i * 2 + 1])

with open(args.base, 'w', encoding='utf8') as ofile:
    ofile.write(text)

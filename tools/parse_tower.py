import argparse
import re
import bisect
import sys
from lib.io import map

parser = argparse.ArgumentParser()
parser.add_argument('-b','--base',type=str,required=True,help='The directory to the map.')
parser.add_argument('-o','--output',type=str,help='The output file')
args = parser.parse_args()

ytd = map(args.base)

# 1. get towers from slk
# Tower has the XSEL(Sell) ability
# row 1: header;
# col 1: tower_id, col 5: tower_abil;
slk = ytd.abilities_slk
abil_dict ={}
for row in slk:
    if row == 1:
        continue
    id = slk[row][1]
    if 5 not in slk[row] or slk[row][5] == '_':
        abil = []
    else:
        abil = set(slk[row][5].split(','))
    if 'XSEL' not in abil:
        continue

    abil_dict[id] = abil

abil_cnt = {}
for id in abil_dict:
    for x in abil_dict[id]:
        abil_cnt.setdefault(x, 0)
        abil_cnt[x] += 1

basic_abilities = set([x for x in abil_cnt if abil_cnt[x] > 1])

# This will get 706 towers (include base towers) and their abilities

for id in abil_dict:
    abil_dict[id] = set([x for x in abil_dict[id] if x not in basic_abilities])

# 2. get tower's item from jass
# The bfv function register the tower with its item
item_dict = {}
bfv_list = []
r_bfv = r"bfv\('(\w{4})'.*?'(\w{4})'.*?\)"
for i, line in enumerate(ytd.jass):
    match = re.search(r_bfv, line)
    if match:
        id = match.group(1)
        item_id = match.group(2)
        item_dict[id] = item_id
        bfv_list.append(i)

# This will get 668 towers (without base towers)
base_towers = set([x for x in abil_dict if x not in item_dict])
towers = set([x for x in item_dict])

for id in base_towers:
    del abil_dict[id]


# 3. get tower's upgrade from func.txt
r_upgrade = r"Upgrade=(\w{4})"
upgrade_dict = {}
for id in towers:
    lines = ytd.unit_dict[id].func.text
    for line in lines:
        match = re.search(r_upgrade, line)
        if match:
            upgrade_id = match.group(1)
            assert(id not in upgrade_dict)
            upgrade_dict[id] = upgrade_id

# 4. get tower's buff from jass
# IIv function linked buff with its effect ability
buff_dict = {}
r_iiv = r"IIv\(.*?'\w{4}'.*?'(\w{4})'\)"

for id in towers:
    buff_dict.setdefault(id, set())

# init function list
function_list = []
r_function = r"function (\w*?) takes"
for i, line in enumerate(ytd.jass):
    match = re.search(r_function, line)
    if match:
        function_list.append(i)

# init call_dict
call_dict = {}
r_call = r"call (.*?)\("
for i, line in enumerate(ytd.jass):
    match = re.search(r_call, line)
    if match:
        function_name = match.group(1)
        call_dict.setdefault(function_name, [])
        call_dict[function_name].append(i)

# step 4 main process
cnt = 0
cnt2 = 0
for i, line in enumerate(ytd.jass):
    match = re.search(r_iiv, line)
    if not match:
        continue
    buff_id = match.group(1)
    # get function
    line_number = i
    j = bisect.bisect_left(function_list, line_number)
    if not j:
        continue
    cur_line = ytd.jass[function_list[j-1]]
    function_match = re.search(r_function, cur_line)
    if not function_match:
        continue
    function_name = function_match.group(1)

    # get call
    if function_name not in call_dict:
        continue
    assert(len(call_dict[function_name]) == 1)
    line_number = call_dict[function_name][0]
    j = bisect.bisect_left(bfv_list, line_number)
    k = bisect.bisect_left(function_list, line_number)
    if j and k and bfv_list[j - 1] > function_list[k - 1]:
        bfv_match = re.search(r_bfv, ytd.jass[bfv_list[j-1]])
        if bfv_match:
            id = bfv_match.group(1)
            buff_dict[id].add(buff_id)

# 4.5 active abil
r_rmv = "rmv\(.*?,.*?,.*?'(\w{4})'"
for i, line in enumerate(ytd.jass):
    match = re.search(r_rmv, line)
    if not match:
        continue
    abil_id = match.group(1)
    # get function
    line_number = i
    j = bisect.bisect_left(function_list, line_number)
    if not j:
        continue
    cur_line = ytd.jass[function_list[j-1]]
    function_match = re.search(r_function, cur_line)
    if not function_match:
        continue
    function_name = function_match.group(1)

    # get call
    if function_name not in call_dict:
        continue
    assert(len(call_dict[function_name]) == 1)
    line_number = call_dict[function_name][0]
    j = bisect.bisect_left(bfv_list, line_number)
    k = bisect.bisect_left(function_list, line_number)
    if j and k and bfv_list[j - 1] > function_list[k - 1]:
        bfv_match = re.search(r_bfv, ytd.jass[bfv_list[j-1]])
        if bfv_match:
            id = bfv_match.group(1)
            abil_dict[id].add(abil_id)


# step 5 output
if not args.output:
    ofile = sys.stdout
else:
    ofile = open(args.output, 'w', encoding='utf8')
towers = sorted(towers)
processed = set()
for id in towers:
    if id in processed:
        continue

    cur_id = id
    # print tower family
    while True:
        processed.add(cur_id)
        print('##Tower', file=ofile)
        ytd.unit_dict[cur_id].print(ofile)
        print('##Item', file=ofile)
        ytd.unit_dict[item_dict[cur_id]].print(ofile)
        if abil_dict[cur_id]:
            print('##Abilities', file=ofile)
            for abil in sorted(abil_dict[cur_id]):
                ytd.unit_dict[abil].print(ofile)
        if len(buff_dict[cur_id]):
            print('##Buffs', file=ofile)
            for buff in sorted(buff_dict[cur_id]):
                ytd.unit_dict[buff].print(ofile)
        print(file=ofile)
        if cur_id in upgrade_dict:
            cur_id = upgrade_dict[cur_id]
        else:
            break



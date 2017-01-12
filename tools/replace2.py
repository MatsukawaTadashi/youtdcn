from parse_tower import TowerCollection
import sys

map_108cn = TowerCollection('../../maps/108CN', 108)
map_108en = TowerCollection('../../maps/108EN', 108)
map_109 = TowerCollection('../map', 109)
logfile = open('log.txt', 'w', encoding='utf8')
processed = set()


# 0. build name dict
dictionary = {}
for id in map_108cn.ytd.unit_collection:
    assert id in map_108en.ytd.unit_collection
    cn_text = map_108cn.get_text(id)
    en_text = map_108en.get_text(id)
    if not cn_text or not en_text:
        continue
    key = en_text.to_string(False)
    for attr in cn_text.attr_dict:
        if attr not in en_text.attr_dict:
            print(attr, cn_text.to_string(), en_text.to_string())
            assert False
    if key in dictionary:
        cn_text2, _ = dictionary[key]
        assert cn_text2.to_string(False) == cn_text.to_string(False)

    dictionary[key] = (cn_text, en_text)

def check_attr(attr):
    ignored_list = ['Editor', 'Hotkey']
    for prefix in ignored_list:
        if attr.startswith(prefix):
            return False

    return True

def check_chinese(s):
    for i in s:
        if i.isalpha() and not (i.islower() or i.isupper()):
            return True
    return False

for id in map_109.ytd.unit_collection:
    text = map_109.get_text(id)
    if not text:
        continue
    key = text.to_string(False)
    if not key:
        continue
    if key not in dictionary:
        if not check_chinese(key):
            print(text.to_string(), file=logfile)
    else:
        cn_text, en_text = dictionary[key]
        for attr in text.attr_dict:
            if check_attr(attr):
                if text.attr_dict[attr] == cn_text.attr_dict[attr]:
                    continue
                if check_chinese(cn_text.attr_dict[attr][1]):
                    print(text.attr_dict[attr])
                    print(cn_text.attr_dict[attr])
                    text.attr_dict[attr][1] = cn_text.attr_dict[attr][1]

# map_109.write_back()
logfile.close()




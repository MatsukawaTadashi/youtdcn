from parse_tower import TowerCollection
import sys

map_108cn = TowerCollection('../../maps/108CN', 108)
map_108en = TowerCollection('../../maps/108EN', 108)
map_109 = TowerCollection('../map', 109)
tl_out = open('tl.txt', 'w', encoding='utf8')

processed = set()


# 0. build name dict
name_dict = {}
for id in map_108en.tower_ids:
    en_text = map_108en.get_text(id)
    name = en_text.attr_dict['Name'][1]
    name_dict[name] = id


def check_attr(attr):
    ignored_list = ['Editor', 'Hotkey']
    for prefix in ignored_list:
        if attr.startswith(prefix):
            return False

    return True

def replace_by_id(id, pre_id):
    text = map_109.get_text(id)
    pre_en = map_108en.get_text(pre_id)
    pre_cn = map_108cn.get_text(pre_id)
    key = text.to_string(False)

    for attr in text.attr_dict:
        if not check_attr(attr):
            continue
        if attr in pre_cn.attr_dict:
            text.attr_dict[attr][1] = pre_cn.attr_dict[attr][1]
        else:
            print('##Changed:', file=tl_out)
            print('##Old EN:', file=tl_out)
            print(pre_en.to_string(), file=tl_out)
            print('##Old CN:', file=tl_out)
            print(pre_cn.to_string(), file=tl_out)
            print('##New:', file=tl_out)
            print(text.to_string(), file=tl_out)


for id in map_109.tower_ids:
    tower = map_109.towers[id]
    text = map_109.get_text(id)
    name = text.attr_dict['Name'][1]
    if name in name_dict:
        pre_id = name_dict[name]
        pre_tower = map_108en.towers[pre_id]
        replace_by_id(tower.id, pre_tower.id)
        replace_by_id(tower.item_id, pre_tower.item_id)

        # Abil
        abil_dict = {}
        for abil in pre_tower.abil_ids:
            t = map_108en.get_text(abil)
            ft = map_108en.get_func_text(abil)
            if 'Buttonpos' not in ft.attr_dict:
                continue
            tip = t.attr_dict['Tip'][1]
            abil_dict[tip] = abil
        for abil in tower.abil_ids:
            t = map_109.get_text(abil)
            ft = map_109.get_func_text(abil)
            if 'Buttonpos' not in ft.attr_dict:
                continue
            tip = t.attr_dict['Tip'][1]
            if tip in abil_dict:
                replace_by_id(abil, abil_dict[tip])
            else:
                print('##New Abil', file=tl_out)
                print(t.to_string(), file=tl_out)

        # Buff
        buff_dict = {}
        for buff in pre_tower.buff_ids:
            t = map_108en.get_text(buff)
            tip = t.attr_dict['Bufftip'][1]
            buff_dict[tip] = buff
        for buff in tower.buff_ids:
            t = map_109.get_text(buff)
            tip = t.attr_dict['Bufftip'][1]
            if tip in buff_dict:
                replace_by_id(buff, buff_dict[tip])
            else:
                print('##New Buff', file=tl_out)
                print(t.to_string(), file=tl_out)

    else:
        print('##New Tower', file=tl_out)
        print(map_109.tower_to_string(tower), file=tl_out)









map_109.write_back()
tl_out.close()




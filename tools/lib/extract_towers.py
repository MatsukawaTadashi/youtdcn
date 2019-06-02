from .io.tower import TowerCollection
from .utils import check_attr, has_chinese


def extract_towers(old_en_map, old_cn_map, new_map, i18n_unit_file):
    old_en_towers = TowerCollection(old_en_map)
    old_cn_towers = TowerCollection(old_cn_map)
    new_towers = TowerCollection(new_map)
    tl_out = open(i18n_unit_file, 'w', encoding='utf8')

    # 0. build name dict
    name_dict = {}
    for id in old_en_towers.tower_ids:
        en_text = old_en_towers.get_text(id)
        name = en_text.attr_dict['Name'][1]
        name_dict[name] = id

    def replace_by_id(id, pre_id):
        text = new_towers.get_text(id)
        pre_en = old_en_towers.get_text(pre_id)
        pre_cn = old_cn_towers.get_text(pre_id)
        flag = False
        for attr in text.attr_dict:
            if not check_attr(attr):
                continue
            if attr in pre_cn.attr_dict:
                assert attr in pre_en.attr_dict
                if has_chinese(text.attr_dict[attr][1]):
                    continue
                if has_chinese(pre_cn.attr_dict[attr][1]):
                    if pre_en.attr_dict[attr][1] == text.attr_dict[attr][1]:
                        text.attr_dict[attr][1] = pre_cn.attr_dict[attr][1]
                    else:
                        flag = True
            else:
                flag = True
        if flag:
            print('##Changed:', file=tl_out)
            print('##Old EN:', file=tl_out)
            print(pre_en.to_string(), file=tl_out)
            print('##Old CN:', file=tl_out)
            print(pre_cn.to_string(), file=tl_out)
            print('##New:', file=tl_out)
            print(text.to_string(), file=tl_out)

    # 1. replace
    for id in new_towers.tower_ids:
        tower = new_towers.towers[id]
        text = new_towers.get_text(id)
        name = text.attr_dict['Name'][1]
        if has_chinese(name):
            continue
        if name in name_dict:
            pre_id = name_dict[name]
            pre_tower = old_en_towers.towers[pre_id]
            replace_by_id(tower.id, pre_tower.id)
            replace_by_id(tower.item_id, pre_tower.item_id)

            # Abil
            abil_dict = {}
            for abil in pre_tower.abil_ids:
                t = old_en_towers.get_text(abil)
                ft = old_en_towers.get_func_text(abil)
                if 'Buttonpos' not in ft.attr_dict:
                    continue
                tip = t.attr_dict['Tip'][1]
                abil_dict[tip] = abil
            for abil in tower.abil_ids:
                t = new_towers.get_text(abil)
                ft = new_towers.get_func_text(abil)
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
                t = old_en_towers.get_text(buff)
                text = t.to_string(False)
                buff_dict[text] = buff
            for buff in tower.buff_ids:
                t = new_towers.get_text(buff)
                text = t.to_string(False)
                if text in buff_dict:
                    replace_by_id(buff, buff_dict[text])
                else:
                    print('##New Buff', file=tl_out)
                    print(t.to_string(), file=tl_out)

        else:
            print('##New Tower', file=tl_out)
            print(new_towers.tower_to_string(tower), file=tl_out)

    # 2. write back
    new_towers.write_back()
    tl_out.close()

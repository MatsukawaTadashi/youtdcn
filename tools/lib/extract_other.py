from .io.map import War3Map
from .io.tower import TowerCollection
from .utils import check_attr, has_chinese


def extract_other(old_en, old_cn, new, i18n_unit_file, log_file):
    old_en_map = War3Map(old_en)
    old_en_towers = TowerCollection(old_en_map)
    old_cn_map = War3Map(old_cn)
    old_cn_towers = TowerCollection(old_cn_map)
    new_map = War3Map(new)
    new_towers = TowerCollection(new_map)
    output = open(i18n_unit_file, 'w', encoding='utf8')
    logfile = open(log_file, 'w', encoding='utf8')

    # 0. build name dict
    dictionary = {}
    for id in old_cn_map.unit_collection:
        assert id in old_en_map.unit_collection
        cn_text = old_cn_towers.get_text(id)
        en_text = old_en_towers.get_text(id)
        if not cn_text or not en_text:
            continue
        key = en_text.to_string(False)
        for attr in cn_text.attr_dict:
            if attr not in en_text.attr_dict:
                print(attr, cn_text.to_string(), en_text.to_string())
                assert False
        if key in dictionary:
            cn_text2, _ = dictionary[key]
            if cn_text2.to_string(False) != cn_text.to_string(False):
                print(cn_text2.to_string(False))
                print(cn_text.to_string(False))
            assert cn_text2.to_string(False) == cn_text.to_string(False)

        dictionary[key] = (cn_text, en_text)
    # 1. iterate new towers
    for id in new_map.unit_collection:
        text = new_towers.get_text(id)
        if not text:
            continue
        key = text.to_string(False)
        if not key:
            continue
        if key not in dictionary:
            if not has_chinese(key):
                # untranslated
                print(text.to_string(), file=output)
        else:
            cn_text, en_text = dictionary[key]
            for attr in text.attr_dict:
                if check_attr(attr):
                    if text.attr_dict[attr] == cn_text.attr_dict[attr]:
                        continue
                    if has_chinese(cn_text.attr_dict[attr][1]):
                        # replace!
                        print(text.attr_dict[attr], file=logfile)
                        print(cn_text.attr_dict[attr], file=logfile)
                        text.attr_dict[attr][1] = cn_text.attr_dict[attr][1]

    # 2. write back
    new_towers.write_back()
    output.close()
    logfile.close()

import argparse
from lib.io.map import War3Map
from lib.io.tower import TowerCollection
from lib.utils import has_chinese


def check(unit):
    l = ['Tip', 'Ubertip', 'Description']
    for attr in l:
        if attr in unit.attr_dict:
            if not has_chinese(unit.attr_dict[attr][1]):
                return False
    return True

def test_units(map_dir):
    m = War3Map(map_dir)
    tc = TowerCollection(m)
    for id in tc.tower_ids:
        t = tc.towers[id]
        x = tc.get_text(t.id)
        if not check(x):
            print(x.to_string())
        x = tc.get_text(t.item_id)
        if not check(x):
            print(x.to_string())
        if t.abil_ids:
            for abil in t.abil_ids:
                x = tc.get_text(abil)
                if not check(x):
                    print(x.to_string())
        if t.buff_ids:
            for buff in t.buff_ids:
                x = tc.get_text(buff)
                if not check(x):
                    print(x.to_string())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--new')
    args = parser.parse_args()
    test_units(args.new)

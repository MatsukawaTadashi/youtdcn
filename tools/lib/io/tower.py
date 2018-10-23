import re
import bisect
from ..constants import R_AUTOCAST_FUNC, R_BUFF_FUNC, R_ITEM_FUNC
from .map import War3Map


class Tower:
    def __init__(self):
        self.id = ''
        self.upgrade_id = ''
        self.item_id = ''
        self.abil_ids = []
        self.buff_ids = []


class TowerCollection:

    def __init__(self, ytd):
        self.ytd = ytd
        self.__init_regex(ytd.get_version())

        self.abil_id_dict = {}
        self.__init_abil_dict()

        self.item_id_dict = {}
        self.__init_item_dict()

        self.base_tower_ids = set()
        self.tower_ids = set()
        self.__init_towers()

        self.upgrade_id_dict = {}
        self.__init_upgrades()

        self.buff_id_dict = {}
        self.__init_buffs()

        self.__init_autocast()

        self.base_towers = {}
        self.towers = {}
        self.tower_families = []
        self.__init_construct_objects()

    # 0. regex
    def __init_regex(self, version):

        self.r_item_func = R_ITEM_FUNC[version]
        self.r_item_results = []

        self.r_buff_func = R_BUFF_FUNC[version]

        self.r_autocast_func = R_AUTOCAST_FUNC[version]

        # init function list
        self.function_list = []
        self.r_function = r"function (\w*?) takes"
        for i, line in enumerate(self.ytd.jass):
            match = re.search(self.r_function, line)
            if match:
                self.function_list.append(i)

        # init call_dict
        self.call_dict = {}
        self.r_call = r"call (.*?)\("
        for i, line in enumerate(self.ytd.jass):
            match = re.search(self.r_call, line)
            if match:
                function_name = match.group(1)
                self.call_dict.setdefault(function_name, [])
                self.call_dict[function_name].append(i)

    # 1. get towers from slk
    # Tower has the XSEL(Sell) ability
    # row 1: header;
    # col 1: tower_id, col 5: tower_abil;
    def __init_abil_dict(self):
        slk = self.ytd.abilities_slk
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

            self.abil_id_dict[id] = abil

        abil_cnt = {}
        for id in self.abil_id_dict:
            for x in self.abil_id_dict[id]:
                abil_cnt.setdefault(x, 0)
                abil_cnt[x] += 1

        basic_abilities = set([x for x in abil_cnt if abil_cnt[x] > 1])
        for x in abil_cnt:
            if x.startswith('A00'):
                basic_abilities.add(x)

        # 108b: This will get 706 towers (include base towers) and their abilities

        for id in self.abil_id_dict:
            self.abil_id_dict[id] = set([x for x in self.abil_id_dict[id] if x not in basic_abilities])

    # 2. get tower's item from jass
    def __init_item_dict(self):
        for i, line in enumerate(self.ytd.jass):
            match = re.search(self.r_item_func, line)
            if match:
                id = match.group(1)
                item_id = match.group(2)
                self.item_id_dict[id] = item_id
                self.r_item_results.append(i)

    # 2.5 get towers
    def __init_towers(self):
        self.base_tower_ids = sorted(set([x for x in self.abil_id_dict if x not in self.item_id_dict]))
        self.tower_ids = sorted(set([x for x in self.item_id_dict]))

    # 3. get tower's upgrade from func.txt
    def __init_upgrades(self):
        key_upgrade = "Upgrade"
        for id in self.tower_ids:
            attr_dict = self.ytd.unit_collection[id].func_text.attr_dict
            if key_upgrade in attr_dict:
                upgrade_id = attr_dict[key_upgrade][1]
                if not upgrade_id:
                    continue
                assert len(upgrade_id) == 4
                assert id not in self.upgrade_id_dict
                self.upgrade_id_dict[id] = upgrade_id

    # 4. get tower's buff from jass
    # IIv function linked buff with its effect ability
    def __init_buffs(self):

        for id in self.tower_ids:
            self.buff_id_dict.setdefault(id, set())

        for i, line in enumerate(self.ytd.jass):
            match = re.search(self.r_buff_func, line)
            if not match:
                continue
            buff_id = match.group(1)
            # get function
            line_number = i
            j = bisect.bisect_left(self.function_list, line_number)
            if not j:
                continue
            cur_line = self.ytd.jass[self.function_list[j - 1]]
            function_match = re.search(self.r_function, cur_line)
            if not function_match:
                continue
            function_name = function_match.group(1)

            # get call
            if function_name not in self.call_dict:
                continue

            id = None
            for line_number in self.call_dict[function_name]:
                j = bisect.bisect_left(self.r_item_results, line_number)
                k = bisect.bisect_left(self.function_list, line_number)
                if j and k and self.r_item_results[j - 1] > self.function_list[k - 1]:
                    bfv_match = re.search(self.r_item_func, self.ytd.jass[self.r_item_results[j - 1]])
                    if bfv_match:
                        res = bfv_match.group(1)
                        if id is not None and id != res:
                            assert False
                        id = res
            if id:
                # tower_name = self.ytd.unit_collection[id].string_text.attr_dict['Name'][1]
                # buff_name = self.ytd.unit_collection[buff_id].string_text.attr_dict['Bufftip'][1]
                # print('Tower Name: {0} Buff Name: {1}'.format(tower_name, buff_name), file=sys.stderr)
                self.buff_id_dict[id].add(buff_id)

    # 4.5 autocast abil
    def __init_autocast(self):
        for i, line in enumerate(self.ytd.jass):
            match = re.search(self.r_autocast_func, line)
            if not match:
                continue
            abil_id = match.group(1)
            # get function
            line_number = i
            j = bisect.bisect_left(self.function_list, line_number)
            if not j:
                continue
            cur_line = self.ytd.jass[self.function_list[j - 1]]
            function_match = re.search(self.r_function, cur_line)
            if not function_match:
                continue
            function_name = function_match.group(1)

            # get call
            if function_name not in self.call_dict:
                continue

            id = None
            for line_number in self.call_dict[function_name]:
                j = bisect.bisect_left(self.r_item_results, line_number)
                k = bisect.bisect_left(self.function_list, line_number)
                if j and k and self.r_item_results[j - 1] > self.function_list[k - 1]:
                    bfv_match = re.search(self.r_item_func, self.ytd.jass[self.r_item_results[j - 1]])
                    if bfv_match:
                        res = bfv_match.group(1)
                        if id is not None and id != res:
                            assert False
                        id = res
            if id:
                # tower_name = self.ytd.unit_collection[id].string_text.attr_dict['Name'][1]
                # abil_name = self.ytd.unit_collection[abil_id].string_text.attr_dict['Tip'][1]
                # print('Tower Name: {0} Ability Name: {1}'.format(tower_name, abil_name), file=sys.stderr)
                self.abil_id_dict[id].add(abil_id)

    def __init_construct_objects(self):
        upgraded = set()
        for id in self.tower_ids:
            t = Tower()
            t.id = id
            t.item_id = self.item_id_dict[id]
            if id in self.upgrade_id_dict:
                t.upgrade_id = self.upgrade_id_dict[id]
                upgraded.add(t.upgrade_id)

            if self.abil_id_dict[id]:
                t.abil_ids = sorted(self.abil_id_dict[id])

            if self.buff_id_dict[id]:
                t.buff_ids = sorted(self.buff_id_dict[id])
            self.towers[id] = t

        for id in self.tower_ids:
            if id not in upgraded:
                self.tower_families.append(self.towers[id])

        for id in self.base_tower_ids:
            t = Tower()
            t.id = id

            if self.abil_id_dict[id]:
                t.abil_ids = sorted(self.abil_id_dict[id])

            self.base_towers[id] = t

    def tower_to_string(self, t):
        assert isinstance(t, Tower)
        res = []
        res.append('##Tower')
        res.append(self.get_text(t.id).to_string())
        res.append('##Item')
        res.append(self.get_text(t.item_id).to_string())
        if t.abil_ids:
            res.append('##Abilities')
            for abil in t.abil_ids:
                res.append(self.get_text(abil).to_string())
        if t.buff_ids:
            res.append('##Buffs')
            for buff in t.buff_ids:
                res.append(self.get_text(buff).to_string())
        res.append('')
        return '\n'.join(res)

    def get_text(self, id):
        return self.ytd.unit_collection[id].string_text

    def get_func_text(self, id):
        return self.ytd.unit_collection[id].func_text

    def write_back(self):
        for prefix in self.ytd.unit_text_file_collection:
            string, func = self.ytd.unit_text_file_collection[prefix]
            string.write_back()


def print_towers(map_dir, i18n_unit_file):
    ytd = War3Map(map_dir)
    tc = TowerCollection(ytd)
    with open(i18n_unit_file, 'w', encoding='utf8') as ofile:
        for tower in tc.tower_families:
            t = tower
            # print tower family
            while True:
                print(tc.tower_to_string(t), file=ofile)
                if t.upgrade_id:
                    t = tc.towers[t.upgrade_id]
                else:
                    break

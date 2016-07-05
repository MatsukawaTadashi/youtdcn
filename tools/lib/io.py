import os
import re
import sys

jass_dir = "scripts/war3map.j"
abilities_slk_dir = "Units/UnitAbilities.slk"
unit_dir = "Units/"
r_unit_id = r"\[\w{4}\]"

class unit:
    id = None
    text = None
    path = None

    def print(self, file):
        for line in self.text:
            print(line, file=file)


class unit_txt:
    path = None
    units = None

    def __init__(self, path):
        self.path = path
        self.units = []
        with open(path, 'r', encoding='utf8') as ifile:
            lines = ifile.readlines()
            lines = [x.strip() for x in lines if x.strip()]
            lines = [x for x in lines if not x.startswith('##')]
        ids = [i for i in range(len(lines)) if re.search(r_unit_id, lines[i])]
        ids.append(len(lines))
        for i in range(len(ids) - 1):
            head = ids[i]
            tail = ids[i + 1]
            t_unit = unit()
            t_unit.id = lines[head][1:-1]
            t_unit.text = [lines[x] for x in range(head, tail)]
            t_unit.path = path
            self.units.append(t_unit)
    def write_back(self):
        with open(self.path, 'w', encoding='utf8') as ofile:
            for unit in self.units:
                for line in unit.text:
                    print(line, file=ofile)


class unit_dict_value:
    id = None
    string = None
    func = None

    def __init__(self, id):
        self.id = id

    def print(self, ofile):
        if self.string:
            self.string.print(ofile)
        else:
            print(id, file=sys.stderr)

class map:
    jass = None
    jass_function_list = None
    abilities_slk = None
    unit_txts = None
    unit_dict = None

    def __init__(self, path):
        self.unit_txts = {}
        self.unit_dict = {}

        print('Reading map: {0}'.format(path))

        # 1.jass
        jass_path = os.path.join(path, jass_dir)
        with open(jass_path, 'r', encoding='utf8') as ifile:
            self.jass = ifile.readlines()

        # 2. slk
        self.abilities_slk = os.path.join(path, abilities_slk_dir)
        self.abilities_slk = self.parse_slk(self.abilities_slk)

        # 3. units
        unit_path = os.path.join(path, unit_dir)
        files = os.listdir(unit_path)

        string_files = [x for x in files if x.endswith('Strings.txt')]
        for x in string_files:
            prefix = x[:-len('Strings.txt')]
            full_path = os.path.join(unit_path, x)
            self.unit_txts.setdefault(prefix, [])
            self.unit_txts[prefix].append(unit_txt(full_path))

        func_files = [x for x in files if x.endswith('Func.txt')]
        for x in func_files:
            prefix = x[:-len('Func.txt')]
            full_path = os.path.join(unit_path, x)
            self.unit_txts.setdefault(prefix, [])
            self.unit_txts[prefix].append(unit_txt(full_path))

        for x in self.unit_txts:
            assert(len(self.unit_txts[x]) == 2)

        # 4. build unit dict
        string_dict = {}
        func_dict = {}
        for prefix in self.unit_txts:
            string_file = self.unit_txts[prefix][0]
            func_file = self.unit_txts[prefix][1]
            for unit in string_file.units:
                if unit.id in string_dict:
                    print('Warning: multiple appearance!', file=sys.stderr)
                    print(unit.id, file=sys.stderr)
                    continue

                string_dict[unit.id] = unit

            for unit in func_file.units:
                if unit.id in func_dict:
                    print('Warning: multiple appearance!', file=sys.stderr)
                    print(unit.id, file=sys.stderr)
                    continue

                func_dict[unit.id] = unit

        for i in string_dict:
            self.unit_dict.setdefault(i, unit_dict_value(i))
            self.unit_dict[i].string = string_dict[i]

        for i in func_dict:
            self.unit_dict.setdefault(i, unit_dict_value(i))
            self.unit_dict[i].func = func_dict[i]

    def parse_slk(self, path):
        with open(path, 'r') as ifile:
            lines = ifile.readlines()
            lines = [x.strip() for x in lines if x.strip()]
        lines = [x.strip() for x in lines if x.strip()]
        # ignore the first 2 lines
        lines = lines[2:]
        X = 0
        Y = 0
        res = {}
        for line in lines:
            tmp = line.split(';')
            for val in tmp:
                if val.startswith('X'):
                    X = int(val[1:])
                elif val.startswith('Y'):
                    Y = int(val[1:])
                elif val.startswith('K'):
                    val = val[1:]
                    if val.startswith('"') and val.endswith('"'):
                        val = val[1:-1]
                    res.setdefault(Y, {})
                    res[Y].setdefault(X, val)
        return res


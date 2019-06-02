import os
import re
import sys
from ..constants import R_MAP_VERSION, JASS_DIR

abilities_slk_dir = "Units/UnitAbilities.slk"
unit_dir = "Units/"
r_unit_id = r"^\[\w{4}\]$"
comment_prefix = '##'


class UnitText:
    def __init__(self, id, lines):
        self.id = id
        self.attr_dict = {}
        self.attr_list = []

        for line in lines:
            if line.startswith('//'):
                continue
            if '=' not in line:
                print('Warning: Illegal attribute:', id, line, file=sys.stderr)
                continue
            splited = line.split('=')

            key = splited[0]
            val = '='.join(splited[1:])
            if key in self.attr_dict:
                print('Warning: Unit attribute multiple assignment.', file=sys.stderr)
                print('ID: {0} Line: {1}'.format(self.id, line), file=sys.stderr)
                print(file=sys.stderr)

            else:
                x = [key, val]
                self.attr_dict[key] = x
                self.attr_list.append(x)

    def to_string(self, with_id=True):
        res = []
        if with_id:
            res.append('[{0}]\n'.format(self.id))
        for attr in self.attr_list:
            key = attr[0]
            val = attr[1]
            res.append('{0}={1}\n'.format(key, val))

        return ''.join(res)


class UnitTextFile:
    def __init__(self, path):
        self.path = path
        self.unit_dict = {}
        self.unit_list = []

        print('Processing {0}.'.format(path), file=sys.stderr)

        with open(path, 'r', encoding='utf8') as ifile:
            lines = ifile.readlines()
            lines = [x.strip() for x in lines if x.strip()]
            lines = [x for x in lines if not x.startswith(comment_prefix)]

        ids = [i for i in range(len(lines)) if re.match(r_unit_id, lines[i])]
        ids.append(len(lines))
        for i in range(len(ids) - 1):
            head = ids[i]
            tail = ids[i + 1]
            id = lines[head][1:-1]
            t_unit = UnitText(id, lines[head + 1: tail])

            if id in self.unit_dict:
                print('Warning:  multiple appearance in one file!', file=sys.stderr)
                print('ID: {0}, File: {1}'.format(id, self.path), file=sys.stderr)
                print(file=sys.stderr)
            else:
                self.unit_dict[id] = t_unit

            self.unit_list.append(t_unit)

    def write_back(self):
        with open(self.path, 'w', encoding='utf8') as ofile:
            for unit in self.unit_list:
                ofile.write(unit.to_string())


class Unit:
    def __init__(self, x, string_file, func_file):
        self.id = x
        self.string_text = None
        self.string_text_file = string_file
        if string_file:
            self.string_text = string_file.unit_dict[x]

        self.func_text = None
        self.func_text_file = func_file
        if func_file:
            self.func_text = func_file.unit_dict[x]


class War3Map:
    def __init__(self, root_path):
        self.path = root_path
        self.jass = []
        self.jass_function_list = []
        self.wts = {}
        self.abilities_slk = []
        self.unit_text_file_collection = {}
        self.unit_collection = {}

        print('Reading map: {0}'.format(root_path), file=sys.stderr)

        # 1.jass
        jass_path = os.path.join(root_path, JASS_DIR)
        with open(jass_path, 'r', encoding='utf8') as ifile:
            self.jass = ifile.readlines()

        # 2. slk
        abilities_slk_path = os.path.join(root_path, abilities_slk_dir)
        self.abilities_slk = self.parse_slk(abilities_slk_path)

        # 3. units
        unit_path = os.path.join(root_path, unit_dir)
        files = os.listdir(unit_path)

        # 3.5 wts
        wts_path = os.path.join(root_path, 'war3map.wts')
        if os.path.exists(wts_path):
            wts_i = 0
            wts_content = False
            with open(wts_path, 'r', encoding='utf8') as ifile:
                for line in ifile:
                    if line.strip() == '{':
                        wts_content = True
                    elif line.strip() == '}':
                        wts_content = False
                    elif wts_content:
                        self.wts[wts_i] = line.strip()
                    elif line.startswith('STRING'):
                        wts_i = int(line[7:])

        string_files = [x for x in files if x.endswith('Strings.txt')]
        for file_name in string_files:
            prefix = file_name[:-len('Strings.txt')]
            full_path = os.path.join(unit_path, file_name)
            self.unit_text_file_collection.setdefault(prefix, [])
            self.unit_text_file_collection[prefix].append(UnitTextFile(full_path))

        func_files = [x for x in files if x.endswith('Func.txt')]
        for file_name in func_files:
            prefix = file_name[:-len('Func.txt')]
            full_path = os.path.join(unit_path, file_name)
            self.unit_text_file_collection.setdefault(prefix, [])
            self.unit_text_file_collection[prefix].append(UnitTextFile(full_path))

        for file_name in self.unit_text_file_collection:
            assert(len(self.unit_text_file_collection[file_name]) == 2)

        # 4. build unit dict
        id2string_file = {}
        id2func_file = {}
        for prefix in self.unit_text_file_collection:
            string_file = self.unit_text_file_collection[prefix][0]
            func_file = self.unit_text_file_collection[prefix][1]
            for unit in string_file.unit_list:
                if unit.id in id2string_file:
                    print('Warning: multiple appearance!', file=sys.stderr)
                    print('ID: {0}, File1: {1}, File2: {2}'.format(unit.id,
                                                                   id2string_file[unit.id].path,
                                                                   string_file.path),
                          file=sys.stderr)
                    print(file=sys.stderr)
                else:
                    id2string_file[unit.id] = string_file

            for unit in func_file.unit_list:
                if unit.id in id2func_file:
                    print('Warning: multiple appearance!', file=sys.stderr)
                    print('ID: {0}, File1: {1}, File2: {2}'.format(unit.id,
                                                                   id2func_file[unit.id].path,
                                                                   func_file.path),
                          file=sys.stderr)
                    print(file=sys.stderr)
                else:
                    id2func_file[unit.id] = func_file
        id_set = set(id2string_file.keys()) | set(id2func_file.keys())
        for id in id_set:
            string_file = None
            if id in id2string_file:
                string_file = id2string_file[id]
            func_file = None
            if id in id2func_file:
                func_file = id2func_file[id]
            self.unit_collection[id] = Unit(id, string_file, func_file)

    def get_version(self):
        for line in self.jass:
            match = re.search(R_MAP_VERSION, line)
            if match:
                target = match[1]
                if target.startswith('TRIGSTR_'):
                    idx = int(target[8:])
                    target = self.wts[idx]
                if target.startswith('YouTD v'):
                    return target[7:]
        raise Exception('Get map version failed {0}'.format(self.path))

    @staticmethod
    def parse_slk(path):
        with open(path, 'r', encoding='utf8') as ifile:
            lines = ifile.readlines()
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

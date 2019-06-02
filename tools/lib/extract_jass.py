import re
from os.path import join
from .constants import R_BUFF_ID_FUNC, R_CONTRIBUTORS_FUNC, R_CUSTOM_STORAGE_FUNC, R_TOWEREFFECT_FUNC, R_EXP_FUNC, R_INIT_CHAR_FUNC, R_MONSTER_SKILL_TAG_FUNC
from .utils import has_chinese

def clean(text, version):
    pattern_list = [
        r'^call ExecuteFunc\("\w*?"\)$',
        r'^call AddUnitAnimationProperties\(.*?\)$',
        r'^call QueueUnitAnimation\(.*?\)$',
        r'^call SetSoundParamsFromLabel\(.*?\)$',
        r'^call NewSoundEnvironment\(\".*?\"\)$',
        r'^call SetAmbientDaySound\(\".*?\"\)$',
        r'^call SetAmbientNightSound\(\".*?\"\)$',
        r'CreateSoundFromLabel\("\w*?".*?\)$',
        r'StringHash\(\(\".*?\"\)\)',
        r'^call BJDebugMsg\(\".*?\"\)$',
        R_TOWEREFFECT_FUNC[version],
        R_CUSTOM_STORAGE_FUNC[version],
        R_CONTRIBUTORS_FUNC[version],
        R_BUFF_ID_FUNC[version],
        R_EXP_FUNC[version],
        R_INIT_CHAR_FUNC[version],
        R_MONSTER_SKILL_TAG_FUNC[version]
    ]
    for p in pattern_list:
        text = re.sub(p, '', text, flags=re.M)
    return text


def extract_string(war3map):
    text = clean(''.join(war3map.jass), war3map.get_version())
    r_a = r'("([^\\"]|(\\.))*")'
    r_b = r"('([^\\']|(\\.))*')"
    r_string = r_a + '|' + r_b
    matches = re.finditer(r_string, text)
    res = []
    for x in matches:
        res.append(x.group(0))
    return res


def ignore(x):
    text = x[1:-1]
    pre = [r'^[A-Z][a-z]{2,3}$', '^xp$', '^DPS$', '^AoE$']
    for i in range(len(pre)):
        x = pre[i]
        if re.search(x, text):
            return 0
    ire = [r'^\w{1,4}$', r'^\|[cC]\w{8}\s*$', r'^([_\-\w]+\\\\)+([_\-\w]+\.\w{3})?$', r'^[^\w]*$', r'^[A-Z_]*$', r'^[a-z_]*$', r'^\.\w{3}$']
    for i in range(len(ire)):
        x = ire[i]
        if re.search(x, text):
            return i + 1
    return 0


def extract_jass(old_en_map, old_cn_map, new_map, i18n_jass_file, ignore_list_file):
    outfile = open(i18n_jass_file, 'w', encoding='utf8')
    res_new = extract_string(new_map)
    res_en = extract_string(old_en_map)
    res_cn = extract_string(old_cn_map)
    assert len(res_cn) == len(res_en)
    # Generate old dict
    old_dict = {}
    for i in range(len(res_cn)):
        if res_en[i] == res_cn[i]:
            continue

        if not has_chinese(res_cn[i]):
            print(i)
            print(res_en[i])
            print(res_cn[i])
            assert False

        if res_en[i] in old_dict:
            old_dict[res_en[i]].add(res_cn[i])
        else:
            old_dict[res_en[i]] = {res_cn[i]}
    # Replace
    processed = set()
    ignored_list = {}
    for sent in res_new:
        if sent in processed or has_chinese(sent):
            continue
        if sent in old_dict:
            ig_res = ignore(sent)
            if ig_res:
                print(sent, old_dict[sent])
            if len(old_dict[sent]) == 1:
                processed.add(sent)
                print('##Old', file=outfile)
                print(sent, file=outfile)
                print(list(old_dict[sent])[0], file=outfile)
            else:
                processed.add(sent)
                print('##Multiple choices', file=outfile)
                print(sent, file=outfile)
                print('|'.join(old_dict[sent]), file=outfile)
        else:
            ig_res = ignore(sent)
            if ig_res:
                ignored_list.setdefault(ig_res, [])
                ignored_list[ig_res].append(sent)
                continue
            processed.add(sent)
            print('##New', file=outfile)
            print(sent, file=outfile)
            print(sent, file=outfile)
    outfile.close()

    # generate ignore list file
    if ignore_list_file:
        with open(ignore_list_file, 'w', encoding='utf8') as ignored_outfile:
            type_list = []
            for type in ignored_list:
                type_list.append(type)
            type_list.sort()
            for type in type_list:
                for sent in ignored_list[type]:
                    print('Ignored:', sent, file=ignored_outfile)
                print(file=ignored_outfile)

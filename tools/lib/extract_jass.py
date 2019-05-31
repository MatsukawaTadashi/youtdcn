import re
from os.path import join
from .constants import JASS_DIR
from .utils import has_chinese


def extract_string(jass_file):
    with open(jass_file, 'r', encoding='utf8') as infile:
        text = infile.read()
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
    ire = [r'^\w{1,4}$', r'^([_\-\w]+\\\\)+([_\-\w]+\.\w{3})?$', r'^[^\w]*$', r'^[A-Z_]*$', r'^[a-z_]*$']
    for i in range(len(ire)):
        x = ire[i]
        if re.search(x, text):
            return i + 1
    return 0


def extract_jass(old_en, old_cn, new_en, i18n_jass_file, ignore_list_file):
    outfile = open(i18n_jass_file, 'w', encoding='utf8')
    res_new = extract_string(join(new_en, JASS_DIR))
    res_en = extract_string(join(old_en, JASS_DIR))
    res_cn = extract_string(join(old_cn, JASS_DIR))
    assert len(res_cn) == len(res_en)
    with open(join(new_en, JASS_DIR), 'r', encoding='utf8') as ifile:
        text_new = ifile.read()
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
        if sent in processed:
            continue
        if sent in old_dict:
            ig_res = ignore(sent)
            if ig_res:
                print(sent, old_dict[sent])
            if len(old_dict[sent]) == 1:
                processed.add(sent)
                text_new = text_new.replace(sent, list(old_dict[sent])[0])
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

    # write back confident translations
    #with open(join(new_en, JASS_DIR), 'w', encoding='utf8') as ofile:
    #    ofile.write(text_new)

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

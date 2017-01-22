import re
from lib.utils import has_chinese


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
if __name__ == '__main__':
    jass_108cn = "../../maps/108CN/scripts/war3map.j"
    jass_108en = "../../maps/108EN/scripts/war3map.j"
    jass_109 = "../map/scripts/war3map.j"
    outfile = open('jass.txt', 'w', encoding='utf8')
    res_cn = extract_string(jass_108cn)
    res_en = extract_string(jass_108en)
    assert len(res_cn) == len(res_en)
    d = {}
    for i in range(len(res_cn)):
        if res_en[i] == res_cn[i]:
            continue

        if not has_chinese(res_cn[i]):
            print(res_en[i], res_cn[i])
            assert False

        if res_en[i] in d:
            d[res_en[i]].add(res_cn[i])
        else:
            d[res_en[i]] = {res_cn[i]}
    res_109 = extract_string(jass_109)

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

    processed = set()
    ignored_list = {}
    with open(jass_109, 'r', encoding='utf8') as ifile:
        text = ifile.read()
    for x in res_109:
        if x in processed:
            continue
        if x in d:
            ig_res = ignore(x)
            if ig_res:
                print(x, d[x])
            if len(d[x]) == 1:
                processed.add(x)
                text = text.replace(x, list(d[x])[0])
            else:
                processed.add(x)
                print('##Multiple choices', file=outfile)
                print(x, file=outfile)
                print('|'.join(d[x]), file=outfile)
        else:
            ig_res = ignore(x)
            if ig_res:
                ignored_list.setdefault(ig_res, [])
                ignored_list[ig_res].append(x)
                continue
            processed.add(x)
            print('##New', file=outfile)
            print(x, file=outfile)
            print(x, file=outfile)
    outfile.close()

    write_back = True
    if write_back:
        with open(jass_109, 'w', encoding='utf8') as ofile:
            ofile.write(text)

    print_ignored = False
    if print_ignored:
        with open('ignored.txt', 'w', encoding='utf8') as ignored_outfile:
            type_list = []
            for type in ignored_list:
                type_list.append(type)
            type_list.sort()
            for type in type_list:
                for x in ignored_list[type]:
                    print('Ignored:', x, file=ignored_outfile)
                print(file=ignored_outfile)


from os.path import join
from .constants import JASS_DIR


def write_back_jass(i18n_jass_file, map_dir):
    with open(i18n_jass_file, 'r', encoding='utf8') as ifile:
        i18n = ifile.readlines()
    if not i18n[-1].strip():
        i18n = i18n[:-1]
    anchors = [i for i, line in enumerate(i18n) if line.startswith('##')]
    anchors.append(len(i18n))
    strs = []
    for i in range(1, len(anchors)):
        assert (anchors[i] - anchors[i-1] - 1) % 2 == 0
        mid = (anchors[i] - anchors[i-1] + 1) // 2 + anchors[i-1]
        strs.append(''.join(i18n[anchors[i-1]+1:mid]).strip())
        strs.append(''.join(i18n[mid:anchors[i]]).strip())
    assert len(strs) % 2 == 0

    jass_file = join(map_dir, JASS_DIR)
    with open(jass_file, 'r', encoding='utf8') as ifile:
        text = ifile.read()
    for i in range(len(strs) // 2):
        text = text.replace(strs[i * 2], strs[i * 2 + 1])
    with open(jass_file, 'w', encoding='utf8') as ofile:
        ofile.write(text)

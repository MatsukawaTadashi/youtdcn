from .extract_jass import extract_string


def write_back_jass(i18n_jass_file, jass_file):
    with open(jass_file, 'r', encoding='utf8') as ifile:
        text = ifile.read()
    strs = extract_string(i18n_jass_file)
    assert len(strs) % 2 == 0
    for i in range(len(strs) // 2):
        text = text.replace(strs[i * 2], strs[i * 2 + 1])
    with open(jass_file, 'w', encoding='utf8') as ofile:
        ofile.write(text)

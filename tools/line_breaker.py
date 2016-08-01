import re
ifile = open('ItemStrings.txt', 'r', encoding='utf8')
ofile = open('ItemStrings2.txt', 'w', encoding='utf8')
fmt = 'Ubertip="{0}"\n'
threshold = 18

def clear_escape(s: str):
    s = re.sub(r"\|r",'',s)
    s = re.sub(r"\|c\w{8}", '', s)
    return s
def word_cnt(s: str):
    cnt = 0
    s = clear_escape(s)
    if all([x.isalnum() or x.isspace() or x in ["-",".","'",'%',',','<','>'] for x in s]):
        return 0
    for i in s:
        if i.isalnum() or i.isspace():
            cnt += 0.5
        else:
            cnt += 1
    return cnt
for line in ifile:
    if line.startswith('Ubertip='):
        target = line[9:-2]
        splited = target.split('|n')
        for i in range(len(splited)):
            if word_cnt(splited[i]) > threshold:
                if ' ' in splited[i] and not ('作者' in splited[i] or '模组' in splited[i] ):
                    splited[i] = splited[i].replace(' ','')
        line = line[:9] + '|n'.join(splited) + line[-2:]

    ofile.write(line)

ifile.close()
ofile.close()
import re
ifile = open('ItemStrings.txt', 'r', encoding='utf8')
ofile = open('ItemStrings2.txt', 'w', encoding='utf8')
fmt = r"^((Ubertip=)|(Description=))"
threshold = 18


def clear_escape(s):
    s = re.sub(r"\|r",'',s)
    s = re.sub(r"\|c\w{8}", '', s)
    return s


def word_cnt(s):
    cnt = 0
    s = clear_escape(s)
    if not any([i.isalpha() and not (i.islower() or i.isupper()) for i in s]):
        return 0
    for i in s:
        if i.isalpha() and not (i.islower() or i.isupper()):
            cnt += 1
        else:
            cnt += 0.5
    return cnt

if __name__ == '__main__':
    for line in ifile:f
        if re.match(fmt, line):
            fq = line.find('"')
            lq = line.rfind('"')
            target = line[fq + 1: lq]
            splited = target.split('|n')
            for i in range(len(splited)):
                if word_cnt(splited[i]) > threshold:
                    if ' ' in splited[i] and not ('作者' in splited[i] or '模组' in splited[i]):
                        splited[i] = splited[i].replace(' ','')
                        print(splited[i])
            line = line[:fq + 1] + '|n'.join(splited) + line[lq:]

        ofile.write(line)

    ifile.close()
    ofile.close()
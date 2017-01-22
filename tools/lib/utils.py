def has_chinese(s):
    for i in s:
        if i.isalpha() and not (i.islower() or i.isupper()):
            return True
    return False

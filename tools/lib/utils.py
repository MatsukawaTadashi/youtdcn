def has_chinese(s):
    for i in s:
        if i in ['。']:
            return True
        if i.isalpha() and not (i.islower() or i.isupper()):
            return True
    return False


def check_attr(attr):
    ignored_list = ['Editor', 'Hotkey']
    for prefix in ignored_list:
        if attr.startswith(prefix):
            return False

    return True

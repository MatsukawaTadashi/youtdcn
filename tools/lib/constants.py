JASS_DIR = "scripts/war3map.j"
R_MAP_VERSION = r'call SetMapName\(\"(.*?)\"\)'
R_ITEM_FUNC = {
    '1.08': r"bfv\('(\w{4})'.*?'(\w{4})'.*?\)",
    '1.09': r"cIv\('(\w{4})'.*?'(\w{4})'.*?\)",
    '1.10b': r"CVv\('(\w{4})'.*?'(\w{4})'.*?\)",
    '1.10c': r"Cjv\('(\w{4})'.*?'(\w{4})'.*?\)"
}
R_BUFF_FUNC = {
    '1.08': r"IIv\(.*?'\w{4}'.*?'(\w{4})'\)",
    '1.09': r"Azv\(.*?'\w{4}'.*?'(\w{4})'\)",
    '1.10b': r"Nsv\(.*?'\w{4}'.*?'(\w{4})'\)",
    '1.10c': r"N7v\(.*?'\w{4}'.*?'(\w{4})'\)"
}
R_AUTOCAST_FUNC = {
    '1.08': r"rmv\(.*?,.*?,.*?'(\w{4})'",
    '1.09': r"avv\(.*?,.*?,.*?'(\w{4})'",
    '1.10b': r"aZv\(.*?,.*?,.*?'(\w{4})'",
    '1.10c': r"nXv\(.*?,.*?,.*?'(\w{4})'"
}

R_TOWEREFFECT_FUNC = {
    '1.10b': r"i7v\(.*?\)",
    '1.10c': r"acv\(.*?\)"
}

R_CUSTOM_STORAGE_FUNC = {
    '1.10b': r"^call vAv.*?$",
    '1.10c': r"^call vMv.*?$"
}

R_BUFF_ID_FUNC = {
    '1.10b': r"^call Nwv.*?$",
    '1.10c': r"^call bov.*?$"
}

R_CONTRIBUTORS_FUNC = {
    '1.10b': r"^call rMv.*?$",
    '1.10c': r"^call r0v.*?$"
}

R_EXP_FUNC = {
    '1.10b': r"function Oov[\s\S]*?endfunction",
    '1.10c': r"function Ogv[\s\S]*?endfunction"
}

R_INIT_CHAR_FUNC = {
    '1.10b': r"function Xhv[\s\S]*?endfunction",
    '1.10c': r"function XWv[\s\S]*?endfunction"
}

R_MONSTER_SKILL_TAG_FUNC = {
    '1.10b': r"^call dhv.*?$",
    '1.10c': r"^call dwv.*?$"
}

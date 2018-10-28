from .io.map import War3Map
from .io.map import UnitTextFile


def write_back_units(i18n_unit_file, map_dir):
    ytd = War3Map(map_dir)
    units = UnitTextFile(i18n_unit_file)
    for unit in units.unit_list:
        text = ytd.unit_collection[unit.id].string_text
        print(unit.id)
        for attr in unit.attr_dict:
            print(attr)
            assert attr in text.attr_dict
            text.attr_dict[attr][1] = unit.attr_dict[attr][1]
    for prefix in ytd.unit_text_file_collection:
        string, func = ytd.unit_text_file_collection[prefix]
        string.write_back()

import argparse
from lib.write_back_jass import write_back_jass
from lib.write_back_units import write_back_units

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--i18n_jass_file')
    parser.add_argument('-u', '--i18n_unit_file')
    parser.add_argument('-n', '--new')

    args = parser.parse_args()
    jass = args.i18n_jass_file
    unit = args.i18n_unit_file
    new = args.new
    
    if jass:
        write_back_jass(jass, new)
    if unit:
        write_back_units(unit, new)
    
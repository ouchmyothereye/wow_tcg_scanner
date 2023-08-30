#!/usr/bin/python3.5
#settings.py
#Store settings in a dictionary and return it

def main():
    settings_dictionary = {}
    settings_dictionary['PATH'] = r"C:\Users\hallc\Documents\worldbuilding\wow_tcg_scanner"
    settings_dictionary['UP'] = 7.5
    settings_dictionary['DOWN'] = 2.5
    settings_dictionary['START'] = 1
    settings_dictionary['PIN_SRV_SCAN'] = 33
    settings_dictionary['PIN_BBEAM'] = 3
    settings_dictionary['RUNS'] = 0
    settings_dictionary['LST_EXP_NAME'] = ["AZEROTH", "DARK PORTAL", "OUTLAND", "LEGION", "BETRAYER", "ILLIDAN", "DRUMS", "GLADIATORS", "HONOR", "SCOURGEWAR", "WRATHGATE", "ICECROWN", "WORLDBREAKER", "ELEMENTS", "TWILIGHT", "THRONE", "CROWN", "TOMB", "ANCIENTS", "BETRAYAL"]
    settings_dictionary['LST_LANG'] = ["en", "de", "fr", "es"]
    return (settings_dictionary)
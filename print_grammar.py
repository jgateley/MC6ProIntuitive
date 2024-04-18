# The script for handling config/backup files
# There are two modes
#
# Base To Intuitive:
# This mode is intended to be used once, to convert your existing config to an Intuitive config
# The MIDI message names are not intuitive and should be edited
#
# Intuitive to Base (the default):
# This mode is used after an intuitive config file is changed
# It generates a new base file, which can then be restored to the controller

import argparse
import json_grammar as jg
import MC6Pro_grammar
import MC6Pro_intuitive

if __name__ == '__main__':

    base_conf = jg.JsonGrammar(MC6Pro_grammar.mc6pro_schema)
    base_grammar = base_conf.print()
    intuitive_conf = jg.JsonGrammar(MC6Pro_intuitive.mc6pro_intuitive_schema, minimal=True)
    intuitive_grammar = intuitive_conf.print()

    base_dest = "tmp/base_grammar.txt"
    intuitive_dest = "tmp/intuitive_grammar.txt"

    with open(base_dest, "w") as write_file:
        print(base_grammar, file=write_file)
    with open(intuitive_dest, "w") as write_file:
        print(intuitive_grammar, file=write_file)

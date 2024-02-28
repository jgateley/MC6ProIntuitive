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
    parser = argparse.ArgumentParser(description="MC6Pro Configuration Management")
    parser.add_argument('--base-to-intuitive', '-b', action='store_true',
                        help='Convert a base config to an intuitive config')
    parser.add_argument('source', help='The source config')
    parser.add_argument('dest', help='The destination config')
    args = parser.parse_args()

    base_conf = jg.JsonGrammar(MC6Pro_grammar.mc6pro_schema)
    intuitive_conf = jg.JsonGrammar(MC6Pro_intuitive.mc6pro_intuitive_schema, minimal=True)

    if args.base_to_intuitive:
        base_model = base_conf.load_file(args.source)

        intuitive_model = MC6Pro_intuitive.MC6ProIntuitive()
        intuitive_model.from_base(base_model)

        intuitive_conf.save_file(args.dest, intuitive_model)
    else:
        intuitive_model = intuitive_conf.load_file(args.source)

        base_model = intuitive_model.to_base()

        base_conf.save_file(args.dest, base_model)

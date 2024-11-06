# Print the grammars

import argparse
import grammar as jg
import backup_grammar
import simple_grammar
import intuitive_grammar

if __name__ == '__main__':

    backup_conf = jg.Grammar(backup_grammar.backup_schema)
    backup_grammar_obj = backup_conf.print()
    simple_conf = jg.Grammar(simple_grammar.simple_schema, minimal=True)
    simple_grammar_text = simple_conf.print()
    config_conf = jg.Grammar(intuitive_grammar.intuitive_schema, minimal=True)
    config_grammar = simple_conf.print()

    backup_dest = "tmp/backup_grammar.txt"
    simple_dest = "tmp/intuitive_grammar.txt"
    config_dest = "tmp/config_grammar.txt"

    with open(backup_dest, "w") as write_file:
        print(backup_grammar_obj, file=write_file)
    with open(simple_dest, "w") as write_file:
        print(simple_grammar_text, file=write_file)
    with open(config_dest, "w") as write_file:
        print(config_grammar, file=write_file)

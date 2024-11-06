import unittest

import backup_grammar
import simple_grammar
import grammar as jg
from version import intuitive_version
import simple_model


class IntuitiveVersionTestCase(unittest.TestCase):
    def test_version(self):
        current_version = intuitive_version
        self.assertEqual(simple_model.version_verify(current_version, None, []), current_version)

        # This should be done with bumps, once we reach a major version
        with self.assertRaises(jg.GrammarException) as context:
            simple_model.version_verify("0.2.0", None, [])
        self.assertEqual('bad_version', context.exception.args[0])


class SimpleTestCase(unittest.TestCase):

    # Recursive json comparator, allows skipping certain keys
    # locator is the bread crumb trail
    def same_json(self, json1, json2, locator, skip_keys):
        if isinstance(json1, dict):
            locator += '{'
            self.assertTrue(isinstance(json2, dict), locator)
            self.assertEqual(json1.keys(), json2.keys(), locator)
            for key in json1.keys():
                if key not in skip_keys:
                    self.same_json(json1[key], json2[key], locator + str(key) + ' ', skip_keys)
        elif isinstance(json1, int):
            self.assertTrue(isinstance(json2, int), locator)
            self.assertEqual(json1, json2, locator)
        elif isinstance(json1, str):
            self.assertTrue(isinstance(json2, str), locator)
            self.assertEqual(json1, json2, locator)
        elif isinstance(json1, list):
            self.assertTrue(isinstance(json2, list), locator)
            self.assertEqual(len(json1), len(json2), locator + " lists different length")
            for list_pos, list_elem in enumerate(json1):
                self.same_json(list_elem, json2[list_pos], locator + '[(' + str(list_pos) + ')', skip_keys)
        else:
            self.assertTrue(False, "Unknown type: " + str(type(json1)))

    def process_one_file(self, filename, extension, skip_final=False, setlist=False):
        # Parse the backup config file into a backup model
        # Convert the backup model into an simple model
        # Write the simple model to an simple config file
        # Load the simple config file to an simple model
        # Compare the reloaded simple model to the original
        # Convert the reloaded simple model to a backup model
        # Compare the reloaded backup model to the original backup model
        # Save the backup model into a backup config file
        # Load the new backup config file back into a backup model
        # Compare against the original backup model
        orig_backup_config_filename = "Configs/Test/" + filename + ".json"
        simple_config_filename = "tmp/" + filename + "_simple." + extension
        new_backup_config_filename = "tmp/" + filename + ".json"
        backup_grammar_obj = jg.Grammar(backup_grammar.backup_schema)
        backup_file = jg.GrammarFile(filename=orig_backup_config_filename)
        orig_backup_model = backup_grammar_obj.parse_config(backup_file.load())
        self.assertEqual(orig_backup_model.modified, True)

        # Convert the config model into an simple model
        orig_int_model = simple_model.Simple()
        orig_int_model.from_backup(orig_backup_model)

        # Save the simple model to a file
        int_grammar = jg.Grammar(simple_grammar.simple_schema, True)
        int_file = jg.GrammarFile(filename=simple_config_filename)
        int_file.save(int_grammar.gen_config(orig_int_model))

        # Load the simple string back to a model
        reloaded_int_grammar = jg.Grammar(simple_grammar.simple_schema, True)
        reloaded_int_file = jg.GrammarFile(simple_config_filename)
        reloaded_int_model = reloaded_int_grammar.parse_config(reloaded_int_file.load())

        # Compare the reloaded model
        if reloaded_int_model is None:
            reloaded_int_model = simple_model.Simple()
        self.assertEqual(reloaded_int_model, orig_int_model)

        # Convert the reloaded int model to a config model
        reloaded_backup_model = reloaded_int_model.to_backup()

        # And compare it to the original config model
        if setlist:
            reloaded_backup_model.midi_channels = None
        self.assertEqual(reloaded_backup_model, orig_backup_model)

        # Save a new config file
        reloaded_backup_file_grammar = jg.Grammar(backup_grammar.backup_schema)
        reloaded_backup_file = jg.GrammarFile(filename=new_backup_config_filename)
        reloaded_backup_file.save(reloaded_backup_file_grammar.gen_config(reloaded_backup_model))

        # Load the new config file
        rereloaded_backup_grammar = jg.Grammar(backup_grammar.backup_schema)
        rereloaded_backup_file = jg.GrammarFile(filename=new_backup_config_filename)
        rereloaded_backup_model = rereloaded_backup_grammar.parse_config(rereloaded_backup_file.load())
        self.assertEqual(rereloaded_backup_model, orig_backup_model)

        # Make sure the raw json is the same
        # Get rid of fields that complicate things
        if skip_final:
            return
        rereloaded_data = rereloaded_backup_file.load()
        backup_data = backup_file.load()
        rereloaded_data['downloadDate'] = ''
        rereloaded_data['hash'] = 0
        backup_data['downloadDate'] = ''
        backup_data['hash'] = 0
        if 'controller_settings' in backup_data['data']:
            # the midi clock output ports only care about the 11 LSBs
            controller_settings = backup_data['data']['controller_settings']['data']['controller_settings']
            backup_midi_clock_output_ports = controller_settings['data']['midiClockOutputPorts']
            new2_backup_midi_clock_output_ports = \
                rereloaded_data['data']['controller_settings']['data']['controller_settings']['data'][
                    'midiClockOutputPorts']
            output_ports = backup_midi_clock_output_ports & new2_backup_midi_clock_output_ports & 2047
            self.assertEqual(output_ports, 2047)
            controller_settings['data']['midiClockOutputPorts'] = output_ports
            rereloaded_data['data']['controller_settings']['data']['controller_settings']['data'][
                'midiClockOutputPorts'] = \
                output_ports
        else:
            rereloaded_data['data'].pop('controller_settings')
        self.same_json(backup_data, rereloaded_data, '',
                       ['bankMsgArray', 'sequencer_engines'])

    def test_configs_empty(self):
        self.process_one_file("Empty", "yaml")
        self.process_one_file("Empty", "json")

    def test_configs_features(self):
        self.process_one_file("Features", "yaml", True)
        self.process_one_file("Features", "json", True)

    def test_configs_MIDIClock(self):
        self.process_one_file("MIDIClock", "yaml", True)
        self.process_one_file("MIDIClock", "json", True)

    def test_configs_waveform_sequence(self):
        self.process_one_file("WaveformSequence", "yaml", True, setlist=True)
        self.process_one_file("WaveformSequence", "json", True, setlist=True)

    def test_configs_set_toggle(self):
        self.process_one_file("SetToggle", "yaml")
        self.process_one_file("Settoggle", "json")

    # def test_configs_select_exp_message(self):
    #     self.process_one_file("SelectExpMessage", "yaml", setlist=True)
    #     self.process_one_file("SelectExpMessage", "json", setlist=True)
    #
    def test_demo(self):
        backup_conf = jg.Grammar(backup_grammar.backup_schema)
        backup_file = jg.GrammarFile('tmp/Demo_test.json')
        simple_conf = jg.Grammar(simple_grammar.simple_schema, minimal=True)
        simple_file = jg.GrammarFile('Configs/Test/Demo.yaml')
        simple_model = simple_conf.parse_config(simple_file.load())
        backup_model = simple_model.to_backup()
        self.assertIsNotNone(backup_model)
        backup_file.save(backup_conf.gen_config(backup_model))


if __name__ == '__main__':
    unittest.main()

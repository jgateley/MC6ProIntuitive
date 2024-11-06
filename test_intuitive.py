import unittest

import intuitive_grammar
import simple_grammar
import grammar as jg


class MC6ProIntuitiveTestCase(unittest.TestCase):
    def process_one_file(self, filename, target_filename, do_test=True):
        # Parse the Intuitive file into an Intuitive model
        # Convert the Intuitive model into a simple model
        # Load a comparable simple file into a simple model
        # Compare the two models to see if it works

        intuitive_filename = "Configs/" + filename
        intuitive_grammar_obj = jg.Grammar(intuitive_grammar.intuitive_schema, minimal=True)
        intuitive_file = jg.GrammarFile(filename=intuitive_filename)
        intuitive_model = intuitive_grammar_obj.parse_config(intuitive_file.load())
        self.assertEqual(intuitive_model.modified, True)

        # Convert the intuitive model into a simple model
        to_simple_model = intuitive_model.to_simple()

        simple_filename = "Configs/" + target_filename
        simple_grammar_obj = jg.Grammar(simple_grammar.simple_schema, minimal=True)
        simple_file = jg.GrammarFile(filename=simple_filename)
        simple_model = simple_grammar_obj.parse_config(simple_file.load())

        if do_test:
            self.assertEqual(to_simple_model, simple_model)

    def test_intuitive_example(self):
        self.process_one_file("Example.yaml", "Test/Example_int.yaml")

    def test_intuitive_config(self):
        self.process_one_file("Config.yaml", "Test/Config_int.yaml", False)

    def test_intuitive_colors(self):
        self.process_one_file("Test/ColorTestNone.yaml", "Test/ColorTestNone_int.yaml")
        self.process_one_file("Test/ColorTestDefault.yaml", "Test/ColorTestDefault_int.yaml")

    def test_intuitive_devices(self):
        self.process_one_file('Test/DeviceTest.yaml', 'Test/DeviceTest_int.yaml')


if __name__ == '__main__':
    unittest.main()

import unittest

import MC6Pro_grammar
import MC6Pro_intuitive
import json_grammar as jg


# Helper function
def make_common_switch():
    switch_enum = jg.make_enum(['a', 'b'], default='a')
    switch_key = jg.make_key('switch', switch_enum)
    a_keys = [jg.make_key('a1', jg.make_atom(int, 1)),
              jg.make_key('a2', jg.make_atom(int, 2))]
    b_keys = [jg.make_key('b1', jg.make_atom(int, 1)),
              jg.make_key('b2', jg.make_atom(int, 2))]
    common_keys = [jg.make_key('c1', jg.make_atom(int, 1)),
                   jg.make_key('c2', jg.make_atom(int, 2))]
    test_switch = jg.make_switch_dict('test', switch_key,
                                      {'a': a_keys, 'b': b_keys}, common_keys=common_keys)
    return test_switch


# Model object used for testing
class ObjectForTests(jg.JsonGrammarModel):
    def __init__(self):
        super().__init__()
        self.x = None


# A second model object used for testing
class Object2ForTests(jg.JsonGrammarModel):
    def __init__(self):
        super().__init__()
        self.y = None


class IntuitiveMessageCatalogTestCase(unittest.TestCase):
    def test_init(self):
        messages = []
        message1 = MC6Pro_intuitive.IntuitiveMessage()
        message1.name = 'one'
        message1.type = 'Bank Jump'
        message1.page = 1
        message1.bank = 2
        messages.append(message1)
        message2 = MC6Pro_intuitive.IntuitiveMessage()
        message2.name = 'two'
        message2.type = 'Bank Jump'
        message2.page = 2
        message2.bank = 1
        messages.append(message2)

        catalog = MC6Pro_intuitive.MessageCatalog(messages)
        self.assertEqual(len(catalog.catalog), 2)
        self.assertEqual(catalog.lookup('one'), message1)
        self.assertEqual(catalog.lookup('two'), message2)

    def test_add(self):
        catalog = MC6Pro_intuitive.MessageCatalog()

        message = MC6Pro_intuitive.IntuitiveMessage()
        message.name = 'one'
        message.type = 'Bank Jump'
        message.page = 1
        message.bank = 2
        self.assertEqual(catalog.add(message), 'one')

        message.name = 'two'
        self.assertEqual(catalog.add(message), 'one')


class IntuitiveColorsCatalogTestCase(unittest.TestCase):
    def test_init(self):
        colors = []
        colors1 = MC6Pro_intuitive.ColorSchema()
        colors1.name = 'One'
        colors1.bank_color = "black"
        colors1.bank_background_color = "lime"
        colors1.preset_color = "blue"
        colors1.preset_background_color = "yellow"
        colors1.preset_toggle_color = "orchid"
        colors1.preset_toggle_background_color = "gray"
        colors.append(colors1)
        colors2 = MC6Pro_intuitive.ColorSchema()
        colors2.name = 'Two'
        colors2.bank_color = "orange"
        colors2.bank_background_color = "red"
        colors2.preset_color = "skyblue"
        colors2.preset_background_color = "deeppink"
        colors2.preset_toggle_color = "olivedrab"
        colors2.preset_toggle_background_color = "mediumslateblue"
        colors.append(colors2)
        catalog = MC6Pro_intuitive.ColorsCatalog(colors)
        self.assertEqual(len(catalog.catalog), 2)
        self.assertEqual(catalog.lookup('One'), colors1)
        self.assertEqual(catalog.lookup('Two'), colors2)

    def test_add(self):
        catalog = MC6Pro_intuitive.ColorsCatalog()

        colors1 = MC6Pro_intuitive.ColorSchema()
        colors1.name = 'One'
        colors1.bank_color = "black"
        colors1.bank_background_color = "lime"
        colors1.preset_color = "blue"
        colors1.preset_background_color = "yellow"
        colors1.preset_toggle_color = "orchid"
        colors1.preset_toggle_background_color = "gray"
        self.assertEqual(catalog.add(colors1), 'One')

        colors1.name = 'Two'
        self.assertEqual(catalog.add(colors1), 'One')


# Test the structure of the various grammar elements
# These are brittle, not the best
class JsonGrammarElementStructureTestCase(unittest.TestCase):
    # Test dict key structure
    def test_key(self):
        self.assertEqual({'name': 'key', 'schema': 1}, jg.make_key('key', 1))

    # Test dict structure, include variable, model and both and none
    def test_dict(self):
        self.assertEqual({'type': 'dictionary', 'name': 'foo', 'keys': [1, 2, 3]},
                         jg.make_dict('foo', [1, 2, 3]))
        self.assertEqual({'type': 'dictionary', 'name': 'foo', 'keys': [1, 2, 3], 'variable': 'x'},
                         jg.make_dict('foo', [1, 2, 3], var='x'))
        self.assertEqual({'type': 'dictionary', 'name': 'foo', 'keys': [1, 2, 3], 'model': ObjectForTests},
                         jg.make_dict('foo', [1, 2, 3], model=ObjectForTests))
        self.assertEqual({'type': 'dictionary', 'name': 'foo', 'keys': [1, 2, 3],
                          'variable': 'x', 'model': ObjectForTests},
                         jg.make_dict('foo', [1, 2, 3], var='x', model=ObjectForTests))

    # Test the switch dictionary, with none, var, model, and both
    def test_switch_dict(self):
        self.assertEqual({'type': 'switch_dictionary', 'name': 'foo', 'switch_key': 1,
                          'case_keys': {'a': 1}, 'common_keys': []},
                         jg.make_switch_dict('foo', 1, {'a': 1}))
        self.assertEqual({'type': 'switch_dictionary', 'name': 'foo', 'switch_key': 1,
                          'case_keys': {'a': 1}, 'common_keys': [],
                          'variable': 'x'},
                         jg.make_switch_dict('foo', 1, {'a': 1}, var='x'))
        self.assertEqual({'type': 'switch_dictionary', 'name': 'foo', 'switch_key': 1,
                          'case_keys': {'a': 1}, 'common_keys': [],
                          'model': ObjectForTests},
                         jg.make_switch_dict('foo', 1, {'a': 1}, model=ObjectForTests))
        self.assertEqual({'type': 'switch_dictionary', 'name': 'foo', 'switch_key': 1,
                          'case_keys': {'a': 1}, 'common_keys': [],
                          'variable': 'x', 'model': ObjectForTests},
                         jg.make_switch_dict('foo', 1, {'a': 1},
                                             var='x', model=ObjectForTests))

    # Test a list, with none, var, model and both
    def test_list(self):
        schema = jg.make_atom(int, value=1)
        self.assertEqual({'type': 'list', 'length': 3, 'schema': schema}, jg.make_list(3, schema))
        self.assertEqual({'type': 'list', 'length': 3, 'schema': schema, 'variable': 'x'},
                         jg.make_list(3, schema, var='x'))
        self.assertEqual({'type': 'list', 'length': 3, 'schema': schema, 'model': ObjectForTests},
                         jg.make_list(3, schema, model=ObjectForTests))
        self.assertEqual({'type': 'list', 'length': 3, 'schema': schema, 'model': ObjectForTests, 'variable': 'x'},
                         jg.make_list(3, schema, var='x', model=ObjectForTests))

    # Test the enum element structure, including none, var, model, and both
    # Also test an enum element where a default is not a member of the enum
    def test_enum(self):
        enum_base = ["one", "two", "three"]
        self.assertEqual({'type': 'enum', 'base': enum_base}, jg.make_enum(enum_base))
        self.assertEqual({'type': 'enum', 'base': enum_base, 'default': 'two'}, jg.make_enum(enum_base, "two"))
        self.assertEqual({'type': 'enum', 'base': enum_base, 'default': 'two', 'variable': 'x'},
                         jg.make_enum(enum_base, "two", var='x'))
        self.assertEqual({'type': 'enum', 'base': enum_base, 'default': 'two', 'model': ObjectForTests},
                         jg.make_enum(enum_base, "two", model=ObjectForTests))
        # Test default with incorrect value
        with self.assertRaises(jg.JsonGrammarException) as context:
            jg.make_enum(enum_base, "four")
        self.assertEqual('bad_enum_value', context.exception.args[0])

    # Test atom structure
    # Test no default nor value atom
    # Test default and value atoms
    # Test that default and value both specified is an error
    # Test var, model sepcified
    def test_atom(self):
        self.assertEqual({'type': 'atom', 'obj_type': str}, jg.make_atom(str))
        self.assertEqual({'type': 'atom', 'obj_type': str, 'default': ''}, jg.make_atom(str, ''))
        self.assertEqual({'type': 'atom', 'obj_type': str, 'value': ''}, jg.make_atom(str, value=''))

        with self.assertRaises(jg.JsonGrammarException) as context:
            jg.make_atom(int, 1, value=2)
        self.assertEqual(context.exception.args[0], 'both_value_default')

        self.assertEqual({'type': 'atom', 'obj_type': str, 'default': '', 'variable': 'x'},
                         (jg.make_atom(str, '', var='x')))
        self.assertEqual({'type': 'atom', 'obj_type': str, 'default': '', 'model': ObjectForTests},
                         jg.make_atom(str, '', model=ObjectForTests))


# Test the list pruning, compacting
# It should only remove empty elements at the end, not the middle
class ListTestCases(unittest.TestCase):
    # Test:
    # Empty list
    # List with all specified
    # List with some Nones at end
    # List with some Nones at end, and in middle
    def test_prune_list(self):
        test_list = []
        jg.prune_list(test_list)
        self.assertEqual([], test_list)

        test_list = [1, 2, 3]
        jg.prune_list(test_list)
        self.assertEqual([1, 2, 3], test_list)

        test_list = [1, 2, 3, None, None]
        jg.prune_list(test_list)
        self.assertEqual([1, 2, 3], test_list)

        test_list = [1, 2, None, 3, None, None]
        jg.prune_list(test_list)
        self.assertEqual([1, 2, None, 3], test_list)

    def test_compact_list(self):
        test_list = []
        jg.compact_list(test_list)
        self.assertEqual([], test_list)

        test_list = [1, 2, 3]
        jg.compact_list(test_list)
        self.assertEqual([1, 2, 3], test_list)

        test_list = [None, 1, 2, 3]
        jg.compact_list(test_list)
        self.assertEqual([1, 2, 3], test_list)

        test_list = [None, None, 1, 2, 3]
        jg.compact_list(test_list)
        self.assertEqual([1, 2, 3], test_list)

        test_list = [1, None, 2, 3]
        jg.compact_list(test_list)
        self.assertEqual([1, 2, 3], test_list)

        test_list = [1, None, 2, None, 3]
        jg.compact_list(test_list)
        self.assertEqual([1, 2, 3], test_list)

        test_list = [1, None, None, 2, 3]
        jg.compact_list(test_list)
        self.assertEqual([1, 2, 3], test_list)

        test_list = [1, 2, 3, None]
        jg.compact_list(test_list)
        self.assertEqual([1, 2, 3], test_list)

        test_list = [None, 1, None, None, 2, None, 3, None, None, None]
        jg.compact_list(test_list)
        self.assertEqual([1, 2, 3], test_list)


class JsonParserTestCase(unittest.TestCase):
    complete_conf = jg.JsonGrammar(None)
    minimal_conf = jg.JsonGrammar(None, True)

    def __init__(self, *args, **kwargs):
        super(JsonParserTestCase, self).__init__(*args, **kwargs)
        self.test_switch_enum = jg.make_enum(['a', 'b', 'c'], 'a')
        self.test_switch_key = jg.make_key('x', self.test_switch_enum)
        self.test_case_keys = {'a': [jg.make_key('a1', jg.make_atom(int, 1)),
                                     jg.make_key('a2', jg.make_atom(int, 2)),
                                     jg.make_key('a3', jg.make_atom(int, 3))],
                               'b': [jg.make_key('b1', jg.make_atom(int, 1)),
                                     jg.make_key('b2', jg.make_atom(int, 2)),
                                     jg.make_key('b3', jg.make_atom(int, 3))],
                               'c': [jg.make_key('c1', jg.make_atom(int, 1)),
                                     jg.make_key('c2', jg.make_atom(int, 2)),
                                     jg.make_key('c3', jg.make_atom(int, 3))]}
        self.test_switch = jg.make_switch_dict('test', self.test_switch_key, self.test_case_keys)

    # Testing an element, primarily testing vars and models
    # No difference between complete and minimal?
    def test_parse_elem(self):
        var_schema = jg.make_atom(int, 1, var='x')
        model_schema = jg.make_dict("foo",
                                    [jg.make_key("a", var_schema),
                                     jg.make_key("b", jg.make_atom(int, 1))],
                                    model=ObjectForTests)

        # Test schema is none
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.parse_elem(1, None, "foo", None, [], None)
        self.assertEqual('no_schema', context.exception.args[0])

        # Test var in schema, not modified
        model = ObjectForTests()
        self.assertIsNone(self.complete_conf.parse_elem(1, var_schema, 'foo', None, [], model))
        self.assertIsNone(model.x)

        # Test var in schema, modified
        model = ObjectForTests()
        self.assertIsNone(self.complete_conf.parse_elem(2, var_schema, 'foo', None, [], model))
        self.assertEqual(model.x, 2)

        # Test model in schema, not modified
        self.assertIsNone(self.complete_conf.parse_elem({'a': 1, 'b': 1}, model_schema, "name",
                                                        None, [], None))

        # Test model in schema, modified
        result = self.complete_conf.parse_elem({'a': 2, 'b': 1}, model_schema, "name",
                                               None, [], None)
        self.assertTrue(isinstance(result, ObjectForTests))
        self.assertEqual(True, result.modified)
        self.assertEqual(2, result.x)

        # Test model in schema, modified, but some result not added to model
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.parse_elem({'a': 2, 'b': 2}, model_schema, "foo",
                                          None, [], None)
        self.assertEqual('unconsumed', context.exception.args[0])

        # Both model and variable in schema
        inner_schema = jg.make_dict('inner',
                                    [jg.make_key('x', jg.make_atom(int, 1, var='x'))],
                                    var='y', model=ObjectForTests)
        outer_schema = jg.make_dict('outer',
                                    [jg.make_key('y', inner_schema)], model=Object2ForTests)

        # Test model not modified
        self.assertIsNone(self.complete_conf.parse_elem({'y': {'x': 1}}, outer_schema, 'outer',
                                                        None, [], None))

        # Test model modified
        outer_schema_model = self.complete_conf.parse_elem({'y': {'x': 2}}, outer_schema, 'outer',
                                                           None, [], None)
        self.assertTrue(isinstance(outer_schema_model, Object2ForTests))
        self.assertEqual(True, outer_schema_model.modified)
        inner_schema_model = outer_schema_model.y
        self.assertTrue(isinstance(inner_schema_model, ObjectForTests))
        self.assertEqual(True, inner_schema_model.modified)
        self.assertEqual(2, inner_schema_model.x)

    # Test that a var appearing as a list elem raises a multiply assigned error
    def test_var_in_list(self):
        list_schema = jg.make_list(3, jg.make_atom(int, 1, var='x'), model=ObjectForTests)
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.parse_elem([1, 2, 3], list_schema, "foo", None, [], None)
        self.assertEqual('multiply_assigned_var', context.exception.args[0])

    # Test parsing dictionaries, error cases
    # Both complete and minimal
    def test_parse_dict_errors(self):
        # Dictionary isn't a dict
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.parse_dict(1, jg.make_dict('foo', []), "foo", [], object)
        self.assertEqual('type_not_dict', context.exception.args[0])
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.minimal_conf.parse_dict(1, jg.make_dict('foo', []), "foo", [], object)
        self.assertEqual('type_not_dict', context.exception.args[0])

        # Key errors
        # elem has too many keys
        # elem has too few keys, and some are misnamed
        # elem has too few keys, complete => error, minimal => parse
        # elem has the right number of keys, but some are named wrong
        # Key appears twice in dict/schema

        # Too many keys
        test_elem = {'a': 1, 'b': 2}
        test_schema = jg.make_dict('foo', [jg.make_key('a', jg.make_atom(int, 1))])
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.parse_dict(test_elem, test_schema, "foo", [], object)
        self.assertEqual('dict_bad_keys', context.exception.args[0])
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.minimal_conf.parse_dict(test_elem, test_schema, "foo", [], object)
        self.assertEqual('dict_bad_keys', context.exception.args[0])

        # Too few keys, some are misnamed
        test_elem = {'a': 1}
        test_schema = jg.make_dict('foo', [jg.make_key('b', jg.make_atom(int, 1)),
                                           jg.make_key('c', jg.make_atom(int, 2))])
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.parse_dict(test_elem, test_schema, "foo", [], object)
        self.assertEqual('dict_bad_keys', context.exception.args[0])
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.minimal_conf.parse_dict(test_elem, test_schema, "foo", [], object)
        self.assertEqual('dict_bad_keys', context.exception.args[0])

        # Too few keys, but all correct
        test_schema = jg.make_dict('foo',
                                   [jg.make_key('a', jg.make_atom(int, 1)),
                                    jg.make_key('b', jg.make_atom(int, 2)),
                                    jg.make_key('c', jg.make_atom(int, 3))])
        test_elem = {'a': 1, 'b': 2}
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.parse_dict(test_elem, test_schema, "foo", [], object)
        self.assertEqual('dict_bad_keys', context.exception.args[0])
        self.assertIsNone(self.minimal_conf.parse_dict(test_elem, test_schema, "foo", [], object))
        test_elems = [{'a': 2}, {'b': 1}, {'a': 2, 'b': 1}]
        for test_elem in test_elems:
            with self.assertRaises(jg.JsonGrammarException) as context:
                self.complete_conf.parse_dict(test_elem, test_schema, "foo", [], object)
            self.assertEqual('dict_bad_keys', context.exception.args[0])
            self.assertEqual(test_elem, self.minimal_conf.parse_dict(test_elem, test_schema,
                                                                     "foo", [], object))

        # Has right number of keys, but name is wrong
        test_elem = {'a': 1}
        test_schema = jg.make_dict('foo', [jg.make_key('b', None)])
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.parse_dict(test_elem, test_schema, 'foo', [], object)
        self.assertEqual('dict_bad_keys', context.exception.args[0])
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.minimal_conf.parse_dict(test_elem, test_schema, 'foo', [], object)
        self.assertEqual('dict_bad_keys', context.exception.args[0])

        # Need to test when grammar is specified incorrectly, and a key appears twice in schema
        test_schema = jg.make_dict('foo', [jg.make_key('a', jg.make_atom(int, value=0)),
                                           jg.make_key('a', jg.make_atom(int, value=0))])
        test_elem = {'a': 0, 'b': 0}
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.parse_dict(test_elem, test_schema, 'foo', [], object)
        self.assertEqual('dict_duplicate_keys', context.exception.args[0])
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.minimal_conf.parse_dict(test_elem, test_schema, 'foo', [], object)
        self.assertEqual('dict_duplicate_keys', context.exception.args[0])

    # Test parsing dictionaries
    # Both complete and minimal
    def test_parse_dict(self):
        # Has right number of keys and subparsing
        test_elem = {'a': 1, 'b': 2}
        test_schema = jg.make_dict('foo',
                                   [jg.make_key('a', jg.make_atom(int, 1)),
                                    jg.make_key('b', jg.make_atom(int, 2))])
        self.assertIsNone(self.complete_conf.parse_dict(test_elem, test_schema, "foo", [], object))
        self.assertIsNone(self.minimal_conf.parse_dict(test_elem, test_schema, "foo", [], object))
        test_elems = [[{'a': 2, 'b': 2}, {'a': 2}],
                      [{'a': 1, 'b': 1}, {'b': 1}],
                      [{'a': 2, 'b': 1}, {'a': 2, 'b': 1}]]
        for test_elem in test_elems:
            self.assertEqual(test_elem[1],
                             self.complete_conf.parse_dict(test_elem[0], test_schema, "foo", [], object))
            self.assertEqual(test_elem[1],
                             self.minimal_conf.parse_dict(test_elem[0], test_schema, "foo", [], object))

    # Test parsing dictionaries context
    # Both complete and minimal
    def test_parse_dict_context(self):
        # Test that matching values work
        test_schema = jg.make_dict('foo',
                                   [jg.make_key('a', jg.make_atom(int, value=1)),
                                    jg.make_key('b', jg.make_atom(int, value=lambda elem, ctxt, lp: ctxt['a']))])
        test_value = {'a': 1, 'b': 1}
        self.assertIsNone(self.complete_conf.parse_dict(test_value, test_schema, 'foo', [], object))
        self.assertIsNone(self.minimal_conf.parse_dict(test_value, test_schema, 'foo', [], object))

        # Test values not matching work
        test_value = {'a': 1, 'b': 2}
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.parse_dict(test_value, test_schema, 'foo', [], object)
        self.assertEqual('atom_wrong_value', context.exception.args[0])
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.minimal_conf.parse_dict(test_value, test_schema, 'foo', [], object)
        self.assertEqual('atom_wrong_value', context.exception.args[0])

        # Test value works against defauts
        test_schema = jg.make_dict('foo',
                                   [jg.make_key('a', jg.make_atom(int, 1)),
                                    jg.make_key('b', jg.make_atom(int, value=lambda elem, ctxt, lp: ctxt['a']))])
        test_value = {'a': 2, 'b': 2}
        self.assertEqual({'a': 2},
                         self.complete_conf.parse_dict(test_value, test_schema, 'foo', [], object))
        self.assertEqual({'a': 2},
                         self.minimal_conf.parse_dict(test_value, test_schema, 'foo', [], object))

        test_value = {'a': 2, 'b': 3}
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.parse_dict(test_value, test_schema, 'foo', [], object)
        self.assertEqual('atom_wrong_value', context.exception.args[0])
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.minimal_conf.parse_dict(test_value, test_schema, 'foo', [], object)
        self.assertEqual('atom_wrong_value', context.exception.args[0])

        # Test defaults work
        test_schema = jg.make_dict('foo',
                                   [jg.make_key('a', jg.make_atom(int, 1)),
                                    jg.make_key('b', jg.make_atom(int, lambda elem, ctxt, lp: ctxt['a']))])
        test_value = {'a': 1, 'b': 1}
        self.assertIsNone(self.complete_conf.parse_dict(test_value, test_schema, 'foo', [], object))
        self.assertIsNone(self.minimal_conf.parse_dict(test_value, test_schema, 'foo', [], object))

        test_elems = [[{'a': 1, 'b': 2}, {'b': 2}],
                      [{'a': 2, 'b': 2}, {'a': 2}],
                      [{'a': 2, 'b': 1}, {'a': 2, 'b': 1}]]
        for test_elem in test_elems:
            self.assertEqual(test_elem[1],
                             self.complete_conf.parse_dict(test_elem[0], test_schema, "foo", [], object))
            self.assertEqual(test_elem[1],
                             self.minimal_conf.parse_dict(test_elem[0], test_schema, "foo", [], object))

    # Test parsing dictionaries, error cases
    # Both complete and minimal
    def test_parse_switch_dict_errors(self):
        # Dictionary isn't a dict
        test_elem = 1
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.parse_switch_dict(test_elem, self.test_switch, "foo", [], object)
        self.assertEqual('type_not_switch_dict', context.exception.args[0])
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.minimal_conf.parse_switch_dict(test_elem, self.test_switch, "foo", [], object)
        self.assertEqual('type_not_switch_dict', context.exception.args[0])

        # Is a dictionary, but missing switch key
        test_elem = {'a': 1}
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.parse_switch_dict(test_elem, self.test_switch, "foo", [], object)
        self.assertEqual('missing_switch', context.exception.args[0])
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.minimal_conf.parse_switch_dict(test_elem, self.test_switch, "foo", [], object)
        self.assertEqual('missing_switch', context.exception.args[0])

        # Dictionary is a dict, switch matches, but has wrong number of keys
        # Too few keys, all correct
        test_elem = {'x': 'a', 'a1': 1, 'a2': 2}
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.parse_switch_dict(test_elem, self.test_switch, "foo", [], object)
        self.assertEqual(context.exception.args[0], 'dict_bad_keys')
        self.assertIsNone(self.minimal_conf.parse_switch_dict(test_elem, self.test_switch, "foo", [], object))
        #   Too few keys, some incorrect
        test_elem = {'x': 'a', 'a1': 1, 'a4': 2}
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.parse_switch_dict(test_elem, self.test_switch, "foo", [], object)
        self.assertEqual('dict_bad_keys', context.exception.args[0])
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.minimal_conf.parse_switch_dict(test_elem, self.test_switch, "foo", [], object)
        self.assertEqual('dict_bad_keys', context.exception.args[0])
        #   Too many keys, some incorrect
        test_elem = {'x': 'a', 'a1': 1, 'a2': 2, 'a3': 3, 'a4': 4}
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.parse_switch_dict(test_elem, self.test_switch, "foo", [], object)
        self.assertEqual('dict_bad_keys', context.exception.args[0])
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.minimal_conf.parse_switch_dict(test_elem, self.test_switch, "foo", [], object)
        self.assertEqual('dict_bad_keys', context.exception.args[0])

        # switch matches Has right number of keys, but name is wrong
        test_elem = {'x': 'a', 'a1': 1, 'a2': 2, 'a4': 3}
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.parse_switch_dict(test_elem, self.test_switch, "foo", [], object)
        self.assertEqual('dict_bad_keys', context.exception.args[0])
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.minimal_conf.parse_switch_dict(test_elem, self.test_switch, "foo", [], object)
        self.assertEqual('dict_bad_keys', context.exception.args[0])

        # Need to test when grammar is specified incorrectly, and a key appears twice in schema
        switch_key = jg.make_key('x', jg.make_enum(['a', 'b']))
        case_keys = {'a': [jg.make_key('x', jg.make_atom(str, 'z'))],
                     'b': [jg.make_key('b1', jg.make_atom(int))]}
        test_switch = jg.make_switch_dict('foo', switch_key, case_keys)
        test_value = {'x': 'a', 'a1': 0}
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.parse_switch_dict(test_value, test_switch, 'foo', [], None)
        self.assertEqual('dict_duplicate_keys', context.exception.args[0])
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.minimal_conf.parse_switch_dict(test_value, test_switch, 'foo', [], None)
        self.assertEqual('dict_duplicate_keys', context.exception.args[0])
        case_keys = {'a': [jg.make_key('a1', jg.make_atom(int, value=0)),
                           jg.make_key('a1', jg.make_atom(int, 1))],
                     'b': [jg.make_key('b1', jg.make_atom(int)),
                           jg.make_key('b2', jg.make_atom(int))]}
        test_switch = jg.make_switch_dict('foo', switch_key, case_keys)
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.parse_switch_dict(test_value, test_switch, 'foo', [], None)
        self.assertEqual('dict_duplicate_keys', context.exception.args[0])
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.minimal_conf.parse_switch_dict(test_value, test_switch, 'foo', [], None)
        self.assertEqual('dict_duplicate_keys', context.exception.args[0])

    # Test parsing dictionaries
    # Both complete and minimal
    def test_parse_switch_dict(self):
        # Has right number of keys
        test_elem = {'x': 'a', 'a1': 1, 'a2': 2, 'a3': 3}
        self.assertIsNone(self.complete_conf.parse_switch_dict(test_elem, self.test_switch, "foo", [], None))
        self.assertIsNone(self.minimal_conf.parse_switch_dict(test_elem, self.test_switch, "foo", [], None))

        tests = [[{'x': 'b', 'b1': 1, 'b2': 2, 'b3': 3}, {'x': 'b'}],
                 [{'x': 'b', 'b1': 2, 'b2': 2, 'b3': 3}, {'x': 'b', 'b1': 2}],
                 [{'x': 'b', 'b1': 2, 'b2': 4, 'b3': 6}, {'x': 'b', 'b1': 2, 'b2': 4, 'b3': 6}]]
        for test in tests:
            self.assertEqual(test[1],
                             self.complete_conf.parse_switch_dict(test[0], self.test_switch, "foo", [], None))

        # Has too few keys
        test_elem = {'x': 'a', 'a1': 1, 'a2': 2}
        self.assertIsNone(self.minimal_conf.parse_switch_dict(test_elem, self.test_switch, "foo", [], None))

        test_elem = {'x': 'b', 'b1': 1, 'b2': 2}
        test_result = {'x': 'b'}
        self.assertEqual(test_result,
                         self.minimal_conf.parse_switch_dict(test_elem, self.test_switch, "foo", [], None))

        test_elem = {'x': 'b', 'b1': 2, 'b2': 2}
        test_result = {'x': 'b', 'b1': 2}
        self.assertEqual(test_result,
                         self.minimal_conf.parse_switch_dict(test_elem, self.test_switch, "foo", [], None))

    def test_parse_switch_dict_switch_var(self):
        switch_enum = jg.make_enum(['a', 'b'], var='x')
        switch_key = jg.make_key('x', switch_enum)
        case_keys = {'a': [jg.make_key('a1', jg.make_atom(int, value=1))],
                     'b': [jg.make_key('b1', jg.make_atom(int, value=1))]}
        test_switch = jg.make_switch_dict('test', switch_key, case_keys)
        test_model = ObjectForTests()

        self.assertIsNone(self.complete_conf.parse_switch_dict({'x': 'a', 'a1': 1}, test_switch, 'foo', [], test_model))
        self.assertEqual('a', test_model.x)
        test_model = ObjectForTests()
        self.assertIsNone(self.minimal_conf.parse_switch_dict({'x': 'b', 'b1': 1}, test_switch, 'foo', [], test_model))
        self.assertEqual('b', test_model.x)

    def test_parse_switch_dict_context(self):
        # Test switch dict context
        # Test non switch key is a value context function, success and failure
        switch_enum = jg.make_enum(['a', 'b'], 'a')
        switch_key = jg.make_key('x', switch_enum)
        case_keys = {'a': [jg.make_key('a1', jg.make_atom(int, value=1)),
                           jg.make_key('a2', jg.make_atom(int, value=lambda elem, ctxt, lp: ctxt['a1']))],
                     'b': [jg.make_key('b1', jg.make_atom(int, 1))]}
        test_switch = jg.make_switch_dict('test', switch_key, case_keys)

        self.assertIsNone(
            self.complete_conf.parse_switch_dict({'x': 'a', 'a1': 1, 'a2': 1}, test_switch, 'foo', [], None))
        self.assertIsNone(
            self.minimal_conf.parse_switch_dict({'x': 'a', 'a1': 1, 'a2': 1}, test_switch, 'foo', [], None))

        with self.assertRaises(jg.JsonGrammarException) as context:
            self.minimal_conf.parse_switch_dict({'x': 'a', 'a1': 1, 'a2': 2}, test_switch, 'foo', [],
                                                None)
        self.assertEqual(context.exception.args[0], 'atom_wrong_value')

        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.parse_switch_dict({'x': 'a', 'a1': 1, 'a2': 2}, test_switch, 'foo', [],
                                                 None)
        self.assertEqual(context.exception.args[0], 'atom_wrong_value')
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.minimal_conf.parse_switch_dict({'x': 'a', 'a1': 1, 'a2': 2}, test_switch, 'foo', [],
                                                None)
        self.assertEqual(context.exception.args[0], 'atom_wrong_value')

        # Test non switch key is a default context function, match and doesn't match
        case_keys = {'a': [jg.make_key('a1', jg.make_atom(int, 1)),
                           jg.make_key('a2', jg.make_atom(int, lambda elem, ctxt, lp: ctxt['a1']))],
                     'b': [jg.make_key('b1', jg.make_atom(int, 1))]}
        test_switch = jg.make_switch_dict('test', switch_key, case_keys)

        self.assertIsNone(
            self.complete_conf.parse_switch_dict({'x': 'a', 'a1': 1, 'a2': 1}, test_switch, 'foo', [], None))
        self.assertIsNone(
            self.minimal_conf.parse_switch_dict({'x': 'a', 'a1': 1, 'a2': 1}, test_switch, 'foo', [], None))

        tests = [[{'x': 'a', 'a1': 2, 'a2': 2}, {'a1': 2}],
                 [{'x': 'a', 'a1': 1, 'a2': 2}, {'a2': 2}],
                 [{'x': 'a', 'a1': 2, 'a2': 3}, {'a1': 2, 'a2': 3}]]
        for test in tests:
            self.assertEqual(test[1], self.complete_conf.parse_switch_dict(test[0], test_switch, 'foo', [], None))
            self.assertEqual(test[1], self.minimal_conf.parse_switch_dict(test[0], test_switch, 'foo', [], None))

    def test_parse_switch_dict_common_keys(self):
        test_switch = make_common_switch()
        test_elem = {'switch': 'a', 'a1': 1, 'a2': 2, 'c1': 1, 'c2': 2}
        self.assertIsNone(self.complete_conf.parse_switch_dict(test_elem, test_switch, 'test',
                                                               [], None))
        self.assertIsNone(self.minimal_conf.parse_switch_dict(test_elem, test_switch, 'test',
                                                              [], None))

    def test_parse_list(self):
        # list isn't a list
        test_schema = jg.make_list(1, jg.make_atom(int, value=1))
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.parse_list(3, test_schema, "foo", [], object)
        self.assertEqual('type_not_list', context.exception.args[0])
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.minimal_conf.parse_list(3, test_schema, "foo", [], object)
        self.assertEqual('type_not_list', context.exception.args[0])

        # List is wrong length
        test_schema = jg.make_list(2, jg.make_atom(int, value=1))
        # Too long
        test_elem = [1, 2, 3]
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.parse_list(test_elem, test_schema, "foo", [], object)
        self.assertEqual('list_bad_length', context.exception.args[0])
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.minimal_conf.parse_list(test_elem, test_schema, "foo", [], object)
        self.assertEqual('list_bad_length', context.exception.args[0])
        # Too short
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.parse_list([1], test_schema, "foo", [], object)
        self.assertEqual('list_bad_length', context.exception.args[0])

        # List is a list and right length, check list index
        test_schema = jg.make_list(3, jg.make_atom(int, value=lambda elem, ctxt, x: x[-1]))
        test_elem = [0, 1, 2]
        self.assertIsNone(self.complete_conf.parse_list(test_elem, test_schema, "foo", [], object))
        self.assertIsNone(self.minimal_conf.parse_list(test_elem, test_schema, "foo", [], object))

        # test nested lists
        test_schema = jg.make_list(3, jg.make_list(3, jg.make_atom(int, value=lambda elem, ctxt, x: x[-1] + x[-2])))
        test_elem = [[0, 1, 2], [1, 2, 3], [2, 3, 4]]
        self.assertIsNone(self.complete_conf.parse_list(test_elem, test_schema, "foo", [], object))
        self.assertIsNone(self.minimal_conf.parse_list(test_elem, test_schema, "foo", [], object))

        # Test lists with defaults
        test_schema = jg.make_list(3, jg.make_atom(int, 1))

        # test list with all matching defaults
        test_elem = [1, 1, 1]
        self.assertIsNone(self.complete_conf.parse_list(test_elem, test_schema, "foo", [], None))
        self.assertIsNone(self.minimal_conf.parse_list(test_elem, test_schema, "foo", [], None))

        # test list with matching defaults
        tests = [[[2, 1, 1], [2, None, None], [2]],
                 [[1, 2, 1], [None, 2, None], [None, 2]],
                 [[2, 2, 1], [2, 2, None], [2, 2]],
                 [[1, 1, 2], [None, None, 2], [None, None, 2]],
                 [[2, 1, 2], [2, None, 2], [2, None, 2]],
                 [[1, 2, 2], [None, 2, 2], [None, 2, 2]],
                 [[2, 2, 2], [2, 2, 2], [2, 2, 2]]]
        for test in tests:
            self.assertEqual(test[1], self.complete_conf.parse_list(test[0], test_schema, "foo", [], None))
            self.assertEqual(test[2], self.minimal_conf.parse_list(test[0], test_schema, "foo", [], None))

    def test_parse_unlimited_list(self):
        zero_list = jg.make_list(0, jg.make_atom(int, 1))

        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.parse_list([], zero_list, "foo", [], object)
        self.assertEqual('unlimited_list_complete_grammar', context.exception.args[0])

        self.assertIsNone(self.minimal_conf.parse_list([], zero_list, "foo", [], object))
        self.assertIsNone(self.minimal_conf.parse_list([1], zero_list, "foo", [], object))
        self.assertIsNone(self.minimal_conf.parse_list([1, 1, 1], zero_list, "foo", [], object))
        self.assertEqual([2], self.minimal_conf.parse_list([2], zero_list, "foo", [], object))
        self.assertEqual([None, 2, 3],
                         self.minimal_conf.parse_list([1, 2, 3], zero_list, "foo", [], object))

    def test_parse_list_minimal(self):
        test_schema = jg.make_list(10, jg.make_atom(int, default=1))

        # emptylist
        test_elem = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.assertIsNone(self.minimal_conf.parse_list(test_elem, test_schema, "foo", [], object))

        tests = [
            # full list
            [[2, 3, 4, 5, 6, 7, 8, 9, 10, 11], [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]],
            # List empty at beginning, one or two slots
            [[1, 3, 4, 5, 6, 7, 8, 9, 10, 11], [None, 3, 4, 5, 6, 7, 8, 9, 10, 11]],
            [[1, 1, 4, 5, 6, 7, 8, 9, 10, 11], [None, None, 4, 5, 6, 7, 8, 9, 10, 11]],
            # List empty at end, one or two slots
            [[2, 3, 4, 5, 6, 7, 8, 9, 10, 1], [2, 3, 4, 5, 6, 7, 8, 9, 10]],
            [[2, 3, 4, 5, 6, 7, 8, 9, 1, 1], [2, 3, 4, 5, 6, 7, 8, 9]],
            # List empty in middle, one or two slots
            [[2, 3, 4, 5, 1, 7, 8, 9, 10, 11], [2, 3, 4, 5, None, 7, 8, 9, 10, 11]],
            [[2, 3, 4, 5, 1, 1, 8, 9, 10, 11], [2, 3, 4, 5, None, None, 8, 9, 10, 11]],
            # List empty at beginning, middle and end
            [[1, 1, 4, 5, 1, 1, 8, 9, 1, 1], [None, None, 4, 5, None, None, 8, 9]],
            # Shorter list than expected
            [[2, 3, 4, 5], [2, 3, 4, 5]]
        ]

        for test in tests:
            self.assertEqual(test[1], self.minimal_conf.parse_list(test[0], test_schema, 'foo', [], ObjectForTests()))

    def test_parse_enum(self):
        test_enum = jg.make_enum(['foo', 'bar', 'baz'])
        test_enum_default = jg.make_enum(['foo', 'bar', 'baz'], 'bar')

        # enum is right type, right value
        for enum_value in test_enum['base']:
            self.assertEqual(enum_value, self.complete_conf.parse_enum(enum_value, test_enum, "test"))
            self.assertEqual(enum_value, self.minimal_conf.parse_enum(enum_value, test_enum, "test"))

        # enum has right type but wrong value
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.parse_enum('bum', test_enum, "foo")
        self.assertEqual('bad_enum_value', context.exception.args[0])
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.minimal_conf.parse_enum('bum', test_enum, "foo")
        self.assertEqual('bad_enum_value', context.exception.args[0])

        # Now test defaults
        # Atom is right type, default value
        self.assertIsNone(self.complete_conf.parse_enum('bar', test_enum_default, "foo"))
        self.assertIsNone(self.minimal_conf.parse_enum('bar', test_enum_default, "foo"))

        # Atom has right type not default value
        self.assertEqual('foo', self.complete_conf.parse_enum('foo', test_enum_default, "foo"))
        self.assertEqual('foo', self.minimal_conf.parse_enum('foo', test_enum_default, "foo"))

    def test_parse_atom_errors(self):
        # Atom has both default and value
        test_schema = jg.make_atom(str, value='123')
        test_schema['default'] = '456'
        test_elem = '3'
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.parse_atom(test_elem, test_schema, "foo", None, [], object)
        self.assertEqual('both_value_default', context.exception.args[0])
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.minimal_conf.parse_atom(test_elem, test_schema, "foo", None, [], object)
        self.assertEqual('both_value_default', context.exception.args[0])

        # Atom is wrong type
        test_schema = jg.make_atom(str, value='blah')
        test_elem = 3
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.parse_atom(test_elem, test_schema, "foo", None, [], object)
        self.assertEqual('atom_wrong_type', context.exception.args[0])
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.minimal_conf.parse_atom(test_elem, test_schema, "foo", None, [], object)
        self.assertEqual('atom_wrong_type', context.exception.args[0])

    def atom_tests(self, test_schema):
        test_elem = 3
        self.assertIsNone(self.complete_conf.parse_atom(test_elem, test_schema, "foo", None, [], object))
        self.assertIsNone(self.minimal_conf.parse_atom(test_elem, test_schema, "foo", None, [], object))

        # Atom has right type but wrong value
        test_elem = 4
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.parse_atom(test_elem, test_schema, "foo", None, [], object)
        self.assertEqual('atom_wrong_value', context.exception.args[0])
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.minimal_conf.parse_atom(test_elem, test_schema, "foo", None, [], object)
        self.assertEqual('atom_wrong_value', context.exception.args[0])

    def test_parse_atom(self):
        # Atom is right type, right value
        self.atom_tests(jg.make_atom(int, value=3))

        # Atom is right type, right value via function
        self.atom_tests(jg.make_atom(int, value=lambda elem, ctxt, lp: 3))

        # Now test defaults
        # Atom is right type, default value
        test_schema = jg.make_atom(int, 3)
        test_elem = 3
        self.assertIsNone(self.complete_conf.parse_atom(test_elem, test_schema, "foo", None, [], object))
        self.assertIsNone(self.minimal_conf.parse_atom(test_elem, test_schema, "foo", None, [], object))

        # Atom has right type not default value
        test_elem = 4
        self.assertEqual(test_elem, self.complete_conf.parse_atom(test_elem, test_schema, "foo", None, [], object))
        self.assertEqual(test_elem, self.minimal_conf.parse_atom(test_elem, test_schema, "foo", None, [], object))

        # Atom is right type, default value via function
        test_schema = jg.make_atom(int, lambda elem, ctxt, lp: 3)
        test_elem = 3
        self.assertIsNone(self.complete_conf.parse_atom(test_elem, test_schema, "foo", None, [], object))
        self.assertIsNone(self.minimal_conf.parse_atom(test_elem, test_schema, "foo", None, [], object))

        # Atom is right type but wrong value via function
        test_elem = 4
        self.assertEqual(test_elem, self.complete_conf.parse_atom(test_elem, test_schema, "foo", None, [], object))
        self.assertEqual(test_elem, self.minimal_conf.parse_atom(test_elem, test_schema, "foo", None, [], object))


class JsonGeneratorTestCase(unittest.TestCase):
    complete_conf = jg.JsonGrammar(None)
    minimal_conf = jg.JsonGrammar(None, True)

    def test_atom(self):
        # Value Atom, int, int from a function, string and bool
        value_int_atom = jg.make_atom(int, value=1)
        value_int_fn_atom = jg.make_atom(int, value=lambda elem, ctxt, lp: 1)
        value_str_atom = jg.make_atom(str, value="a")
        value_bool_atom = jg.make_atom(bool, value=True)

        default_int_atom = jg.make_atom(int, 1)
        default_int_fn_atom = jg.make_atom(int, lambda elem, ctxt, lp: 1)
        default_str_atom = jg.make_atom(str, "a")
        default_bool_atom = jg.make_atom(bool, True)

        # Val atom w/ incorrect value
        tests = [
            [2, value_int_atom],
            [2, value_int_fn_atom],
            ['b', value_str_atom],
            [False, value_bool_atom]
        ]

        for test in tests:
            with self.assertRaises(jg.JsonGrammarException) as context:
                self.complete_conf.gen_atom(test[0], test[1], None, [])
            self.assertEqual('model_schema_mismatch', context.exception.args[0])
            with self.assertRaises(jg.JsonGrammarException) as context:
                self.minimal_conf.gen_atom(test[0], test[1], None, [])
            self.assertEqual('model_schema_mismatch', context.exception.args[0])

        test_model = ObjectForTests()
        tests = [
            # Val atom w/ None,
            [None, value_int_atom, 1, 1],
            [None, value_int_fn_atom, 1, 1],
            [None, value_str_atom, 'a', 'a'],
            [None, value_bool_atom, True, True],
            # Val atom w/ correct value
            [1, value_int_atom, 1, None],
            [1, value_int_fn_atom, 1, None],
            ['a', value_str_atom, 'a', None],
            [True, value_bool_atom, True, None],
            # Val atom with model value
            [test_model, value_int_atom, 1, 1],
            [test_model, value_int_fn_atom, 1, 1],
            [test_model, value_str_atom, 'a', 'a'],
            [test_model, value_bool_atom, True, True],
            # Def Atom with none
            [None, default_int_atom, 1, None],
            [None, default_int_fn_atom, 1, None],
            [None, default_str_atom, 'a', None],
            [None, default_bool_atom, True, None],
            # Def Atom with default
            [1, default_int_atom, 1, None],
            [1, default_int_fn_atom, 1, None],
            ['a', default_str_atom, 'a', None],
            [True, default_bool_atom, True, None],
            # Def Atom with value different than default
            [2, default_int_atom, 2, 2],
            [2, default_int_fn_atom, 2, 2],
            ['b', default_str_atom, 'b', 'b'],
            [False, default_bool_atom, False, False],
            # Def atom with an (unused) model
            [test_model, default_int_atom, 1, None],
            [test_model, default_int_fn_atom, 1, None],
            [test_model, default_str_atom, 'a', None],
            [test_model, default_bool_atom, True, None]
        ]

        for test in tests:
            self.assertEqual(test[2], self.complete_conf.gen_atom(test[0], test[1], None, []))
            self.assertEqual(test[3], self.minimal_conf.gen_atom(test[0], test[1], None, []))

    def test_enum(self):
        test_enum = jg.make_enum(["one", "two", "three", "four"])
        test_default_enum = jg.make_enum(["one", "two", "three", "four"], default="one")
        test_model = ObjectForTests()

        tests = [
            # Enum with no model value
            [None, test_enum],
        ]

        for test in tests:
            with self.assertRaises(jg.JsonGrammarException) as context:
                self.complete_conf.gen_enum(test[0], test[1], None, [])
            self.assertEqual('enum_no_default', context.exception.args[0])
            with self.assertRaises(jg.JsonGrammarException) as context:
                self.minimal_conf.gen_enum(test[0], test[1], None, [])
            self.assertEqual('enum_no_default', context.exception.args[0])

        tests = [
            # Enum with no model value
            [None, test_default_enum, "one", None, "default no model"],
            # Enum with model value, same and different than default
            ["one", test_enum, "one", "one", "no default model==1"],
            ["one", test_default_enum, "one", None, "default model==1"],
            ["two", test_enum, "two", "two", "no default model==2"],
            ["two", test_default_enum, "two", "two", "default model==2"],
            # Def atom with an (unused) model
            [test_model, test_default_enum, "one", None, "model object default"]
        ]

        for test in tests:
            self.assertEqual(test[2], self.complete_conf.gen_enum(test[0], test[1], None, []), test[4])
            self.assertEqual(test[3], self.minimal_conf.gen_enum(test[0], test[1], None, []), test[4])

    def test_list(self):
        test_value_schema = jg.make_list(3, jg.make_atom(int, value=1))
        test_unlimited_value_schema = jg.make_list(0, jg.make_atom(int, value=1))
        test_value_fn_schema = jg.make_list(3, jg.make_atom(int, value=lambda elem, ctxt, lp: lp[-1] * lp[-2]))
        test_default_schema = jg.make_list(3, jg.make_atom(int, 1))
        test_unlimited_default_schema = jg.make_list(0, jg.make_atom(int, 1))
        test_default_fn_schema = jg.make_list(3, jg.make_atom(int, lambda elem, ctxt, lp: lp[-1] * lp[-2]))

        # Test list is wrong length
        tests = [
            # Test model is not a list, raises assertion
            ["model not a list", 3, 'model_schema_mismatch'],
            ["wrong length list", [1, 1, 1, 1], 'list_bad_length']
        ]

        for test in tests:
            with self.assertRaises(jg.JsonGrammarException) as context:
                self.complete_conf.gen_list(test[1], test_value_schema, [])
            self.assertEqual(test[2], context.exception.args[0])
            with self.assertRaises(jg.JsonGrammarException) as context:
                self.minimal_conf.gen_list(test[1], test_value_schema, [])
            self.assertEqual(test[2], context.exception.args[0])

        # Test model is None
        self.assertEqual([1, 1, 1], self.complete_conf.gen_list(None, test_value_schema, [2]))
        self.assertEqual([1, 1, 1], self.minimal_conf.gen_list(None, test_value_schema, [2]))
        self.assertEqual([], self.complete_conf.gen_list(None, test_unlimited_value_schema, [2]))
        self.assertIsNone(self.minimal_conf.gen_list(None, test_unlimited_value_schema, [2]))
        self.assertEqual([0, 2, 4], self.complete_conf.gen_list(None, test_value_fn_schema, [2]))
        self.assertEqual([0, 2, 4], self.minimal_conf.gen_list(None, test_value_fn_schema, [2]))
        self.assertEqual([1, 1, 1], self.complete_conf.gen_list(None, test_default_schema, [2]))
        self.assertIsNone(self.minimal_conf.gen_list(None, test_default_schema, [2]))
        self.assertEqual([], self.complete_conf.gen_list(None, test_unlimited_default_schema, [2]))
        self.assertIsNone(self.minimal_conf.gen_list(None, test_unlimited_default_schema, [2]))
        self.assertEqual([0, 2, 4], self.complete_conf.gen_list(None, test_default_fn_schema, [2]))
        self.assertIsNone(self.minimal_conf.gen_list(None, test_default_fn_schema, [2]))

        # Test model is model, but no need to test variable, handled by test_elem
        test_obj = ObjectForTests()
        self.assertEqual([1, 1, 1], self.complete_conf.gen_list(test_obj, test_value_schema, [2]))
        self.assertEqual([1, 1, 1], self.minimal_conf.gen_list(test_obj, test_value_schema, [2]))
        self.assertEqual([], self.complete_conf.gen_list(test_obj, test_unlimited_value_schema, [2]))
        self.assertIsNone(self.minimal_conf.gen_list(test_obj, test_unlimited_value_schema, [2]))
        self.assertEqual([0, 2, 4], self.complete_conf.gen_list(test_obj, test_value_fn_schema, [2]))
        self.assertEqual([0, 2, 4], self.minimal_conf.gen_list(test_obj, test_value_fn_schema, [2]))
        self.assertEqual([1, 1, 1], self.complete_conf.gen_list(test_obj, test_default_schema, [2]))
        self.assertIsNone(self.minimal_conf.gen_list(test_obj, test_default_schema, [2]))
        self.assertEqual([], self.complete_conf.gen_list(test_obj, test_unlimited_default_schema, [2]))
        self.assertIsNone(self.minimal_conf.gen_list(test_obj, test_unlimited_default_schema, [2]))
        self.assertEqual([0, 2, 4], self.complete_conf.gen_list(test_obj, test_default_fn_schema, [2]))
        self.assertIsNone(self.minimal_conf.gen_list(test_obj, test_default_fn_schema, [2]))

        # Test model is list, and uses a function relying on list_pos, including nested list_pos
        self.assertEqual([1, 1, 1], self.complete_conf.gen_list([1, 1, 1], test_value_schema, [2]))
        self.assertIsNone(self.minimal_conf.gen_list([1, 1, 1], test_value_schema, [2]))
        self.assertEqual([1, 1, 1], self.complete_conf.gen_list([1, 1, 1], test_unlimited_value_schema, [2]))
        self.assertIsNone(self.minimal_conf.gen_list([1, 1, 1], test_unlimited_value_schema, [2]))
        self.assertEqual([0, 2, 4], self.complete_conf.gen_list([0, 2, 4], test_value_fn_schema, [2]))
        self.assertIsNone(self.minimal_conf.gen_list([0, 2, 4], test_value_fn_schema, [2]))
        self.assertEqual([1, 1, 1], self.complete_conf.gen_list([1, 1, 1], test_default_schema, [2]))
        self.assertIsNone(self.minimal_conf.gen_list([1, 1, 1], test_default_schema, [2]))
        self.assertEqual([1, 1, 1], self.complete_conf.gen_list([1, 1, 1], test_unlimited_default_schema, [2]))
        self.assertIsNone(self.minimal_conf.gen_list([1, 1, 1], test_unlimited_default_schema, [2]))
        self.assertEqual([0, 2, 4], self.complete_conf.gen_list([0, 2, 4], test_default_fn_schema, [2]))
        self.assertIsNone(self.minimal_conf.gen_list([0, 2, 4], test_default_fn_schema, [2]))

    def test_gen_list_minimal(self):
        test_schema = jg.make_list(10, jg.make_atom(int, default=1))
        # Test a full list
        full_list = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        full_list_res = full_list
        result = self.minimal_conf.gen_list(full_list, test_schema, [])
        self.assertEqual(result, full_list_res)
        # Empty list
        empty_list = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        result = self.minimal_conf.gen_list(empty_list, test_schema, [])
        self.assertIsNone(result)
        # List empty at beginning, one or two slots
        begin1_list = [1, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        begin1_list_res = [None, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        result = self.minimal_conf.gen_list(begin1_list, test_schema, [])
        self.assertEqual(result, begin1_list_res)
        begin2_list = [1, 1, 4, 5, 6, 7, 8, 9, 10, 11]
        begin2_list_res = [None, None, 4, 5, 6, 7, 8, 9, 10, 11]
        result = self.minimal_conf.gen_list(begin2_list, test_schema, [])
        self.assertEqual(result, begin2_list_res)
        # List empty at end, one or two slots
        end1_list = [2, 3, 4, 5, 6, 7, 8, 9, 10, 1]
        end1_list_res = [2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = self.minimal_conf.gen_list(end1_list, test_schema, [])
        self.assertEqual(result, end1_list_res)
        end2_list = [2, 3, 4, 5, 6, 7, 8, 9, 1, 1]
        end2_list_res = [2, 3, 4, 5, 6, 7, 8, 9]
        result = self.minimal_conf.gen_list(end2_list, test_schema, [])
        self.assertEqual(result, end2_list_res)
        # List empty in middle, one or two slots
        middle1_list = [2, 3, 4, 5, 1, 7, 8, 9, 10, 11]
        middle1_list_res = [2, 3, 4, 5, None, 7, 8, 9, 10, 11]
        result = self.minimal_conf.gen_list(middle1_list, test_schema, [])
        self.assertEqual(result, middle1_list_res)
        middle2_list = [2, 3, 4, 5, 1, 1, 8, 9, 10, 11]
        middle2_list_res = [2, 3, 4, 5, None, None, 8, 9, 10, 11]
        result = self.minimal_conf.gen_list(middle2_list, test_schema, [])
        self.assertEqual(result, middle2_list_res)
        # List empty at beginning, middle and end
        complex_list = [1, 1, 4, 5, 1, 1, 8, 9, 1, 1]
        complex_list_res = [None, None, 4, 5, None, None, 8, 9]
        result = self.minimal_conf.gen_list(complex_list, test_schema, [])
        self.assertEqual(result, complex_list_res)

    def test_gen_dict(self):
        test_schema = jg.make_dict('foo',
                                   [jg.make_key('a', jg.make_atom(int, value=1)),
                                    jg.make_key('b', jg.make_atom(int, value=2)),
                                    jg.make_key('c', jg.make_atom(int, value=3))])
        test_result = {'a': 1, 'b': 2, 'c': 3}

        # Test dict is not a dict, raises assertion
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.gen_dict(3, test_schema, [])
        self.assertEqual('type_not_dict', context.exception.args[0])

        # Test dict is None
        self.assertEqual(test_result, self.complete_conf.gen_dict(None, test_schema, []))

        # Test dict is model, but no need to test variable, handled by test_elem
        self.assertEqual(test_result, self.complete_conf.gen_dict(ObjectForTests(), test_schema, []))

        # Test dict is a dict, but too few keys
        self.assertEqual(test_result, self.complete_conf.gen_dict({'a': 1, 'b': 2}, test_schema, []),)

        # Test dict is a dict, right number of keys, but key name mismatch
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.gen_dict({'a': 1, 'b': 2, 'd': 3}, test_schema, [])
        self.assertEqual('dict_bad_keys', context.exception.args[0])

        # Test dict is a dict
        self.assertEqual(test_result, self.complete_conf.gen_dict(test_result, test_schema, []))

    def test_gen_dict_context(self):
        # Test ordering of keys, they are added in order of appearance
        # That is the firt two tests here
        # Test value function: None as model produces appropriate value
        test_schema = jg.make_dict('foo',
                                   [jg.make_key('a', jg.make_atom(int, value=1)),
                                    jg.make_key('b', jg.make_atom(int, value=lambda elem, ctxt, lp: ctxt['a']))])
        self.assertEqual({'a': 1, 'b': 1}, self.complete_conf.gen_dict(None, test_schema, []))

        # Test value function: None as model, improper ordering fails
        test_schema = jg.make_dict('foo',
                                   [jg.make_key('a', jg.make_atom(int, value=lambda elem, ctxt, lp: ctxt['b'])),
                                    jg.make_key('b', jg.make_atom(int, value=1))])
        with self.assertRaises(KeyError) as context:
            self.complete_conf.gen_dict(None, test_schema, [])
        self.assertEqual('b', context.exception.args[0])

        # Test default function:
        # None as model produces appropriate entry
        test_schema = jg.make_dict('foo',
                                   [jg.make_key('a', jg.make_atom(int, default=1)),
                                    jg.make_key('b', jg.make_atom(int, default=lambda elem, ctxt, lp: ctxt['a']))])
        self.assertEqual({'a': 1, 'b': 1}, self.complete_conf.gen_dict(None, test_schema, []))

        #  Non default as model produces appropriate entry
        test_schema = jg.make_dict('foo',
                                   [jg.make_key('a', jg.make_atom(int, default=1)),
                                    jg.make_key('b', jg.make_atom(int, default=lambda elem, ctxt, lp: ctxt['a']))])
        self.assertEqual({'a': 2}, self.minimal_conf.gen_dict({'a': 2}, test_schema, []))
        self.assertEqual({'b': 2}, self.minimal_conf.gen_dict({'b': 2}, test_schema, []))

    def test_gen_dict_minimal(self):
        test_schema = jg.make_dict('test',
                                   [jg.make_key('a', jg.make_atom(int, 1)),
                                    jg.make_key('b', jg.make_atom(int, 1)),
                                    jg.make_key('c', jg.make_atom(int, 1)),
                                    jg.make_key('d', jg.make_atom(int, 1))])

        # Test that None produces None
        self.assertIsNone(self.minimal_conf.gen_dict(None, test_schema, []))

        # Test that no keys appearing produced None
        self.assertIsNone(self.minimal_conf.gen_dict({}, test_schema, []))

        # Test wrong key out of all
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.minimal_conf.gen_dict({'e': 1}, test_schema, [])
        self.assertEqual('dict_bad_keys', context.exception.args[0])

        # Test one key out of all
        self.assertEqual({"a": 2}, self.minimal_conf.gen_dict({'a': 2}, test_schema, []))
        # Test two keys out of all
        self.assertEqual({"a": 2, 'c': 3}, self.minimal_conf.gen_dict({'a': 2, 'c': 3}, test_schema, []))
        # Test all keys out of all
        self.assertEqual({"a": 2, 'b': 4, 'c': 3, 'd': 5},
                         self.minimal_conf.gen_dict({'a': 2, 'b': 4, 'c': 3, 'd': 5}, test_schema, []))

    def test_gen_switch_dict(self):
        test_case_keys = {'a': [jg.make_key('d', jg.make_atom(int, 1))],
                          'b': [jg.make_key('e', jg.make_atom(int, 1))],
                          'c': [jg.make_key('f', jg.make_atom(int, 1))]}
        test_enum = jg.make_enum(["a", "b", "c"])
        test_enum_default = jg.make_enum(["a", "b", "c"], "a")
        test_switch_dict_schema = jg.make_switch_dict('test', jg.make_key('switch', test_enum_default), test_case_keys)
        test_switch_dict_default_schema = jg.make_switch_dict('test', jg.make_key('switch', test_enum), test_case_keys)

        # Test switch dict model is None, enum has default
        self.assertEqual({'switch': 'a', 'd': 1},
                         self.complete_conf.gen_switch_dict(None, test_switch_dict_schema, []))

        # Test switch dict model is None, enum doesn't have default
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.gen_switch_dict(None, test_switch_dict_default_schema, [])
        self.assertEqual('enum_no_default', context.exception.args[0])

        # Test switch dict model is a model, no variable (that test handled by test_elem), enum has default
        self.assertEqual({'switch': 'a', 'd': 1},
                         self.complete_conf.gen_switch_dict(ObjectForTests(), test_switch_dict_schema, []))

        # Test switch dict model is a model, no variable (that test handled by test_elem), enum has no default
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.gen_switch_dict(ObjectForTests(), test_switch_dict_default_schema, [])
        self.assertEqual('enum_no_default', context.exception.args[0])

        # Test switch dict model is a dict, but wrong number of keys
        test_model = {'switch': 'b', 'e': 1, 'f': 1}
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.gen_switch_dict(test_model, test_switch_dict_schema, [])
        self.assertEqual('dict_bad_keys', context.exception.args[0])
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.minimal_conf.gen_switch_dict(test_model, test_switch_dict_schema, [])
        self.assertEqual('dict_bad_keys', context.exception.args[0])

        # Test switch dict model is a dict, right number of keys, but wrong keys
        test_model = {'switch': 'b', 'd': 1}
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.gen_switch_dict(test_model, test_switch_dict_schema, [])
        self.assertEqual('dict_bad_keys', context.exception.args[0])
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.minimal_conf.gen_switch_dict(test_model, test_switch_dict_schema, [])
        self.assertEqual('dict_bad_keys', context.exception.args[0])

        # Test switch dict has an invalid switch field
        test_model = {'switch': 'd', 'd': 1}
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.gen_switch_dict(test_model, test_switch_dict_schema, [])
        self.assertEqual('switch_dict_bad_switch', context.exception.args[0])
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.minimal_conf.gen_switch_dict(test_model, test_switch_dict_schema, [])
        self.assertEqual('switch_dict_bad_switch', context.exception.args[0])

        # Test switch dict has a valid switch field
        test_model = {'switch': 'a', 'd': 1}
        self.assertEqual({'switch': 'a', 'd': 1},
                         self.complete_conf.gen_switch_dict(test_model, test_switch_dict_schema, []))

    def test_switch_dict_context(self):
        # Functions cannot appear as switch
        # Test value function: None as model produces appropriate value
        # Test default function:
        #  None as model produces appropriate entry
        #  Non default as model produces appropriate entry
        # Must test ordering where keys added to context
        test_switch_key = jg.make_key('switch', jg.make_enum(["a", "b"], "a"))
        test_case_keys = {'a': [jg.make_key('a1', jg.make_atom(int, value=1)),
                                jg.make_key('a2', jg.make_atom(int, value=lambda elem, ctxt, lp: ctxt['a1']))],
                          'b': [jg.make_key('b1', jg.make_atom(int, value=1)),
                                jg.make_key('b2', jg.make_atom(int, value=lambda elem, ctxt, lp: ctxt['b1']))]}
        test_schema = jg.make_switch_dict('test', test_switch_key, test_case_keys)
        # Test value function: None as model produces appropriate value
        self.assertEqual({'switch': 'a', 'a1': 1, 'a2': 1},
                         self.complete_conf.gen_switch_dict(None, test_schema, []))
        self.assertEqual({'a1': 1, 'a2': 1},
                         self.minimal_conf.gen_switch_dict(None, test_schema, []))

        # Test value function: None as model, improper ordering fails
        test_case_keys = {'a': [jg.make_key('a1',
                                            jg.make_atom(int, value=lambda elem, ctxt, lp: ctxt['a2'])),
                                jg.make_key('a2', jg.make_atom(int, value=1))],
                          'b': [jg.make_key('b1', jg.make_atom(int, value=1)),
                                jg.make_key('b2', jg.make_atom(int, value=lambda elem, ctxt, lp: ctxt['b1']))]}
        test_schema = jg.make_switch_dict('test', test_switch_key, test_case_keys)
        with self.assertRaises(KeyError) as context:
            self.complete_conf.gen_switch_dict(None, test_schema, [])
        self.assertEqual('a2', context.exception.args[0])

        # Test default function:
        #  None as model produces appropriate entry
        test_case_keys = {'a': [jg.make_key('a1', jg.make_atom(int, 1)),
                                jg.make_key('a2', jg.make_atom(int, lambda elem, ctxt, lp: ctxt['a1']))],
                          'b': [jg.make_key('b1', jg.make_atom(int, 1)),
                                jg.make_key('b2', jg.make_atom(int, lambda elem, ctxt, lp: ctxt['b1']))]}
        test_schema = jg.make_switch_dict('test', test_switch_key, test_case_keys)
        self.assertEqual({'switch': 'a', 'a1': 1, 'a2': 1},
                         self.complete_conf.gen_switch_dict(None, test_schema, []))

        #  Non default as model produces appropriate entry
        self.assertEqual({'switch': 'a', 'a1': 2, 'a2': 2},
                         self.complete_conf.gen_switch_dict({'switch': 'a', 'a1': 2}, test_schema, []))
        self.assertEqual({'switch': 'a', 'a1': 2, 'a2': 4},
                         self.complete_conf.gen_switch_dict({'switch': 'a', 'a1': 2, 'a2': 4}, test_schema, []))
        self.assertEqual({'switch': 'b', 'b1': 2, 'b2': 2},
                         self.complete_conf.gen_switch_dict({'switch': 'b', 'b1': 2}, test_schema, []))
        self.assertEqual({'switch': 'b', 'b1': 2, 'b2': 4},
                         self.complete_conf.gen_switch_dict({'switch': 'b', 'b1': 2, 'b2': 4}, test_schema, []))
        self.assertEqual({'switch': 'b', 'b1': 2, 'b2': 4},
                         self.minimal_conf.gen_switch_dict({'switch': 'b', 'b1': 2, 'b2': 4}, test_schema, []))

    def test_switch_dict_minimal(self):
        test_switch_key = jg.make_key('switch', jg.make_enum(["a", "b", "c"], "a"))
        test_schema = jg.make_switch_dict('test', test_switch_key,
                                          {'a': [jg.make_key('d', jg.make_atom(int, 1))],
                                           'b': [jg.make_key('e', jg.make_atom(int, 1))],
                                           'c': [jg.make_key('f', jg.make_atom(int, 1))]})

        # Test switch dict model is None,
        self.assertIsNone(self.minimal_conf.gen_switch_dict(None, test_schema, []))

        # Test switch dict is a model, no variable (that test handled by test_elem), and enum is default
        # There is no non-default case here?
        self.assertIsNone(self.minimal_conf.gen_switch_dict(ObjectForTests(), test_schema, []))

        # Test switch dict has a valid switch field
        test_model = {'switch': 'b', 'e': 2}
        self.assertEqual({'switch': 'b', 'e': 2}, self.minimal_conf.gen_switch_dict(test_model, test_schema, []))

    def test_gen_switch_dict_common_keys(self):
        test_switch = make_common_switch()
        full_result = {'switch': 'a', 'a1': 1, 'a2': 2, 'c1': 1, 'c2': 2}
        self.assertEqual(self.complete_conf.gen_switch_dict(None, test_switch, []), full_result)
        self.assertIsNone(self.minimal_conf.gen_switch_dict(None, test_switch, []))

    def test_elem(self):
        # Test schema is None
        with self.assertRaises(jg.JsonGrammarException) as context:
            self.complete_conf.gen_elem(1, None, None, [])
        self.assertEqual('no_schema', context.exception.args[0])

        # Test dictionary
        test_schema = jg.make_dict('foo',
                                   [jg.make_key('a', jg.make_atom(int, value=1)),
                                    jg.make_key('b', jg.make_atom(int, value=2)),
                                    jg.make_key('c', jg.make_atom(int, value=3))])
        test_result = {'a': 1, 'b': 2, 'c': 3}
        self.assertEqual(test_result, self.complete_conf.gen_elem(test_result, test_schema, None, []))

        # Test list
        test_schema = jg.make_list(3, jg.make_atom(int, value=1))
        self.assertEqual([1, 1, 1], self.complete_conf.gen_elem(None, test_schema, None, [2]))

        # Test atom
        test_schema = jg.make_atom(int, value=1)
        self.assertEqual(1, self.complete_conf.gen_elem(1, test_schema, None, []))

        # Test variable expansion
        test_model = ObjectForTests()
        test_model.x = 3
        test_schema = jg.make_atom(int, 1, var='x')
        self.assertEqual(3, self.complete_conf.gen_elem(test_model, test_schema, None, []), 3)


class IntuitiveTestCases(unittest.TestCase):
    def test_colors_schema(self):
        self.assertEqual(MC6Pro_intuitive.ColorSchema.from_base_bank_color(None), "default")
        self.assertEqual(MC6Pro_intuitive.ColorSchema.from_base_bank_color(127), "default")
        self.assertEqual(MC6Pro_intuitive.ColorSchema.from_base_bank_color(7), "white")
        self.assertIsNone(MC6Pro_intuitive.ColorSchema.to_base_bank_color("default"))
        self.assertEqual(MC6Pro_intuitive.ColorSchema.to_base_bank_color("white"), 7)
        self.assertEqual(MC6Pro_intuitive.ColorSchema.from_base_preset_color(None, False), "white")
        self.assertEqual(MC6Pro_intuitive.ColorSchema.from_base_preset_color(None, True), "black")
        self.assertEqual(MC6Pro_intuitive.ColorSchema.from_base_preset_color(0, False), "black")
        self.assertEqual(MC6Pro_intuitive.ColorSchema.from_base_preset_color(7, True), "white")
        self.assertEqual(MC6Pro_intuitive.ColorSchema.from_base_preset_color(4, False), "yellow")
        self.assertIsNone(MC6Pro_intuitive.ColorSchema.to_base_preset_color("black", True))
        self.assertIsNone(MC6Pro_intuitive.ColorSchema.to_base_preset_color("white", False))
        self.assertEqual(MC6Pro_intuitive.ColorSchema.to_base_preset_color("yellow", True), 4)
        self.assertEqual(MC6Pro_intuitive.ColorSchema.to_base_preset_color("yellow", False), 4)

    def test_IntuitiveMidiMessage_eq(self):
        msg1 = MC6Pro_intuitive.IntuitiveMessage()
        msg2 = MC6Pro_intuitive.IntuitiveMessage()

        msg1.type = "PC"
        msg2.type = "CC"
        self.assertFalse(msg1 == msg2)

        msg2.type = "PC"
        msg1.channel = "channel1"
        msg2.channel = "channel2"
        self.assertFalse(msg1 == msg2)

        msg2.channel = "channel1"
        msg1.number = 1
        msg2.number = 2
        self.assertFalse(msg1 == msg2)

        msg1.number = 2
        self.assertTrue(msg1 == msg2)

        msg1.name = "msg1"
        msg2.name = "msg2"
        msg1.value = 1
        msg2.value = 2
        msg1.bank = 1
        msg2.bank = 2
        self.assertTrue(msg1 == msg2)

        msg1.type = "CC"
        msg2.type = "CC"
        msg1.value = 1
        msg2.value = 2
        self.assertFalse(msg1 == msg2)

        msg2.value = 1
        self.assertTrue(msg1 == msg2)

        msg1.value = 1
        msg1.number = 1
        msg2.value = 2
        msg2.number = 2

        msg1.type = "Bank Jump"
        msg2.type = "Bank Jump"
        msg1.page = 1
        msg1.bank = 1
        msg2.page = 1
        msg2.bank = 2
        self.assertFalse(msg1 == msg2)

        msg2.bank = 1
        msg2.page = 2
        self.assertFalse(msg1 == msg2)

        msg2.page = 1
        self.assertTrue(msg1 == msg2)

        msg2.bank = 2
        msg2.page = 2
        msg1.type = 'Page Jump'
        msg2.type = 'Page Jump'
        self.assertFalse(msg1 == msg2)

        msg2.page = 1
        self.assertTrue(msg1 == msg2)

        msg1.type = 'Toggle Page'
        msg2.type = 'Toggle Page'
        msg1.page_up = True
        msg2.page_up = False
        self.assertFalse(msg1 == msg2)

        msg2.page_up = True
        self.assertTrue(msg1 == msg2)


class IntuitiveFromBaseTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(IntuitiveFromBaseTestCase, self).__init__(*args, **kwargs)
        self.midi_channels = []
        for i in range(1, 4):
            midi_channel = MC6Pro_intuitive.IntuitiveMidiChannel()
            midi_channel.name = 'channel' + str(i)
            self.midi_channels.append(midi_channel)
        self.catalog = MC6Pro_intuitive.MessageCatalog()

    @staticmethod
    def mk_base_method(channel, base_type, msg_array):
        base_message = MC6Pro_grammar.MidiMessage()
        base_message.channel = channel
        base_message.type = base_type
        base_message.msg_array_data = msg_array
        return base_message

    @staticmethod
    def mk_message(name, channel, message_type, number, value):
        message = MC6Pro_intuitive.IntuitiveMessage()
        message.name = name
        message.channel = channel
        message.type = message_type
        message.number = number
        message.value = value
        return message

    def test_intuitive_midi_message(self):

        # Test adding the first MIDI message
        base_message = self.mk_base_method(None, 1, [None, None])
        message = MC6Pro_intuitive.IntuitiveMessage()
        self.assertEqual(message.from_base(base_message, self.catalog, None, self.midi_channels), "PC:channel1:0")
        result_message = self.mk_message("PC:channel1:0", 'channel1', 'PC', 0, None)
        result = {"PC:channel1:0": result_message}
        self.assertEqual(self.catalog.catalog, result)

        # Test adding a second message
        base_message = self.mk_base_method(1, 2, [0, 0])
        message = MC6Pro_intuitive.IntuitiveMessage()
        self.assertEqual(message.from_base(base_message, self.catalog, None, self.midi_channels), "CC:channel1:0:0")
        result_message = self.mk_message("CC:channel1:0:0", 'channel1', 'CC', 0, 0)
        result["CC:channel1:0:0"] = result_message
        self.assertEqual(self.catalog.catalog, result)

        # Test adding a third message
        base_message = self.mk_base_method(2, 2, [2, 3])
        message = MC6Pro_intuitive.IntuitiveMessage()
        self.assertEqual(message.from_base(base_message, self.catalog, None, self.midi_channels), "CC:channel2:2:3")
        result_message = self.mk_message("CC:channel2:2:3", 'channel2', 'CC', 2, 3)
        result["CC:channel2:2:3"] = result_message
        self.assertEqual(self.catalog.catalog, result)

        # Test found under same name, same value
        message = MC6Pro_intuitive.IntuitiveMessage()
        self.assertEqual(message.from_base(base_message, self.catalog, None, self.midi_channels), "CC:channel2:2:3")
        self.assertEqual(self.catalog.catalog, result)

        # Test found under same name, different value
        self.catalog.catalog["CC:channel2:2:3"] = self.catalog.catalog["CC:channel1:0:0"]
        message = MC6Pro_intuitive.IntuitiveMessage()
        with self.assertRaises(MC6Pro_intuitive.IntuitiveException) as context:
            message.from_base(base_message, self.catalog, None, self.midi_channels)
        self.assertEqual(context.exception.args[0], 'name_appears')

        # Test found under different name, same value
        base_message = self.mk_base_method(3, 2, [4, 5])
        result_message = self.mk_message("foo", 'channel3', 'CC', 4, 5)
        self.catalog.add(result_message)
        message = MC6Pro_intuitive.IntuitiveMessage()
        self.assertEqual(message.from_base(base_message, self.catalog, None, self.midi_channels), "foo")

    def test_different_midi_messages(self):
        # Test PC
        base_message = self.mk_base_method(1, 1, [3])
        message = MC6Pro_intuitive.IntuitiveMessage()
        self.assertEqual(message.from_base(base_message, self.catalog, None,  self.midi_channels), "PC:channel1:3")
        self.assertEqual(message.channel, 'channel1')
        self.assertEqual(message.number, 3)
        self.assertEqual(message.type, 'PC')

        # Test CC
        base_message = self.mk_base_method(2, 2, [4, 5])
        message = MC6Pro_intuitive.IntuitiveMessage()
        self.assertEqual(message.from_base(base_message, self.catalog, None, self.midi_channels), "CC:channel2:4:5")
        self.assertEqual(message.channel, 'channel2')
        self.assertEqual(message.number, 4)
        self.assertEqual(message.value, 5)
        self.assertEqual(message.type, 'CC')

        # Test Bank Jump
        base_message = self.mk_base_method(None, 13, [4, None, 14])
        message = MC6Pro_intuitive.IntuitiveMessage()
        banks = [None, None, None, None, 'Bank 5']
        self.assertEqual(message.from_base(base_message, self.catalog, banks, self.midi_channels), "Bank Jump:Bank 5:2")
        self.assertEqual(message.type, 'Bank Jump')
        self.assertEqual(message.bank, 'Bank 5')
        self.assertEqual(message.page, 2)

        # Test Toggle Page
        base_message = self.mk_base_method(None, 14, [6])
        message = MC6Pro_intuitive.IntuitiveMessage()
        self.assertEqual(message.from_base(base_message, self.catalog, None, self.midi_channels), "Page Jump:3")
        self.assertEqual(message.type, 'Page Jump')
        self.assertEqual(message.page, 3)

    # No tests written yet
    def test_intuitive_message(self):
        self.assertEqual(True, True)

    # No tests written yet
    def test_intuitive_preset(self):
        self.assertEqual(True, True)

    # No tests written yet
    def test_intuitive_bank(self):
        self.assertEqual(True, True)

    # No tests written yet
    def test_intuitive_midi_channel(self):
        self.assertEqual(True, True)

    def test_intuitive_roadmap_pages(self):
        self.assertEqual(1, MC6Pro_intuitive.MC6ProIntuitive.number_pages(1))
        self.assertEqual(1, MC6Pro_intuitive.MC6ProIntuitive.number_pages(2))
        self.assertEqual(1, MC6Pro_intuitive.MC6ProIntuitive.number_pages(3))
        self.assertEqual(1, MC6Pro_intuitive.MC6ProIntuitive.number_pages(4))
        self.assertEqual(1, MC6Pro_intuitive.MC6ProIntuitive.number_pages(5))
        self.assertEqual(1, MC6Pro_intuitive.MC6ProIntuitive.number_pages(6))
        self.assertEqual(2, MC6Pro_intuitive.MC6ProIntuitive.number_pages(7))
        self.assertEqual(2, MC6Pro_intuitive.MC6ProIntuitive.number_pages(8))
        self.assertEqual(2, MC6Pro_intuitive.MC6ProIntuitive.number_pages(9))
        self.assertEqual(2, MC6Pro_intuitive.MC6ProIntuitive.number_pages(10))
        self.assertEqual(3, MC6Pro_intuitive.MC6ProIntuitive.number_pages(11))
        self.assertEqual(3, MC6Pro_intuitive.MC6ProIntuitive.number_pages(12))
        self.assertEqual(3, MC6Pro_intuitive.MC6ProIntuitive.number_pages(13))
        self.assertEqual(3, MC6Pro_intuitive.MC6ProIntuitive.number_pages(14))
        self.assertEqual(4, MC6Pro_intuitive.MC6ProIntuitive.number_pages(15))
        self.assertEqual(4, MC6Pro_intuitive.MC6ProIntuitive.number_pages(16))

    def test_intuitive_roadmap_banks(self):
        self.assertEqual(1, MC6Pro_intuitive.MC6ProIntuitive.number_banks(1))
        self.assertEqual(1, MC6Pro_intuitive.MC6ProIntuitive.number_banks(2))
        self.assertEqual(1, MC6Pro_intuitive.MC6ProIntuitive.number_banks(3))
        self.assertEqual(1, MC6Pro_intuitive.MC6ProIntuitive.number_banks(4))
        self.assertEqual(2, MC6Pro_intuitive.MC6ProIntuitive.number_banks(5))
        self.assertEqual(2, MC6Pro_intuitive.MC6ProIntuitive.number_banks(6))
        self.assertEqual(2, MC6Pro_intuitive.MC6ProIntuitive.number_banks(7))
        self.assertEqual(2, MC6Pro_intuitive.MC6ProIntuitive.number_banks(8))
        self.assertEqual(3, MC6Pro_intuitive.MC6ProIntuitive.number_banks(9))


class IntuitiveToBaseTestCase(unittest.TestCase):
    # No tests written yet
    def test_intuitive_midi_message(self):
        self.assertEqual(True, True)

    # No tests written yet
    def test_intuitive_message(self):
        self.assertEqual(True, True)

    # No tests written yet
    def test_intuitive_preset(self):
        self.assertEqual(True, True)

    # No tests written yet
    def test_intuitive_bank(self):
        self.assertEqual(True, True)

    # No tests written yet
    def test_intuitive_midi_channel(self):
        self.assertEqual(True, True)

    # No tests written yet
    def test_intuitive(self):
        self.assertEqual(True, True)


class MC6ProIntuitiveTestCase(unittest.TestCase):

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

    def process_one_file(self, filename, extension):
        # Parse the base config file into a base model
        # Convert the base model into an intuitive model
        # Write the intuitive model to an intuitive config file
        # Load the intuitive config file to an intuitive model
        # Compare the reloaded intuitive model to the original
        # Convert the reloaded intuitive model to a base model
        # Compare the reloaded base model to the original base model
        # Save the base model into a base config file
        # Load the new base config file back into a base model
        # Compare against the original base model
        orig_base_config_filename = "Configs/" + filename + ".json"
        intuitive_config_filename = "tmp/" + filename + "_intuitive." + extension
        new_base_config_filename = "tmp/" + filename + ".json"
        base_grammar = jg.JsonGrammar(MC6Pro_grammar.mc6pro_schema)
        base_file = jg.JsonGrammarFile(filename=orig_base_config_filename)
        orig_base_model = base_grammar.parse(base_file.load())
        self.assertEqual(orig_base_model.modified, True)

        # Convert the config model into an intuitive model
        orig_int_model = MC6Pro_intuitive.MC6ProIntuitive()
        orig_int_model.from_base(orig_base_model)

        # Save the intuitive model to a file
        int_grammar = jg.JsonGrammar(MC6Pro_intuitive.mc6pro_intuitive_schema, True)
        int_file = jg.JsonGrammarFile(filename=intuitive_config_filename)
        int_file.save(int_grammar.gen(orig_int_model))

        # Load the intuitive string back to a model
        reloaded_int_grammar = jg.JsonGrammar(MC6Pro_intuitive.mc6pro_intuitive_schema, True)
        reloaded_int_file = jg.JsonGrammarFile(intuitive_config_filename)
        reloaded_int_model = reloaded_int_grammar.parse(reloaded_int_file.load())

        # Compare the reloaded model
        if reloaded_int_model is None:
            reloaded_int_model = MC6Pro_intuitive.MC6ProIntuitive()
        self.assertEqual(reloaded_int_model, orig_int_model)

        # Convert the reloaded int model to a config model
        reloaded_base_model = reloaded_int_model.to_base()

        # And compare it to the original config model
        self.assertEqual(reloaded_base_model, orig_base_model)

        # Save a new config file
        reloaded_base_file_grammar = jg.JsonGrammar(MC6Pro_grammar.mc6pro_schema)
        reloaded_base_file = jg.JsonGrammarFile(filename=new_base_config_filename)
        reloaded_base_file.save(reloaded_base_file_grammar.gen(reloaded_base_model))

        # Load the new config file
        rereloaded_base_grammar = jg.JsonGrammar(MC6Pro_grammar.mc6pro_schema)
        rereloaded_base_file = jg.JsonGrammarFile(filename=new_base_config_filename)
        rereloaded_base_model = rereloaded_base_grammar.parse(rereloaded_base_file.load())
        self.assertEqual(rereloaded_base_model, orig_base_model)

        # Make sure the raw json is the same
        # Get rid of fields that complicate things
        rereloaded_data = rereloaded_base_file.load()
        base_data = base_file.load()
        rereloaded_data['downloadDate'] = ''
        rereloaded_data['hash'] = 0
        base_data['downloadDate'] = ''
        base_data['hash'] = 0
        # the midi clock output ports only care about the 11 LSBs
        controller_settings = base_data['data']['controller_settings']['data']['controller_settings']
        base_midi_clock_output_ports = controller_settings['data']['midiClockOutputPorts']
        new2_base_midi_clock_output_ports = \
            rereloaded_data['data']['controller_settings']['data']['controller_settings']['data'][
                'midiClockOutputPorts']
        output_ports = base_midi_clock_output_ports & new2_base_midi_clock_output_ports & 2047
        self.assertEqual(output_ports, 2047)
        controller_settings['data']['midiClockOutputPorts'] = output_ports
        rereloaded_data['data']['controller_settings']['data']['controller_settings']['data'][
            'midiClockOutputPorts'] = \
            output_ports

        self.same_json(base_data, rereloaded_data, '',
                       ['bankMsgArray', 'sequencer_engines'])

    def test_configs(self):
        self.process_one_file("Empty", "yaml")
        self.process_one_file("Empty", "json")
        self.process_one_file("Features", "yaml")
        self.process_one_file("Features", "json")

    def test_demo(self):
        base_conf = jg.JsonGrammar(MC6Pro_grammar.mc6pro_schema)
        base_file = jg.JsonGrammarFile('tmp/Demo.json')
        intuitive_conf = jg.JsonGrammar(MC6Pro_intuitive.mc6pro_intuitive_schema, minimal=True)
        intuitive_file = jg.JsonGrammarFile('Configs/Demo.yaml')
        intuitive_model = intuitive_conf.parse(intuitive_file.load())
        base_model = intuitive_model.to_base()
        self.assertIsNotNone(base_model)
        base_file.save(base_conf.gen(base_model))


class MC6ProNavigatorTestCase(unittest.TestCase):
    navigator_banks = [
        ["Home",
         ["Bank 1", "Bank 2", "Bank 3", "Bank 4", "Bank 5", "Next",
          "Bank 6", "Bank 7", "Previous", "Bank 8", "Bank 9", "Next",
          "Bank 10", "Bank 11", "Previous", "Bank 12", "Bank 13", "Next",
          "Bank 14", "Bank 15", "Previous", "Bank 16", "Bank 17", "Next"]
         ],
        ["Home (2)",
         ["Bank 18", "Bank 19", "Previous", "Bank 20", "Bank 21", "Next",
          "Bank 22", "Bank 23", "Previous", "Bank 24", "Bank 25", "Next",
          "Bank 26", "Bank 27", "Previous", "Bank 28", "Bank 29", "Bank 30"
          ]
         ],
        ["Bank 1",
         ['', '', 'Home']
         ],
        ["Bank 2",
         ['Preset 1', '', 'Home']
         ],
        ["Bank 3",
         ['Preset 1', 'Preset 2', 'Home']
         ],
        ["Bank 4",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3']
         ],
        ["Bank 5",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4']
         ],
        ["Bank 6",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Preset 5']
         ],
        ["Bank 7",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous']
         ],
        ["Bank 8",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7']
         ],
        ["Bank 9",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8']
         ],
        ["Bank 10",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Preset 9']
         ],
        ["Bank 11",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous']
         ],
        ["Bank 12",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11']
         ],
        ["Bank 13",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12']
         ],
        ["Bank 14",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Preset 13']
         ],
        ["Bank 15",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous']
         ],
        ["Bank 16",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15']
         ],
        ["Bank 17",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15', 'Preset 16']
         ],
        ["Bank 18",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15', 'Preset 16', 'Preset 17']
         ],
        ["Bank 19",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15', 'Preset 16', 'Next']
         ],
        ["Bank 19 (2)",
         ['Preset 17', 'Preset 18', 'Previous']
         ],
        ["Bank 20",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15', 'Preset 16', 'Next']
         ],
        ["Bank 20 (2)",
         ['Preset 17', 'Preset 18', 'Previous', 'Preset 19']
         ],
        ["Bank 21",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15', 'Preset 16', 'Next']
         ],
        ["Bank 21 (2)",
         ['Preset 17', 'Preset 18', 'Previous', 'Preset 19', 'Preset 20']
         ],
        ["Bank 22",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15', 'Preset 16', 'Next']
         ],
        ["Bank 22 (2)",
         ['Preset 17', 'Preset 18', 'Previous', 'Preset 19', 'Preset 20', 'Preset 21']
         ],
        ["Bank 23",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15', 'Preset 16', 'Next']
         ],
        ["Bank 23 (2)",
         ['Preset 17', 'Preset 18', 'Previous', 'Preset 19', 'Preset 20', 'Next',
          'Preset 21', 'Preset 22', 'Previous']
         ],
        ["Bank 24",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15', 'Preset 16', 'Next']
         ],
        ["Bank 24 (2)",
         ['Preset 17', 'Preset 18', 'Previous', 'Preset 19', 'Preset 20', 'Next',
          'Preset 21', 'Preset 22', 'Previous', 'Preset 23']
         ],
        ["Bank 25",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15', 'Preset 16', 'Next']
         ],
        ["Bank 25 (2)",
         ['Preset 17', 'Preset 18', 'Previous', 'Preset 19', 'Preset 20', 'Next',
          'Preset 21', 'Preset 22', 'Previous', 'Preset 23', 'Preset 24']
         ],
        ["Bank 26",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15', 'Preset 16', 'Next']
         ],
        ["Bank 26 (2)",
         ['Preset 17', 'Preset 18', 'Previous', 'Preset 19', 'Preset 20', 'Next',
          'Preset 21', 'Preset 22', 'Previous', 'Preset 23', 'Preset 24', 'Preset 25']
         ],
        ["Bank 27",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15', 'Preset 16', 'Next']
         ],
        ["Bank 27 (2)",
         ['Preset 17', 'Preset 18', 'Previous', 'Preset 19', 'Preset 20', 'Next',
          'Preset 21', 'Preset 22', 'Previous', 'Preset 23', 'Preset 24', 'Next',
          'Preset 25', 'Preset 26', 'Previous']
         ],
        ["Bank 28",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15', 'Preset 16', 'Next']
         ],
        ["Bank 28 (2)",
         ['Preset 17', 'Preset 18', 'Previous', 'Preset 19', 'Preset 20', 'Next',
          'Preset 21', 'Preset 22', 'Previous', 'Preset 23', 'Preset 24', 'Next',
          'Preset 25', 'Preset 26', 'Previous', 'Preset 27']
         ],
        ["Bank 29",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15', 'Preset 16', 'Next']
         ],
        ["Bank 29 (2)",
         ['Preset 17', 'Preset 18', 'Previous', 'Preset 19', 'Preset 20', 'Next',
          'Preset 21', 'Preset 22', 'Previous', 'Preset 23', 'Preset 24', 'Next',
          'Preset 25', 'Preset 26', 'Previous', 'Preset 27', 'Preset 28']
         ],
        ["Bank 30",
         ['Preset 1', 'Preset 2', 'Home', 'Preset 3', 'Preset 4', 'Next',
          'Preset 5', 'Preset 6', 'Previous', 'Preset 7', 'Preset 8', 'Next',
          'Preset 9', 'Preset 10', 'Previous', 'Preset 11', 'Preset 12', 'Next',
          'Preset 13', 'Preset 14', 'Previous', 'Preset 15', 'Preset 16', 'Next']
         ],
        ["Bank 30 (2)",
         ['Preset 17', 'Preset 18', 'Previous', 'Preset 19', 'Preset 20', 'Next',
          'Preset 21', 'Preset 22', 'Previous', 'Preset 23', 'Preset 24', 'Next',
          'Preset 25', 'Preset 26', 'Previous', 'Preset 27', 'Preset 28', 'Preset 29']
         ]
    ]

    def test_navigator(self):
        intuitive_conf = jg.JsonGrammar(MC6Pro_intuitive.mc6pro_intuitive_schema, minimal=True)
        intuitive_file = jg.JsonGrammarFile(filename='Configs/NavigatorTest.json')
        intuitive_model = intuitive_conf.parse(intuitive_file.load())
        base_model = intuitive_model.to_base()
        self.assertIsNotNone(base_model)
        for pos, bank in enumerate(base_model.banks):
            if pos < len(self.navigator_banks):
                self.assertEqual(bank.name, self.navigator_banks[pos][0])
                for pos2, preset in enumerate(bank.presets):
                    if pos2 < len(self.navigator_banks[pos][1]):
                        self.assertEqual(preset.short_name, self.navigator_banks[pos][1][pos2])
                    else:
                        if preset is not None:
                            x = 1
                        self.assertIsNone(preset)
            else:
                self.assertIsNone(bank)


class MC6ProColorsInheritanceTestCase(unittest.TestCase):
    def check_bank(self, bank, foreground_color, background_color):
        if foreground_color is None:
            self.assertIsNone(bank.text_color)
        else:
            self.assertEqual(bank.text_color, MC6Pro_intuitive.preset_colors.index(foreground_color))
        if background_color is None:
            self.assertIsNone(bank.background_color)
        else:
            self.assertEqual(bank.background_color, MC6Pro_intuitive.preset_colors.index(background_color))

    def check_preset(self, preset, preset_color, preset_toggle_color, preset_background_color,
                     preset_toggle_background_color):
        if preset_color is None:
            self.assertIsNone(preset.name_color)
        else:
            self.assertEqual(preset.name_color, MC6Pro_intuitive.preset_colors.index(preset_color))
        if preset_toggle_color is None:
            self.assertIsNone(preset.name_toggle_color)
        else:
            self.assertEqual(preset.name_toggle_color, MC6Pro_intuitive.preset_colors.index(preset_toggle_color))
        if preset_background_color is None:
            self.assertIsNone(preset.background_color)
        else:
            self.assertEqual(preset.background_color, MC6Pro_intuitive.preset_colors.index(preset_background_color))
        if preset_toggle_background_color is None:
            self.assertIsNone(preset.background_toggle_color)
        else:
            self.assertEqual(preset.background_toggle_color,
                             MC6Pro_intuitive.preset_colors.index(preset_toggle_background_color))

    def test_inheritance1(self):
        # Navigator schema:
        #   Bank: steelblue/lightsteelblue
        #   Preset: tan/cornsilk
        #   Preset Toggle: brown/maroon
        # Default schema:
        #   Bank: orange/red
        #   Preset: skyblue/olivedrab
        #   Preset Toggle: deeppink/mediumslateblue
        # Bank 2 schema:
        #   Bank: blueviolet/thistle
        #   Preset: darkseagreen/olive
        #   Preset Toggle: forestgreen/indigo
        # Preset 2 schema:
        #   Preset: khaki/lightyellow
        #   Preset Toggle: darkkhaki/lightsalmon
        intuitive_conf = jg.JsonGrammar(MC6Pro_intuitive.mc6pro_intuitive_schema, minimal=True)
        intuitive_file = jg.JsonGrammarFile(filename='Configs/ColorsTest1.yaml')
        intuitive_model = intuitive_conf.parse(intuitive_file.load())
        base_model = intuitive_model.to_base()
        navigator_bank = base_model.banks[0]
        self.check_bank(navigator_bank, "steelblue", "lightsteelblue")
        self.check_preset(navigator_bank.presets[0], "tan", "brown",
                          "cornsilk", "maroon")
        self.check_preset(navigator_bank.presets[1], "tan", "brown",
                          "cornsilk", "maroon")
        bank_one = base_model.banks[1]
        self.check_bank(bank_one, "orange", "red")
        self.check_preset(bank_one.presets[0], "skyblue", "deeppink",
                          "olivedrab", "mediumslateblue")
        self.check_preset(bank_one.presets[1], "khaki", "darkkhaki",
                          "lightyellow", "lightsalmon")
        self.check_preset(bank_one.presets[2], "tan", "brown",
                          "cornsilk", "maroon")
        bank_two = base_model.banks[2]
        self.check_bank(bank_two, "blueviolet", "thistle")
        self.check_preset(bank_two.presets[0], "darkseagreen", "forestgreen",
                          "olive", "indigo")
        self.check_preset(bank_two.presets[1], "khaki", "darkkhaki",
                          "lightyellow", "lightsalmon")
        self.check_preset(bank_two.presets[2], "tan", "brown",
                          "cornsilk", "maroon")

    def test_inheritance2(self):
        # Navigator schema:
        #   Bank: steelblue/lightsteelblue
        #   Preset: tan/cornsilk
        #   Preset Toggle: brown/maroon
        # Default schema:
        #   Bank: None/None
        #   Preset: None/None
        #   Preset Toggle: None/NOne
        # Bank 2 schema:
        #   Bank: blueviolet/thistle
        #   Preset: darkseagreen/olive
        #   Preset Toggle: forestgreen/indigo
        # Preset 2 schema:
        #   Preset: khaki/lightyellow
        #   Preset Toggle: darkkhaki/lightsalmon
        intuitive_conf = jg.JsonGrammar(MC6Pro_intuitive.mc6pro_intuitive_schema, minimal=True)
        intuitive_file = jg.JsonGrammarFile(filename='Configs/ColorsTest2.yaml')
        intuitive_model = intuitive_conf.parse(intuitive_file.load())
        base_model = intuitive_model.to_base()
        navigator_bank = base_model.banks[0]
        self.check_bank(navigator_bank, "steelblue", "lightsteelblue")
        self.check_preset(navigator_bank.presets[0], "tan", "brown",
                          "cornsilk", "maroon")
        self.check_preset(navigator_bank.presets[1], "tan", "brown",
                          "cornsilk", "maroon")
        bank_one = base_model.banks[1]
        self.check_bank(bank_one, None, None)
        self.check_preset(bank_one.presets[0], None, None,
                          None, None)
        self.check_preset(bank_one.presets[1], "khaki", "darkkhaki",
                          "lightyellow", "lightsalmon")
        self.check_preset(bank_one.presets[2], "tan", "brown",
                          "cornsilk", "maroon")
        bank_two = base_model.banks[2]
        self.check_bank(bank_two, "blueviolet", "thistle")
        self.check_preset(bank_two.presets[0], "darkseagreen", "forestgreen",
                          "olive", "indigo")
        self.check_preset(bank_two.presets[1], "khaki", "darkkhaki",
                          "lightyellow", "lightsalmon")
        self.check_preset(bank_two.presets[2], "tan", "brown",
                          "cornsilk", "maroon")

    def test_inheritance3(self):
        # Navigator schema: same as default
        # Default schema:
        #   Bank: orange/red
        #   Preset: skyblue/olivedrab
        #   Preset Toggle: deeppink/mediumslateblue
        # Bank 2 schema:
        #   Bank: blueviolet/thistle
        #   Preset: darkseagreen/olive
        #   Preset Toggle: forestgreen/indigo
        # Preset 2 schema:
        #   Preset: khaki/lightyellow
        #   Preset Toggle: darkkhaki/lightsalmon
        intuitive_conf = jg.JsonGrammar(MC6Pro_intuitive.mc6pro_intuitive_schema, minimal=True)
        intuitive_file = jg.JsonGrammarFile(filename='Configs/ColorsTest3.yaml')
        intuitive_model = intuitive_conf.parse(intuitive_file.load())
        base_model = intuitive_model.to_base()
        navigator_bank = base_model.banks[0]
        self.check_bank(navigator_bank, "orange", "red")
        self.check_preset(navigator_bank.presets[0], "skyblue", "deeppink",
                          "olivedrab", "mediumslateblue")
        self.check_preset(navigator_bank.presets[1], "skyblue", "deeppink",
                          "olivedrab", "mediumslateblue")
        bank_one = base_model.banks[1]
        self.check_bank(bank_one, "orange", "red")
        self.check_preset(bank_one.presets[0], "skyblue", "deeppink",
                          "olivedrab", "mediumslateblue")
        self.check_preset(bank_one.presets[1], "khaki", "darkkhaki",
                          "lightyellow", "lightsalmon")
        self.check_preset(bank_one.presets[2], "skyblue", "deeppink",
                          "olivedrab", "mediumslateblue")
        bank_two = base_model.banks[2]
        self.check_bank(bank_two, "blueviolet", "thistle")
        self.check_preset(bank_two.presets[0], "darkseagreen", "forestgreen",
                          "olive", "indigo")
        self.check_preset(bank_two.presets[1], "khaki", "darkkhaki",
                          "lightyellow", "lightsalmon")
        self.check_preset(bank_two.presets[2], "skyblue", "deeppink",
                          "olivedrab", "mediumslateblue")

    def test_inheritance4(self):
        # Navigator schema: None
        # Default schema: None
        # Bank 2 schema:
        #   Bank: blueviolet/thistle
        #   Preset: darkseagreen/olive
        #   Preset Toggle: forestgreen/indigo
        # Preset 2 schema:
        #   Preset: khaki/lightyellow
        #   Preset Toggle: darkkhaki/lightsalmon
        intuitive_conf = jg.JsonGrammar(MC6Pro_intuitive.mc6pro_intuitive_schema, minimal=True)
        intuitive_file = jg.JsonGrammarFile(filename='Configs/ColorsTest4.yaml')
        intuitive_model = intuitive_conf.parse(intuitive_file.load())
        base_model = intuitive_model.to_base()
        navigator_bank = base_model.banks[0]
        self.check_bank(navigator_bank, None, None)
        self.check_preset(navigator_bank.presets[0], None, None,
                          None, None)
        self.check_preset(navigator_bank.presets[1], None, None,
                          None, None)
        bank_one = base_model.banks[1]
        self.check_bank(bank_one, None, None)
        self.check_preset(bank_one.presets[0], None, None,
                          None, None)
        self.check_preset(bank_one.presets[1], "khaki", "darkkhaki",
                          "lightyellow", "lightsalmon")
        self.check_preset(bank_one.presets[2], None, None,
                          None, None)
        bank_two = base_model.banks[2]
        self.check_bank(bank_two, "blueviolet", "thistle")
        self.check_preset(bank_two.presets[0], "darkseagreen", "forestgreen",
                          "olive", "indigo")
        self.check_preset(bank_two.presets[1], "khaki", "darkkhaki",
                          "lightyellow", "lightsalmon")
        self.check_preset(bank_two.presets[2], "darkseagreen", "forestgreen",
                          "olive", "indigo")


if __name__ == '__main__':
    unittest.main()

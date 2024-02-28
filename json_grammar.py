import copy
import json


# Parsing a JSON Grammar
#
# There are two kinds of JSON grammars: complete and minimal.
# A complete grammar expects all elements to be present.
# A minimal grammar excludes elements that default, and shortens lists as needed
#
# For the MC6Pro, the config/backup file is a complete grammar. Requiring all elements ensures that as things change
# we will not miss an item
#
# For the MC6Pro intuitive file, it is a minimal grammar. Only elements needed are specified. This is much more
# human readable.
#
# The grammar provides two operations: parse and gen.
# Parsing creates a "model" in the theoretical computer science sense - it is a model of what is intended by the JSON
# Generating takes a model and creates the JSON string equivalent.
#
# Grammar elements are Dictionaries, Switch Dictionaries, Lists, Enums and Atoms
# Dictionaries and switch dictionaries have keys that map to elements
# For complete grammars, all keys must be present
# For minimal grammars, only non-default keys must be present
# Switch dictionaries have an switch key which must be an enum, and a set of keys for each enum value.
# This allows a choice mechanism
# Lists are fixed length lists, in the minimal grammars, they can be truncated.
# Lists can also be unlimited (length == 0), only for minimal grammars
# Enums are lists of constants, used for color names (for example) or for switch keys in dictionaries
# Atoms are ints, strings, or booleans
#
# All grammar elements have var and model bindings (optional)
# A var binding means that when that element is encountered while parsing, it is bound to that variable in the current
# model.
# A model binding means that model (python class) is used for parsing that element and all subelements
#
# Atoms also have optional default and value attributes. The default value is what is normally expected, and is left
# out when creating a model (only significant information is in the model, even for complete grammars).
# The value attribute requires a specific value for the atom. This is used for elements not yet covered, so that if
# a configuration file has them, an error is flagged rather than ignoring them.
# defaults and values can also be functions. These functions take 3 arguments: the value being examined, the "context",
# and the list position:
#  The value being examined is the element being parsed, if parsing, and may be a value pulled from a model if genning
# The "context" is the immediately enclosing dictionary or list element
# The list position is a list of integers, represeting which position in the list this element occurred in, with the
# innermost being the last in the list
#
# Models are python classes, with variables mapping to values.
# All models must inherit from JsonGrammarModel

class JsonGrammarException(Exception):
    """used for exceptions raised during parsing"""
    pass


class JsonGrammarModel:
    """Base class for models, includes the modified boolean"""
    def __init__(self):
        self.modified = False


# Grammar creation helpers
def make_dict(dict_name, keys, var=None, model=None):
    result = {'type': 'dictionary', 'name': dict_name, 'keys': keys}
    if var is not None:
        result = add_variable(result, var)
    if model is not None:
        result = add_model(result, model)
    return result


def make_switch_dict(dict_name, switch_key, case_keys, common_keys=None, var=None, model=None):
    if common_keys is None:
        common_keys = []
    result = {'type': 'switch_dictionary', 'name': dict_name, 'switch_key': switch_key, 'case_keys': case_keys,
              'common_keys': common_keys}
    if var is not None:
        result = add_variable(result, var)
    if model is not None:
        result = add_model(result, model)
    return result


def make_key(key_name, key_schema, var=None, model=None):
    result = {'name': key_name, 'schema': key_schema}
    if var is not None:
        result = add_variable(result, var)
    if model is not None:
        result = add_model(result, model)
    return result


def make_list(length, schema, var=None, model=None):
    if 'type' not in schema:
        raise JsonGrammarException('probable_key', "got non schema")
    result = {'type': 'list', 'length': length, 'schema': schema}
    if var is not None:
        result = add_variable(result, var)
    if model is not None:
        result = add_model(result, model)
    return result


def make_enum(enum_base, default=None, var=None, model=None):
    result = {'type': 'enum', 'base': enum_base}
    if default is not None:
        try:
            enum_base.index(default)
        except ValueError:
            raise JsonGrammarException('bad_enum_value', "bad enum value")
        result['default'] = default
    if var is not None:
        result['variable'] = var
    if model is not None:
        result = add_model(result, model)
    return result


def make_atom(atom_type, default=None, value=None, var=None, model=None):
    number_set = 0
    if default is not None:
        number_set += 1
    if value is not None:
        number_set += 1
    if number_set > 1:
        raise JsonGrammarException('both_value_default', 'Schema atom has more than 1 value, default set')
    result = {'type': 'atom', 'obj_type': atom_type}
    if default is not None:
        result['default'] = default
    if value is not None:
        result['value'] = value
    if var is not None:
        result = add_variable(result, var)
    if model is not None:
        result = add_model(result, model)
    return result


false_atom = make_atom(bool, value=False)
zero_atom = make_atom(int, value=0)


def add_variable(schema, variable):
    if 'type' not in schema:
        raise JsonGrammarException('probable_key', "got non schema")
    schema['variable'] = variable
    return schema


def add_model(schema, model):
    if 'type' not in schema:
        raise JsonGrammarException('probable_key', "got non schema")
    schema['model'] = model
    return schema


def make_unimplemented():
    return {'type': 'unimplemented'}


# Value/Default atom functions, commonly used
# identity just returns the position in the list, zero based
def identity(_elem, _ctxt, lp):
    return lp[-1]


# returns the 1 based position in the list
def identity_plus_1(_elem, _ctxt, lp):
    return lp[-1] + 1


# returns the position in the enclosing list
def identity2(_elem, _ctxt, lp):
    return lp[-2]


# Helper function to remove all None elements from the end of a list
def prune_list(list_to_prune):
    while len(list_to_prune) > 0 and list_to_prune[len(list_to_prune) - 1] is None:
        list_to_prune.pop(len(list_to_prune) - 1)


def compact_list(list_to_compact):
    i = 0
    while i < len(list_to_compact):
        if list_to_compact[i] is None:
            del list_to_compact[i]
        else:
            i += 1


class JsonGrammar:

    def __init__(self, schema, minimal=False):
        self.schema = schema
        self.minimal = minimal
        self.loaded = False
        self.file_name = None
        self.source_string = None
        self.raw = None

    # Parsing
    # Parsing takes a JSON string and returns a model.
    # The model is usually associated at the top level via model tag in the root grammar element
    # Parson a JSON subexpression can store the result in 3 ways
    # If a model is specified, all sub-subexpressions are parsed with this model
    # If a variable is specified, the result of the parse is stored in that variable in the current model
    # If neither is speficied, the result is returned as the result of the parse
    # Note that if both a model and variable are specified for the same element,
    # the element is parsed with sub-elements using the specified model, and the result is stored in the variable
    # in the passed-in model.
    # At the moment, there is no way to refer to the outer model when parsing the inner model
    #
    # If a node parses to a non-default value AND there is no model/variable associated with it, the parse function
    # returns the non-default value.
    #
    # Only significant values are stored in the model. Lack of a value means it is the default etc.

    # Parsing an element
    # elem is the JSON element to be parsed
    # schema is the schema/grammar for the element
    # name is a debugging name indicating where in the grammar we are
    # context is the immediately enclosing dictionary or list object
    # list_pos is the list_pos documented above
    # model is the current model to be used for storing significant changes
    #
    # If a model is specified in the schema, it is used in the subparsing
    # Also, if there is a result that wasn't stored in the model, an error is raised (losing significant info)
    # Finally, the result is the new model object
    #
    # If a variable is specified in the schema for this element, the result is bound in the model (old model)
    def parse_elem(self, elem: object, schema: object, name: object, context: object, list_pos: object,
                   model: object) -> object:
        if schema is None:
            raise JsonGrammarException('no_schema', "Schema is None")

        new_model = False
        # This really belongs inside the 'if' where we create a new model
        # But PyCharm complains then that old_model might be reffed before assignment below
        old_model = model
        if 'model' in schema:
            model = schema['model']()
            new_model = True

        if schema['type'] == 'dictionary':
            result = self.parse_dict(elem, schema, name, list_pos, model)
        elif schema['type'] == 'switch_dictionary':
            result = self.parse_switch_dict(elem, schema, name, list_pos, model)
        elif schema['type'] == 'list':
            result = self.parse_list(elem, schema, name, list_pos, model)
        elif schema['type'] == 'enum':
            result = self.parse_enum(elem, schema, name)
        elif schema['type'] == 'atom':
            result = self.parse_atom(elem, schema, name, context, list_pos, model)
        elif schema['type'] == 'unimplemented':
            raise JsonGrammarException('not_implemented', "Not implemented: specifically requested")
        else:
            raise JsonGrammarException('not_implemented', "Not implemented: parse_elem schema type")

        if new_model and model.modified:
            if result is not None:
                raise JsonGrammarException('unconsumed', "Model was used, but some result not added")
            result = model
            model = old_model

        if 'variable' in schema and result is not None:
            model.modified = True
            model_vars = vars(model)
            if model_vars[schema['variable']] is not None:
                raise JsonGrammarException('multiply_assigned_var', 'Variable is assigned multipe times')
            model_vars[schema['variable']] = result
            result = None
        return result

    def parse_dict_keys(self, elem, name, list_pos, model, keys, result, seen_keys):
        # The list of keys seen ensures we don't allow keys to appear twice
        # Found keys is the number of keys found in the elem while processing the schema
        # If this is not the total number of keys in the elem, some keys didn't match
        found_keys = len(seen_keys)

        # process each schema key
        for key in keys:
            if key['name'] not in elem:
                if self.minimal:
                    key_result = None
                else:
                    raise JsonGrammarException('dict_bad_keys',
                                               "parse_dict called with elem key mismatch: " + key['name'] + " not in " +
                                               str(elem.keys()))
            else:
                found_keys += 1
                # Note we update the context with the elem for sub-parsing
                key_result = self.parse_elem(elem[key['name']], key['schema'], name + ':' + key['name'], elem,
                                             list_pos, model)
            if key['name'] in seen_keys:
                raise JsonGrammarException('dict_duplicate_keys', 'grammar has duplicate keys')
            seen_keys[key['name']] = True
            # Only store if significant
            if key_result is not None:
                result[key['name']] = key_result

        # Make sure all keys in the elem were processed
        if found_keys != len(elem):
            raise JsonGrammarException('dict_bad_keys', 'some keys were not found')
        if result == {}:
            return None
        return result

    # parse_dict
    # elem is the dictionary element to be parsed
    # schema is the dictionary schema/grammar
    # name is the debugging trail
    # list_pos and model as documented above
    #
    # The schema name is added to the debugging trail
    #
    # There are two modes, complete or minimal
    # In complete, all keys must appear to be sub-parsed
    # In minimal, keys need not appear, but we must still make sure that all appearing keys are in the grammar
    def parse_dict(self, elem, schema, name, list_pos, model):
        name = name + ":" + schema['name']
        if not isinstance(elem, dict):
            raise JsonGrammarException('type_not_dict', "parse_dict called on non_dict")

        return self.parse_dict_keys(elem, name, list_pos, model, schema['keys'], {}, {})

    # same as parse_dict except
    # we must parse the switch key into a value, even if it is the default
    def parse_switch_dict(self, elem, schema, name, list_pos, model):
        name = name + ":" + schema['name']
        if not isinstance(elem, dict):
            raise JsonGrammarException('type_not_switch_dict', "parse_switch_dict called on non switch_dict")

        switch_key = schema['switch_key']
        if switch_key['name'] not in elem:
            raise JsonGrammarException('missing_switch', 'missing switch element')
        switch_value = self.parse_enum(elem[switch_key['name']], switch_key['schema'], name)
        # The following line is executed solely for the effect on the model
        parse_value = self.parse_elem(elem[switch_key['name']], switch_key['schema'], name, None, list_pos, model)
        absolute_switch_value = switch_value
        if switch_value is None:
            absolute_switch_value = switch_key['schema']['default']
        if absolute_switch_value not in schema['case_keys']:
            raise JsonGrammarException('bad_switch', 'switch element not in case keys')
        case_keys = schema['case_keys'][absolute_switch_value]
        all_keys = schema['common_keys'] + case_keys

        # need to add switch to result if not default
        result = {}
        if parse_value is not None:
            result[switch_key['name']] = parse_value
        seen_keys = {switch_key['name']: True}

        return self.parse_dict_keys(elem, name, list_pos, model, all_keys, result, seen_keys)

    # parse_list
    # for complete grammars, the list must be the exact length of the schema
    # for minimal grammars, the list can be shorter
    # If the schema list length is 0, there is no maximum length (only used with minimal grammars)
    # The significant result is a list with all significant values filled in.
    # Note that the list is not compacted, embedded insignificant values are kept with None
    # If the entire list is empty, None is returned
    def parse_list(self, elem, schema, name, list_pos, model):
        no_max = schema['length'] == 0
        if not isinstance(elem, list):
            raise JsonGrammarException('type_not_list', "parse_list called on non list")
        if not self.minimal and no_max:
            raise JsonGrammarException('unlimited_list_complete_grammar', 'length 0 with complete grammar')

        list_length = schema['length']
        if list_length == 0:
            list_length = len(elem)

        if len(elem) != list_length:
            if not (self.minimal and len(elem) < list_length):
                raise JsonGrammarException('list_bad_length', "parse_list called with wrong length list")

        result = [None] * list_length
        modified = False
        for new_list_pos, list_elem in enumerate(elem):
            if list_elem is not None:
                entry_result = self.parse_elem(list_elem, schema['schema'], name, elem, list_pos + [new_list_pos],
                                               model)
                if entry_result is not None:
                    modified = True
                    result[new_list_pos] = entry_result
        if modified:
            if self.minimal:
                prune_list(result)
                if len(result) == 0:
                    result = None
            return result
        else:
            return None

    # parse_enum parses an enum element
    # This could be static, but I choose not to for consistency with the other defs
    # There is no difference between complete and minimal grammars
    # The result is significant if it is not default
    @staticmethod
    def parse_enum(elem: object, schema: object, _name: object) -> object:
        if not isinstance(elem, str):
            raise JsonGrammarException('enum_wrong_type', "parse_enum called with element not a str")
        # Make sure the elem is valid
        try:
            schema['base'].index(elem)
        except ValueError:
            raise JsonGrammarException('bad_enum_value', "bad enum value")
        if 'default' in schema and elem == schema['default']:
            return None
        return elem

    # parse_atom parses a number, string, or boolean
    # It is the same for complete and minimal grammars
    # Significant values differ from the default
    # If the schema is 'value', then the value is required. This is used for portions of the MC6Pro file that are
    # not yet handled - we will throw an error when getting a config where features are used
    @staticmethod
    def parse_atom(elem, schema, name, context, list_pos, _model):
        if not isinstance(elem, schema['obj_type']):
            raise JsonGrammarException('atom_wrong_type', "parse_atom called with element having wrong type")
        num_found = 0
        target = None
        value = False
        if 'default' in schema:
            num_found += 1
            target = schema['default']
        if 'value' in schema:
            num_found += 1
            target = schema['value']
            value = True
        if num_found > 1:
            raise JsonGrammarException('both_value_default', 'Schema atom has more than 1 value, skip and default')
        if callable(target):
            target_elem = target(elem, context, list_pos)
        else:
            target_elem = target
        if elem != target_elem:
            if value:
                msg = "parse_atom called with " + str(elem) + " not matching schema " + str(schema['value'])
                msg += "in " + name
                raise JsonGrammarException('atom_wrong_value', msg)
            result = elem
        else:
            result = None
        return result

    # Generate a config JSON string from a model
    # There are two modes: complete and minimal

    # generate the JSON for one element
    # The model can be a value, a schema, or a model object
    # The context is the enclosing dictionary
    # The list_pos is the same as parse
    # If there is a variable, look up the value associated with that variable in the current model and use that for
    # the sub model.
    # Otherwise, if there is a model in the schema, and the passed in model isn't the right type, the sub model is None
    # This happens when a model is defaulted/None
    # Finally if neither of the above two cases are true, the sub model is the model
    def gen_elem(self, model, schema, context, list_pos):
        if schema is None:
            raise JsonGrammarException('no_schema', "Schema is None")
        if 'model' in schema and not isinstance(model, schema['model']):
            sub_model = None
        else:
            sub_model = model
        if 'variable' in schema:
            # If model is None, that means the model was not populated, everything is default
            if model is not None:
                if not isinstance(model, JsonGrammarModel):
                    raise JsonGrammarException('variable_without_model',
                                               "In gen_elem, have a variable that isn't a model")
                model_vars = vars(model)
                if schema['variable'] not in model_vars.keys():
                    raise JsonGrammarException('variable_not_in_model',
                                               'In gen_elem, there is a variable that is not in the model')
                sub_model = model_vars[schema['variable']]
        if schema['type'] == 'dictionary':
            result = self.gen_dict(sub_model, schema, list_pos)
        elif schema['type'] == 'switch_dictionary':
            result = self.gen_switch_dict(sub_model, schema, list_pos)
        elif schema['type'] == 'list':
            result = self.gen_list(sub_model, schema, list_pos)
        elif schema['type'] == 'enum':
            result = self.gen_enum(sub_model, schema, context, list_pos)
        elif schema['type'] == 'atom':
            result = self.gen_atom(sub_model, schema, context, list_pos)
        elif schema['type'] == 'unimplemented':
            raise JsonGrammarException('not_implemented', "Not implemented: specificly requested")
        else:
            raise JsonGrammarException('not_implemented', "Not implemented: parse_elem schema type")
        return result

    # gen the keys of a dict or a switch dict
    # the result is empty for a dict
    # the variable_result is empty for a dict
    # the result is the switch key and value for a switch dict
    # the variable_result is empty for a switch dict if in minimal mode AND the switch value is None, otherwise
    # it is the switch key and value
    # found keys is the number of keys found (0 for dicts, 1 for switch dicts, since we found the switch key)
    # the model is either None, a model object, or a dictionary
    # If none or a object, we pass directly to the sub-gen
    # If a dictionary we get the key out of the model and use that
    # If an atom uses the context function, keys are added to the context in the order they appear in the schema
    def gen_dict_keys(self, is_dict, model, keys, list_pos, result, variable_result, found_keys):
        sub_model = model
        for key in keys:
            if is_dict:
                sub_model = None
                if key['name'] in model:
                    sub_model = model[key['name']]
                    found_keys += 1
            result[key['name']] = self.gen_elem(sub_model, key['schema'], result, list_pos)
            if result[key['name']] is not None:
                variable_result[key['name']] = result[key['name']]

        if is_dict and found_keys != len(model.keys()):
            raise JsonGrammarException('dict_bad_keys', "gen_dict has unknown key in model")
        if self.minimal:
            if variable_result == {}:
                return None
            else:
                return variable_result
        else:
            return result

    # generate a dictionary element
    # returns significant keys when minimal, or the entire dict when complete
    def gen_dict(self, model, schema, list_pos):
        result = {}
        variable_result = {}
        found_keys = 0
        is_dict = isinstance(model, dict)
        if model is not None and not isinstance(model, JsonGrammarModel) and not is_dict:
            raise JsonGrammarException('type_not_dict', "gen_dict called on non_dict")

        return self.gen_dict_keys(is_dict, model, schema['keys'], list_pos, result, variable_result, found_keys)

    # generate a switch key element
    # returns significant keys when minimal, or the entire dict when complete
    # Get the switch key value.
    #   It may be None, in which case get the default
    # Build the result
    # Note that the result is used as the context too, and this is not thoroughly understood
    # This affects value and default functions which try to access the switch key
    # I don't have any use cases yet
    def gen_switch_dict(self, model, schema, list_pos):
        is_dict = isinstance(model, dict)
        if model is not None and not isinstance(model, JsonGrammarModel) and not is_dict:
            raise JsonGrammarException('type_not_dict', "gen_dict called on non_dict")

        # Determine what the switch is
        switch_key = schema['switch_key']
        switch_model = model
        if is_dict:
            if switch_key['name'] in model:
                switch_model = model[switch_key['name']]
            else:
                switch_model = None
        switch_value = self.gen_elem(switch_model, switch_key['schema'], {}, list_pos)
        defaulted_switch_value = switch_value
        if defaulted_switch_value is None:
            defaulted_switch_value = switch_key['schema']['default']
        if defaulted_switch_value not in schema['case_keys']:
            raise JsonGrammarException('switch_dict_bad_switch', 'invalid switch in model')
        keys = schema['case_keys'][defaulted_switch_value] + schema['common_keys']
        result = {}
        variable_result = {}
        if switch_value is not None:
            result = {switch_key['name']: switch_value}
            variable_result = {switch_key['name']: switch_value}
        found_keys = 1

        return self.gen_dict_keys(is_dict, model, keys, list_pos, result, variable_result, found_keys)

    # generate a list from a model
    # For a complete grammar, this is a full length list
    # For a minimal grammar, it is only up to the last non-None element
    # For zero length lists, this is only minimal grammar, and only for list models
    # For zero length lists, and non list models, the current behavior is an empty list. I don't have a use case,
    # so I am not sure this is correct
    # The model can be None, using only defaults
    # The model can be a model, pass through to sub elements
    # The model can be a list, the list elements are used in sub-parsing
    def gen_list(self, model, schema, list_pos):
        is_list = isinstance(model, list)
        unlimited = schema['length'] == 0
        if model is not None and not isinstance(model, JsonGrammarModel):
            if not is_list:
                raise JsonGrammarException('model_schema_mismatch', "gen_list got non list")
            if not self.minimal and not unlimited and len(model) != schema['length']:
                raise JsonGrammarException('list_bad_length', "gen_list called with wrong length list")
            if self.minimal and not unlimited and len(model) > schema['length']:
                raise JsonGrammarException('list_bad_length', "gen_list called with wrong length list")

        list_length = schema['length']
        if list_length == 0 and is_list:
            list_length = len(model)

        result = [None] * list_length
        for new_list_pos in range(0, list_length):
            sub_model = model
            if is_list:
                if new_list_pos >= len(model):
                    sub_model = None
                else:
                    sub_model = model[new_list_pos]
            result[new_list_pos] = self.gen_elem(sub_model, schema['schema'], result, list_pos + [new_list_pos])
        if self.minimal:
            prune_list(result)
            if len(result) == 0:
                result = None
        return result

    # generate an enum
    # This doesn't handle default/value functions
    # I don't have a use case
    def gen_enum(self, model, schema, _context, _list_pos):
        enum_value = None
        if 'default' in schema:
            enum_value = schema['default']

        result = None
        variable_result = result
        if model is None or isinstance(model, JsonGrammarModel):
            result = enum_value
        else:
            if model == enum_value:
                result = enum_value
            else:
                variable_result = model
                result = model

        if result is None:
            raise JsonGrammarException('enum_no_default', 'gen_enum resulted in None')

        if self.minimal:
            return variable_result
        else:
            return result

    # Generate an atom
    # model is an atom, None, or model object
    # None or model object is ignored, result is the default or value
    # if atom, that is the result
    # for minimal grammars, we need to check if the atom value is default (but not value)
    def gen_atom(self, model, schema, context, list_pos):
        is_atom = not (model is None or isinstance(model, JsonGrammarModel))
        if isinstance(model, JsonGrammarModel):
            model = None

        atom_value = None
        if 'value' in schema:
            atom_value = schema['value']
        elif 'default' in schema:
            atom_value = schema['default']
        elif not self.minimal:
            raise JsonGrammarException('no_value_default', "Missing both value and default in atom")
        if callable(atom_value):
            atom_value = atom_value(model, context, list_pos)

        variable_result = None
        if not is_atom:
            result = atom_value
            # Weird case, but if model is None we want to set the value
            if 'value' in schema:
                variable_result = atom_value
        else:
            if model == atom_value:
                result = atom_value
            elif 'value' not in schema:
                variable_result = model
                result = model
            else:
                raise JsonGrammarException('model_schema_mismatch', "atom has wrong value in model and schema")

        if not self.minimal and result is None:
            raise JsonGrammarException('programmer_error', 'gen_atom resulted in None')

        if self.minimal:
            return variable_result
        else:
            return result

    def parse_data(self):
        elem = self.raw
        if self.raw is None and self.minimal:
            elem = {}
        return self.parse_elem(elem, self.schema, "", None, [], None)

    def load_file(self, file_name):
        self.file_name = file_name
        with open(self.file_name, "r") as read_file:
            self.raw = json.load(read_file)
        self.loaded = True
        return self.parse_data()

    def save_file(self, file_name, model):
        temp_json = self.gen_elem(model, self.schema, None, [])
        self.file_name = file_name
        with open(self.file_name, "w") as write_file:
            json.dump(temp_json, write_file, indent=4)

    def load_string(self, source_string):
        self.source_string = source_string
        self.raw = json.loads(self.source_string)
        self.loaded = True
        return self.parse_data()

    def save_string(self, model):
        temp_json = self.gen_elem(model, self.schema, None, [])
        self.source_string = json.dumps(temp_json)
        return self.source_string

import copy
import json
import yaml
import re


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
# It is like an abstract syntax tree, but more focused on meaning than syntax
# Generating takes a model and creates the JSON string equivalent.
#
# Grammar elements are Dictionaries, Switch Dictionaries, Lists, Enums and Atoms
# Dictionaries and switch dictionaries have keys that map to elements
# For complete grammars, all keys must be present
# For minimal grammars, only non-default keys must be present
# Switch dictionaries have an switch key which must be an enum, and a set of keys for each enum value.
# This allows a choice mechanism
# Switch Dicts have an optional set of "common keys" which are common to all switches
# Lists are fixed length lists, in the minimal grammars, they can be truncated.
# Lists can also be unlimited (length == 0), only for minimal grammars
# Enums are lists of constants, used for color names (for example) or for switch keys in dictionaries
# Atoms are ints, strings, or booleans
#
# All grammar elements have var, model and cleanup bindings (optional)
# A var binding means that when that element is encountered while parsing, it is bound to that variable in the current
# model.
# A model binding means that model (python class) is used for parsing that element and all subelements
# A cleanup binding is a function that runs in the parse, after parsing an element, to clean up as needed
# It is used, for example, in a MIDI message where some of the data is present, but the type is None. It replaces
# the message with Nonw
#
# Atoms also have optional default and value attributes. The default value is what is normally expected, and is left
# out when creating a model (only significant information is in the model, even for complete grammars).
# The value attribute requires a specific value for the atom. This is used for elements not yet covered, so that if
# a configuration file has them, an error is flagged rather than ignoring them.
# defaults and values can also be functions. These functions take 3 arguments: the value being examined, the "context",
# and the list position:
#  The value being examined is the element being parsed, if parsing, and may be a value pulled from a model if genning
# The "context" is the immediately enclosing dictionary or list element
# The list position is a list of integers, representing which position in the list this element occurred in, with the
# innermost being the last in the list
#
# Models are python classes, with variables mapping to values.
# All models must inherit from JsonGrammarModel

class JsonGrammarException(Exception):
    """used for exceptions raised during parsing"""
    pass


class JsonGrammarModel:
    """Base class for models, includes the modified boolean"""
    def __init__(self, name):
        self.modified = False
        self.name = name


class JsonGrammarNode:
    def __init__(self, var=None, model=None, cleanup=None):
        self.variable = None
        self.model = None
        self.cleanup = None
        if var is not None:
            self.variable = var
        if model is not None:
            self.model = model
        if cleanup is not None:
            self.cleanup = cleanup

    # Base methods, keeps the child method signatures correct
    def parse(self, grammar, elem, name, context, list_pos, model):
        raise JsonGrammarException("not implemented")

    def gen(self, grammar, model, context, list_pos):
        raise JsonGrammarException("not implemented")


# Base class for Dict and SwitchDict nodes
class DictBase(JsonGrammarNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def make_key(key_name, key_schema, required=False):
        return {'name': key_name, 'schema': key_schema, 'required': required}

    @staticmethod
    def check_elem(elem):
        if not isinstance(elem, dict):
            raise JsonGrammarException('type_not_dict', "parse called on non_dict")

    def parse_keys(self, grammar, elem, name, list_pos, model, keys, result, seen_keys):
        name = name + ":" + self.name
        self.check_elem(elem)

        # The list of keys seen ensures we don't allow keys to appear twice
        # Found keys is the number of keys found in the elem while processing the schema
        # If this is not the total number of keys in the elem, some keys didn't match
        found_keys = len(seen_keys)
        found_keys_name = []
        for key in seen_keys:
            found_keys_name.append(key)

        # process each schema key
        for key in keys:
            if key['name'] not in elem:
                if grammar.minimal and not key['required']:
                    key_result = None
                else:
                    raise JsonGrammarException(
                        'dict_bad_keys',
                        "Parse position: " + name + ", error: parse dictionary/switch dictionary expected key: \"" +
                        key['name'] + "\" but didn't find it in " + str(elem.keys()))
            else:
                found_keys += 1
                found_keys_name.append(key['name'])
                # Note we update the context with the elem for sub-parsing
                key_result = grammar.parse(elem[key['name']], key['schema'], name + ':' + key['name'], elem,
                                           list_pos, model)
            if key['name'] in seen_keys:
                raise JsonGrammarException('dict_duplicate_keys', 'grammar has duplicate keys')
            seen_keys[key['name']] = True
            # Only store if significant
            if key_result is not None:
                result[key['name']] = key_result

        # Make sure all keys in the elem were processed
        if found_keys != len(elem):
            missing_keys = []
            for key in elem:
                if key not in found_keys_name:
                    missing_keys.append(key)
            message = 'While parsing ' + name + ' the following keys are undefined: '
            message += ", ".join(missing_keys)
            raise JsonGrammarException('dict_bad_keys', message)
        if result == {}:
            return None
        return result

    # gen the keys of a dict or a switch dict
    # found keys is the number of keys found (0 for dicts, 1 for switch dicts, since we found the switch key)
    # the model is either None, a model object, or a dictionary
    # If none or a object, we pass directly to the sub-gen
    # If a dictionary we get the key out of the model and use that
    # If an atom uses the context function, keys are added to the context in the order they appear in the schema
    @staticmethod
    def gen_keys(grammar, model, keys, list_pos, result, variable_result, found_keys):
        model_is_dict = isinstance(model, dict)
        if model is not None and not isinstance(model, JsonGrammarModel) and not model_is_dict:
            raise JsonGrammarException('type_not_dict', "gen called on non dict")

        # Determine the model for genning sub elements
        sub_model = model
        for key in keys:
            if model_is_dict:
                # Model is a dictionary, look up the key name to get the submodel
                sub_model = None
                if key['name'] in model:
                    sub_model = model[key['name']]
                    found_keys += 1
            result[key['name']] = grammar.gen(sub_model, key['schema'], result, list_pos)
            if result[key['name']] is not None:
                variable_result[key['name']] = result[key['name']]

        if model_is_dict and found_keys != len(model.keys()):
            raise JsonGrammarException('dict_bad_keys', "gen_dict has unknown key in model")
        if grammar.minimal:
            if variable_result == {}:
                return None
            else:
                return variable_result
        else:
            return result


class Dict(DictBase):
    def __init__(self, name, keys, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.keys = keys

    # parse_dict
    # elem is the dictionary element to be parsed
    # name is the debugging trail
    # list_pos and model as documented above
    #
    # The schema name is added to the debugging trail
    #
    # There are two modes, complete or minimal
    # In complete, all keys must appear to be sub-parsed
    # In minimal, keys need not appear, but we must still make sure that all appearing keys are in the grammar
    def parse(self, grammar, elem, name, context, list_pos, model):
        return super().parse_keys(grammar, elem, name, list_pos, model, self.keys, {}, {})

    # generate a dictionary element
    # returns significant keys when minimal, or the entire dict when complete
    def gen(self, grammar, model, context, list_pos):
        result = {}
        variable_result = {}
        found_keys = 0

        return super().gen_keys(grammar, model, self.keys, list_pos, result, variable_result, found_keys)


class SwitchDict(DictBase):
    def __init__(self, name, switch_key, case_keys, common_keys=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.switch_key = switch_key
        self.case_keys = case_keys
        self.common_keys = common_keys
        if self.common_keys is None:
            self.common_keys = []

    # same as parse_dict except
    # we must parse the switch key into a value, even if it is the default
    def parse(self, grammar, elem, name, context, list_pos, model):
        self.check_elem(elem)
        switch_key = self.switch_key
        if switch_key['name'] not in elem:
            raise JsonGrammarException('missing_switch', 'missing switch element')
        # Figure out what the switch value is
        switch_value = switch_key['schema'].parse(grammar, elem[switch_key['name']], name, None, [], None)
        if switch_value is None:
            switch_value = switch_key['schema'].default
        if switch_value not in self.case_keys:
            raise JsonGrammarException('bad_switch', 'switch element not in case keys')
        case_keys = self.case_keys[switch_value]
        all_keys = self.common_keys + case_keys

        parse_value = grammar.parse(elem[switch_key['name']], switch_key['schema'], name, None, list_pos, model)
        result = {}
        if parse_value is not None:
            result[switch_key['name']] = parse_value
        seen_keys = {switch_key['name']: True}

        return super().parse_keys(grammar, elem, name, list_pos, model, all_keys, result, seen_keys)

    # generate a switch key element
    # returns significant keys when minimal, or the entire dict when complete

    # Get the switch key value.
    #   It may be None, in which case get the default
    # Build the result
    # Note that the result is used as the context too, and this is not thoroughly understood
    # This affects value and default functions which try to access the switch key
    # I don't have any use cases yet
    def gen(self, grammar, model, context, list_pos):
        # Determine what the switch is
        switch_model = model
        if isinstance(model, dict):
            if self.switch_key['name'] in model:
                switch_model = model[self.switch_key['name']]
            else:
                switch_model = None
        switch_value = grammar.gen(switch_model, self.switch_key['schema'], {}, list_pos)

        defaulted_switch_value = switch_value
        if defaulted_switch_value is None:
            defaulted_switch_value = self.switch_key['schema'].default
        if defaulted_switch_value not in self.case_keys:
            raise JsonGrammarException('switch_dict_bad_switch', 'invalid switch in model')
        keys = self.case_keys[defaulted_switch_value] + self.common_keys
        result = {}
        variable_result = {}
        if switch_value is not None:
            result = {self.switch_key['name']: switch_value}
            variable_result = {self.switch_key['name']: switch_value}
        found_keys = 1

        return super().gen_keys(grammar, model, keys, list_pos, result, variable_result, found_keys)


class List(JsonGrammarNode):
    def __init__(self, length, schema, **kwargs):
        super().__init__(**kwargs)
        self.length = length
        self.schema = schema

    # parse_list
    # for complete grammars, the list must be the exact length of the schema
    # for minimal grammars, the list can be shorter
    # If the schema list length is 0, there is no maximum length (only used with minimal grammars)
    # The significant result is a list with all significant values filled in.
    # Note that the list is not compacted, embedded insignificant values are kept with None
    # If the entire list is empty, None is returned
    def parse(self, grammar, elem, name, context, list_pos, model):
        no_max = self.length == 0
        if not isinstance(elem, list):
            raise JsonGrammarException('type_not_list', "parse_list called on non list")
        if not grammar.minimal and no_max:
            raise JsonGrammarException('unlimited_list_complete_grammar', 'length 0 with complete grammar')

        list_length = self.length
        if list_length == 0:
            list_length = len(elem)

        if len(elem) != list_length:
            if not (grammar.minimal and len(elem) < list_length):
                raise JsonGrammarException('list_bad_length', "parse_list called with wrong length list")

        result = [None] * list_length
        modified = False
        for new_list_pos, list_elem in enumerate(elem):
            if list_elem is not None:
                entry_result = grammar.parse(list_elem, self.schema, name, elem, list_pos + [new_list_pos],
                                             model)
                if entry_result is not None:
                    modified = True
                    result[new_list_pos] = entry_result
        if modified:
            if grammar.minimal:
                prune_list(result)
                if len(result) == 0:
                    result = None
            return result
        else:
            return None

    # generate a list from a model
    # For a complete grammar, this is a full length list
    # For a minimal grammar, it is only up to the last non-None element
    # For zero length lists, this is only minimal grammar, and only for list models
    # For zero length lists, and non list models, the current behavior is an empty list. I don't have a use case,
    # so I am not sure this is correct
    # The model can be None, using only defaults
    # The model can be a model, pass through to sub elements
    # The model can be a list, the list elements are used in sub-parsing
    def gen(self, grammar, model, context, list_pos):
        is_list = isinstance(model, list)
        unlimited = self.length == 0
        if model is not None and not isinstance(model, JsonGrammarModel):
            if not is_list:
                raise JsonGrammarException('model_schema_mismatch', "gen_list got non list")
            if not grammar.minimal and not unlimited and len(model) != self.length:
                raise JsonGrammarException('list_bad_length', "gen_list called with wrong length list")
            if grammar.minimal and not unlimited and len(model) > self.length:
                raise JsonGrammarException('list_bad_length', "gen_list called with wrong length list")

        list_length = self.length
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
            result[new_list_pos] = grammar.gen(sub_model, self.schema, result, list_pos + [new_list_pos])
        if grammar.minimal:
            prune_list(result)
            if len(result) == 0:
                result = None
        return result


class Enum(JsonGrammarNode):
    def __init__(self, base, default, **kwargs):
        super().__init__(**kwargs)
        self.base = base
        if default is not None:
            try:
                base.index(default)
            except ValueError:
                raise JsonGrammarException('bad_enum_value', "bad enum value")
        self.default = default

    # parse_enum parses an enum element
    # The result is significant if it is not default
    def parse(self, grammar, elem, name, context, list_pos, model):
        if not isinstance(elem, str):
            raise JsonGrammarException('enum_wrong_type', "parse_enum called with element not a str")
        # Make sure the elem is valid
        try:
            self.base.index(elem)
        except ValueError:
            raise JsonGrammarException('bad_enum_value', "bad enum value")
        if self.default is not None and elem == self.default:
            return None
        return elem

    # generate an enum
    # This doesn't handle default/value functions
    # I don't have a use case
    def gen(self, grammar, model, context, list_pos):
        enum_value = None
        if self.default is not None:
            enum_value = self.default

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

        if grammar.minimal:
            return variable_result
        else:
            return result


class Atom(JsonGrammarNode):
    def __init__(self, atom_type, default=None, value=None, **kwargs):
        super().__init__(**kwargs)
        self.type = atom_type
        self.default = default
        self.value = value
        if self.default is not None and self.value is not None:
            raise JsonGrammarException('both_value_default', 'Schema atom has more than 1 value, default set')

    # parse_atom parses a number, string, or boolean
    # It is the same for complete and minimal grammars
    # Significant values differ from the default
    # If the schema is 'value', then the value is required. This is used for portions of the MC6Pro file that are
    # not yet handled - we will throw an error when getting a config where features are used
    def parse(self, grammar, elem, name, context, list_pos, model):
        if not isinstance(elem, self.type):
            raise JsonGrammarException('atom_wrong_type', "parse_atom called with element having wrong type")
        if self.default is not None and self.value is not None:
            raise JsonGrammarException('both_value_default', 'Schema atom has more than 1 value, skip and default')
        target = None
        value = False
        if self.default is not None:
            target = self.default
        if self.value is not None:
            target = self.value
            value = True
        if callable(target):
            target_elem = target(elem, context, list_pos)
        else:
            target_elem = target

        if elem != target_elem:
            if value:
                msg = "parse atom called with " + str(elem) + " not matching schema " + str(target_elem)
                msg += " in " + name
                raise JsonGrammarException('atom_wrong_value', msg)
            result = elem
        else:
            result = None
        return result

    # Generate an atom
    # model is an atom, None, or model object
    # None or model object is ignored, result is the default or value
    # if atom, that is the result
    # for minimal grammars, we need to check if the atom value is default (but not value)
    def gen(self, grammar, model, context, list_pos):
        is_atom = not (model is None or isinstance(model, JsonGrammarModel))
        if isinstance(model, JsonGrammarModel):
            model = None

        atom_value = None
        if self.value is not None:
            atom_value = self.value
        elif self.default is not None:
            atom_value = self.default
        elif not grammar.minimal:
            raise JsonGrammarException('no_value_default', "Missing both value and default in atom")
        if callable(atom_value):
            atom_value = atom_value(model, context, list_pos)

        variable_result = None
        if not is_atom:
            result = atom_value
            # Weird case, but if model is None we want to set the value
            if self.value is not None:
                variable_result = atom_value
        else:
            if model == atom_value:
                result = atom_value
            elif self.value is None:
                variable_result = model
                result = model
            else:
                raise JsonGrammarException('model_schema_mismatch', "atom has wrong value in model and schema")

        if not grammar.minimal and result is None:
            raise JsonGrammarException('programmer_error', 'gen_atom resulted in None')

        if grammar.minimal:
            return variable_result
        else:
            return result


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


false_atom = Atom(bool, value=False)
true_atom = Atom(bool, value=True)
zero_atom = Atom(int, value=0)
empty_atom = Atom(str, value='')
identity_atom = Atom(int, value=identity)
identity2_atom = Atom(int, value=identity2)


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

    # Parsing
    # Parson a JSON/YAML subexpression can store the result in 3 ways
    # If a model is specified, all sub-subexpressions are parsed with this model
    # If a variable is specified, the result of the parse is stored in that variable in the current model
    # If neither is specified, the result is returned as the result of the parse
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
    # schema is the grammar node for the element
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
    def parse(self, elem: object, schema: object, name: object, context: object, list_pos: object,
              model: object) -> object:
        if schema is None:
            raise JsonGrammarException('no_schema', "Schema is None")

        new_model = False
        # This really belongs inside the 'if' where we create a new model
        # But PyCharm complains then that old_model might be reffed before assignment below
        old_model = model
        if schema.model is not None:
            model = schema.model()
            new_model = True

        result = schema.parse(self, elem, name, context, list_pos, model)

        if new_model:
            if result is not None:
                raise JsonGrammarException('unconsumed', "Model was used, but some result not added")
            if model.modified:
                result = model
            model = old_model

        if schema.cleanup is not None:
            result = schema.cleanup(result, context, list_pos)

        if schema.variable is not None and result is not None:
            model.modified = True
            model_vars = vars(model)
            if schema.variable not in model_vars:
                raise JsonGrammarException('model_missing_var', 'In ' + name + ' the model ' + model.name +
                                           ' is missing the variable ' + schema.variable)
            if model_vars[schema.variable] is not None:
                raise JsonGrammarException('multiply_assigned_var', 'Variable is assigned multipe times')
            model_vars[schema.variable] = result
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
    def gen(self, model, schema, context, list_pos):
        if schema is None:
            raise JsonGrammarException('no_schema', "Schema is None")

        # If the schema specifies a model, and if the current model is not an instance of this
        # then we need to not use the current model
        if schema.model is not None and not isinstance(model, schema.model):
            sub_model = None
        else:
            sub_model = model

        if schema.variable is not None:
            # If model is None, that means the model was not populated, everything is default
            if model is not None:
                if not isinstance(model, JsonGrammarModel):
                    raise JsonGrammarException('variable_without_model',
                                               "In gen_elem, have a variable that isn't a model")
                model_vars = vars(model)
                if schema.variable not in model_vars.keys():
                    # TODO: Need name/breadcrumb better error
                    raise JsonGrammarException('variable_not_in_model',
                                               'The variable ' + schema.variable + ' is not in the model ' +
                                               model.name)
                sub_model = model_vars[schema.variable]

        result = schema.gen(self, sub_model, context, list_pos)
        return result

    def parse_config(self, elem):
        return self.parse(elem, self.schema, "", None, [], None)

    def gen_config(self, model):
        return self.gen(model, self.schema, None, [])


class JsonGrammarFile:
    def __init__(self, filename=None, is_yaml=None):
        if filename is None:
            if is_yaml is None:
                raise JsonGrammarException('must specify filename or is_yaml')
            self.is_yaml = is_yaml
            self.filename = None
        else:
            self.filename = filename
            if re.search(r'\.yaml$', filename):
                self.is_yaml = True
            elif re.search(r'\.json$', filename):
                self.is_yaml = False
            else:
                raise JsonGrammarException('File is not json or yaml')

    def save(self, data):
        if self.filename is not None:
            with open(self.filename, "w") as write_file:
                if self.is_yaml:
                    yaml.dump(data, write_file)
                else:
                    json.dump(data, write_file, indent=4)
        else:
            raise JsonGrammarException('Not implemented')

    def load(self):
        if self.filename is not None:
            with open(self.filename, "r") as read_file:
                if self.is_yaml:
                    result = yaml.safe_load(read_file)
                else:
                    result = json.load(read_file)
        else:
            raise JsonGrammarException('Not implemented')
        if result is None:
            result = {}
        return result

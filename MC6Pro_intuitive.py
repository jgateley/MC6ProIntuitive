import copy

import MC6Pro_grammar
import semver
import json_grammar as jg
from IntuitiveException import IntuitiveException
import intuitive_message as im
import intuitive_midi_channel

# This is the intuitive grammar, it is a minimal grammar
# It also includes to_base and from_base methods, these convert intuitive models to base models
#
# The main features:
# It is minimal, you only include what is significant, making it easier to edit the config file
# It is not deeply nested, again for ease of editing
# MIDI messages are named and are at the top level
# Naming makes them more intuitive
# At the top level: they are easily reused

intuitive_version = '0.2.1'

preset_colors = ["black", "lime", "blue", "color3", "yellow", "orchid", "gray", "white",
                 "orange", "red", "skyblue", "deeppink", "olivedrab", "mediumslateblue", "darkgreen", "color15",
                 "color16", "color17", "color18", "color19", "color20", "color21", "color22", "color23",
                 "color24", "color25", "color26", "color27", "color28", "aqua", "turquoise", "cadetblue",
                 "steelblue", "lightsteelblue", "tan", "brown", "cornsilk", "maroon", "lavender", "teal",
                 "darkseagreen", "forestgreen", "olive", "indigo", "blueviolet", "thistle", "rebeccapurple", "gold",
                 "khaki", "darkkhaki", "lightyellow", "lightsalmon", "tomato", "orangered", "darkorange", "indianred",
                 "salmon", "firebrick", "darkred", "lightpink", "hotpink", "palevioletred", "slategray", "lightgray",
                 "color64", "color65", "color66", "color67", "color68", "color69", "color70", "color71",
                 "color72", "color73", "color74", "color75", "color76", "color77", "color78", "color79",
                 "color80", "color81", "color82", "color83", "color84", "color85", "color86", "color87",
                 "color88", "color89", "color90", "color91", "color92", "color93", "color94", "color95",
                 "color96", "color97", "color98", "color99", "color100", "color101", "color102", "color103",
                 "color104", "color105", "color106", "color107", "color108", "color109", "color110", "color111",
                 "color112", "color113", "color114", "color115", "color116", "color117", "color118", "color119",
                 "color120", "color121", "color122", "color123", "color124", "color125", "color126", "default"]
preset_default_color = preset_colors[7]
preset_empty_color = preset_colors[0]

preset_toggle_state = ["one", "two", "both", "shift"]
preset_toggle_state_default = preset_toggle_state[2]

preset_message_trigger = ["No Action", "Press", "Release", "Long Press", "Long Press Scroll", "Long Press Release",
                          "Release All", "Double Tap", "Double Tap Release", "Long Double Tap",
                          "Long Double Tap Release", "On First Engage", "On First Engage (send only this)",
                          "On Disengage"]
preset_message_trigger_default = preset_message_trigger[1]

engage_preset_action = ["No Action", "Press", "Release", "Long Press", "Long Press Scroll", "Long Press Release",
                        "Release All", "Double Tap", "Double Tap Release", "Long Double Tap",
                        "Long Double Tap Release"]
engage_preset_action_default = engage_preset_action[0]

bank_message_trigger = ["unused", "On Enter Bank", "On Exit Bank", "On Enter Bank - Execute Once Only",
                        "On Exit Bank - Execute Once Only", "On Enter Bank - Page 1", "On Enter Bank - Page 2",
                        "On Toggle Page - Page 1", "On Toggle Page - Page 2"]
bank_message_trigger_default = bank_message_trigger[1]

navigator_mode = ["None", "One Button", "Two Button"]
navigator_mode_default = "None"


class MessageCatalog:
    def __init__(self, messages=None):
        self.catalog = {}
        if messages is not None:
            for message in messages:
                self.add(message)

    def add(self, intuitive_message):
        if intuitive_message.name in self.catalog:
            if self.catalog[intuitive_message.name] != intuitive_message:
                raise IntuitiveException("name_appears", "Midi message name already exists, and is different")

        for message_name in self.catalog:
            if self.catalog[message_name] == intuitive_message:
                return message_name

        self.catalog[intuitive_message.name] = intuitive_message
        return intuitive_message.name

    def lookup(self, name):
        try:
            return self.catalog[name]
        except KeyError as e:
            msg = "Message " + e.args[0] + " not found\n"
            msg += ", ".join(sorted(list(self.catalog.keys())))
            msg += "\n"
            raise IntuitiveException('message_not_found', msg)

    def to_list(self):
        result = []
        for message_name in self.catalog:
            result.append(self.catalog[message_name])
        return result


class ColorsCatalog:
    def __init__(self, colors=None):
        self.catalog = {}
        if colors is not None:
            for color in colors:
                self.add(color)

    def add(self, schema):
        if schema.name in self.catalog:
            if schema != self.catalog[schema.name]:
                raise IntuitiveException("mismatch", "Schema name already exists, and is different")
        for catalog_schema_name in self.catalog:
            if self.catalog[catalog_schema_name] == schema:
                return catalog_schema_name
        self.catalog[schema.name] = schema
        return schema.name

    def add_preset_schema(self, bank_color_schema, name_color, name_toggle_color, shifted_name_color, background_color,
                          background_toggle_color):
        name_color = ColorSchema.from_base_preset_color(name_color, False)
        name_toggle_color = ColorSchema.from_base_preset_color(name_toggle_color, False)
        shifted_name_color = ColorSchema.from_base_preset_color(shifted_name_color, False)
        background_color = ColorSchema.from_base_preset_color(background_color, True)
        background_toggle_color = ColorSchema.from_base_preset_color(background_toggle_color, True)
        schema = ColorSchema.make_preset_schema(bank_color_schema.bank_color, bank_color_schema.bank_background_color,
                                                name_color, name_toggle_color, shifted_name_color,
                                                background_color, background_toggle_color)
        for other_schema in self.catalog:
            if schema.same_colors(self.catalog[other_schema]):
                return other_schema
        schema.build_name(False)
        return self.add(schema)

    def add_bank_schema(self, schema):
        for other_schema in self.catalog:
            if schema.same_bank_colors(self.catalog[other_schema]):
                return other_schema
        schema.build_name(True)
        return self.add(schema)

    def lookup(self, name):
        if name is None:
            if 'default' in self.catalog:
                return self.catalog['default']
            return ColorSchema()
        return self.catalog[name]

    def to_list(self):
        result = []
        for schema_name in self.catalog:
            result.append(self.catalog[schema_name])
        return result

    def get_navigator_schema(self):
        if 'navigator' in self.catalog:
            return 'navigator'
        elif 'default' in self.catalog:
            return 'default'
        else:
            return None


class Navigator:
    @staticmethod
    def clone_bank(bank, overflow_number, presets):
        result = IntuitiveBank()
        result.name = bank.name + " (" + str(overflow_number + 2) + ")"
        result.description = bank.description
        result.colors = bank.colors
        result.presets = presets
        return result

    def __init__(self, mode, banks, colors_catalog, message_catalog):
        self.mode = mode
        self.banks = banks
        self.colors_schema = colors_catalog.get_navigator_schema()
        self.message_catalog = message_catalog
        if mode == "One Button":
            self.main_action = "Release"
            self.second_action = "Long Press"
        else:
            self.main_action = "Press"
            self.second_action = "Press"
        self.blank_preset = self.mk_preset('', [])
        return_to_home_message = self.mk_bank_jump_message('Home')
        self.return_to_home_preset = self.mk_preset('Home', self.mk_preset_messages(return_to_home_message))
        self.next_page_message = im.IntuitiveMessage.make_toggle_page_message('next_page', True, message_catalog)
        self.next_page_preset = self.mk_preset('Next', self.mk_preset_messages(self.next_page_message))
        self.prev_page_message = im.IntuitiveMessage.make_toggle_page_message('prev_page', False, message_catalog)
        self.prev_page_preset = self.mk_preset('Previous', self.mk_preset_messages(self.prev_page_message))
        self.prev_next_page_preset = self.mk_preset('Previous/Next',
                                                    self.mk_preset_messages(self.prev_page_message,
                                                                            self.next_page_message))

    def pad_presets(self, presets, desired_length):
        while len(presets) < desired_length:
            presets.append(self.blank_preset)

    def mk_bank_jump_message(self, bank_name):
        return im.IntuitiveMessage.make_bank_jump_message('navigator ' + bank_name, bank_name, 0, self.message_catalog)

    def mk_preset_messages(self, main_message, second_message=None):
        if isinstance(main_message, IntuitivePresetMessage):
            first_message = main_message
        else:
            first_message = IntuitivePresetMessage.make(main_message, self.main_action)
        result = [first_message]
        if second_message is not None:
            result.append(IntuitivePresetMessage.make(second_message, self.second_action))
        return result

    def mk_preset(self, name, messages):
        return IntuitivePreset.make(name, messages, self.colors_schema)

    # Clean up the bank list (remove internal Nones)
    # Add in the roadmap bank at the beginning
    # Fill in the roadmap presets, and add the home preset to each bank
    # Go through each bank:
    #   Add the home preset or prev page preset
    #   Add next page preset if needed
    # Go through each real bank and add the home preset, and page moving presets
    def build(self):
        self.add_home_bank()
        self.add_page_up_down()

    def add_home_bank(self):
        jg.compact_list(self.banks)
        home_bank = self.get_home_bank()
        # And add in the navigator presets and the return home preset
        for bank in self.banks:
            home_bank.presets.append(self.jump_to_bank_preset(bank))
            self.add_navigator_home_preset(bank)
        self.banks.insert(0, home_bank)

    def get_home_bank(self):
        result = IntuitiveBank()
        result.name = "Home"
        result.description = "Navigation Home"
        result.colors = self.colors_schema
        result.presets = []
        return result

    def jump_to_bank_preset(self, bank):
        jump_to_bank_message = self.mk_bank_jump_message(bank.name)
        return self.mk_preset(bank.name, self.mk_preset_messages(jump_to_bank_message))

    def add_navigator_home_preset(self, bank):
        home_offset = 2
        if self.mode == "One Button":
            home_offset = 5
        if bank.presets is None:
            bank.presets = []
        self.pad_presets(bank.presets, home_offset)
        bank.presets.insert(home_offset, copy.deepcopy(self.return_to_home_preset))

    def add_page_up_down(self):
        bank_number = 0
        while bank_number < len(self.banks):
            bank = self.banks[bank_number]
            presets = self.add_page_up_down_bank(bank)
            prev_bank = bank
            bank_number += 1
            overflow_number = 0
            while len(presets) > 0:
                bank = self.clone_bank(bank, overflow_number, presets)
                self.add_next_bank(prev_bank, bank)
                self.add_previous_bank(bank, prev_bank)
                self.banks.insert(bank_number + overflow_number, bank)
                presets = self.add_page_up_down_bank(bank)
                prev_bank = bank
                overflow_number += 1
            bank_number += overflow_number

    def add_paging_preset_pair(self, bank, page):
        pos = page * 6 + 5
        offset = pos + 3
        if self.mode == "One Button":
            offset = pos + 6
        if bank.presets[pos] == self.prev_page_preset:
            # The previous page has already added a next/previous pair, this is the "previous" part of the pair
            bank.presets[pos] = self.prev_next_page_preset
        elif bank.presets[pos].short_name == 'Previous':
            # In one button mode, one page 1 of an overflow bank, we need to add a next page
            preset = bank.presets[pos]
            preset.short_name = 'Previous/Next'
            preset.messages = self.mk_preset_messages(preset.messages[0], self.next_page_message)
        elif bank.presets[pos].short_name == 'Home':
            # Add a page up message to the return to home preset
            preset = bank.presets[pos]
            preset.short_name = 'Home/Next'
            preset.messages = self.mk_preset_messages(preset.messages[0], self.next_page_message)
        else:
            bank.presets.insert(pos, self.next_page_preset)
        self.pad_presets(bank.presets, offset)
        bank.presets.insert(offset, self.prev_page_preset)

    def add_page_up_down_bank(self, bank):
        if len(bank.presets) <= 6:
            return []
        self.add_paging_preset_pair(bank, 0)
        if len(bank.presets) <= 12:
            return []
        self.add_paging_preset_pair(bank, 1)
        if len(bank.presets) <= 18:
            return []
        self.add_paging_preset_pair(bank, 2)
        if len(bank.presets) <= 24:
            return []
        if self.mode == "One Button":
            limit = 24
        else:
            limit = 23
        result = bank.presets[limit:]
        bank.presets = bank.presets[0:limit]
        return result

    def add_next_bank(self, bank, next_bank):
        next_page_message = self.mk_bank_jump_message(next_bank.name)
        if self.mode == "One Button":
            prev_next_page_preset = self.mk_preset('Previous/Next',
                                                   self.mk_preset_messages(self.prev_page_message, next_page_message))
            bank.presets[23] = prev_next_page_preset
        else:
            next_page_preset = self.mk_preset('Next', self.mk_preset_messages(next_page_message))
            bank.presets.insert(23, next_page_preset)

    def add_previous_bank(self, bank, previous_bank):
        previous_page_message = self.mk_bank_jump_message(previous_bank.name)
        previous_page_preset = self.mk_preset('Previous', self.mk_preset_messages(previous_page_message))
        position = 2
        if self.mode == "One Button":
            position = 5
        while len(bank.presets) < position:
            bank.presets.append(self.blank_preset)
        bank.presets.insert(position, previous_page_preset)


# Colors Schemas
class ColorSchema(jg.JsonGrammarModel):
    @staticmethod
    def from_base_bank_color(color):
        if color is None:
            return preset_colors[127]
        return preset_colors[color]

    @staticmethod
    def to_base_bank_color(color):
        if color == "default" or color is None:
            return None
        return preset_colors.index(color)

    @staticmethod
    def to_base_preset_color(color, is_background):
        if is_background:
            if color == preset_colors[0]:
                return None
        else:
            if color == preset_colors[7]:
                return None
        if color is None:
            return None
        return preset_colors.index(color)

    @staticmethod
    def from_base_preset_color(color, is_background):
        if color is None:
            if is_background:
                return preset_colors[0]
            return preset_colors[7]
        return preset_colors[color]

    @staticmethod
    def make_preset_schema(bank_color, bank_background_color, preset_color, toggle_color, preset_shifted_color,
                           preset_background_color, toggle_background_color, name=None):
        schema = ColorSchema()
        if name is not None:
            schema.name = name
        schema.bank_color = bank_color
        schema.bank_background_color = bank_background_color
        schema.preset_color = preset_color
        schema.preset_background_color = preset_background_color
        schema.preset_toggle_color = toggle_color
        schema.preset_toggle_background_color = toggle_background_color
        schema.preset_shifted_color = preset_shifted_color
        return schema

    def __init__(self):
        super().__init__('ColorSchema')
        self.name = None
        self.bank_color = None
        self.bank_background_color = None
        self.preset_color = None
        self.preset_background_color = None
        self.preset_toggle_color = None
        self.preset_toggle_background_color = None
        self.preset_shifted_color = None

    def __eq__(self, other):
        result = isinstance(other, ColorSchema)
        result = result and self.name == other.name
        result = result and self.bank_color == other.bank_color
        result = result and self.bank_background_color == other.bank_background_color
        result = result and self.preset_color == other.preset_color
        result = result and self.preset_background_color == other.preset_background_color
        result = result and self.preset_toggle_color == other.preset_toggle_color
        result = result and self.preset_toggle_background_color == other.preset_toggle_background_color
        result = result and self.preset_shifted_color == other.preset_shifted_color
        if not result:
            self.modified = True
        return result

    def same_colors(self, other):
        result = isinstance(other, ColorSchema)
        result = result and self.bank_color == other.bank_color
        result = result and self.bank_background_color == other.bank_background_color
        result = result and self.preset_color == other.preset_color
        result = result and self.preset_background_color == other.preset_background_color
        result = result and self.preset_toggle_color == other.preset_toggle_color
        result = result and self.preset_toggle_background_color == other.preset_toggle_background_color
        result = result and self.preset_shifted_color == other.preset_shifted_color
        if result:
            self.modified = True
        return result

    def same_bank_colors(self, other):
        result = isinstance(other, ColorSchema)
        result = result and self.bank_color == other.bank_color
        result = result and self.bank_background_color == other.bank_background_color
        if result:
            self.modified = True
        return result

    def build_name(self, is_bank):
        self.name = self.bank_color + ':' + self.bank_background_color
        if not is_bank:
            self.name += ':' + \
                self.preset_color + ':' + self.preset_background_color + ':' + \
                self.preset_toggle_color + ':' + self.preset_toggle_background_color

    def from_base_bank(self, bank):
        self.bank_color = self.from_base_bank_color(bank.text_color)
        self.bank_background_color = self.from_base_bank_color(bank.background_color)


# This is the preset component of a MIDI message
# The trigger, and the toggle state
class IntuitivePresetMessage(jg.JsonGrammarModel):

    @staticmethod
    def make(message_name, trigger):
        result = IntuitivePresetMessage()
        result.midi_message = message_name
        result.trigger = trigger
        return result

    def __init__(self):
        super().__init__('IntuitivePresetMessage')
        self.trigger = None
        self.toggle = None
        self.midi_message = None

    def __eq__(self, other):
        result = (isinstance(other, IntuitivePresetMessage) and self.trigger == other.trigger and
                  self.toggle == other.toggle and self.midi_message == other.midi_message)
        if not result:
            self.modified = True
        return result

    def from_base(self, base_message, base_bank, message_catalog, bank_catalog, midi_channels):
        if base_message.trigger is not None:
            if base_message.trigger == 1:
                self.trigger = None
            else:
                self.trigger = preset_message_trigger[base_message.trigger]
        else:
            self.trigger = preset_message_trigger[0]
        if base_message.toggle_group is not None:
            self.toggle = preset_toggle_state[base_message.toggle_group]
        midi_message = im.IntuitiveMessage()
        self.midi_message = midi_message.from_base(base_message, base_bank, message_catalog, bank_catalog,
                                                   midi_channels)

    # Pull the MIDI message out of the dictionary, then convert it to the base model
    def to_base(self, message_catalog, bank_catalog, midi_channels, intuitive_bank, intuitive_preset):
        base_message = MC6Pro_grammar.MidiMessage()
        if self.trigger is not None:
            base_message.trigger = preset_message_trigger.index(self.trigger)
        else:
            base_message.trigger = preset_message_trigger.index("Press")
        if self.toggle is not None:
            base_message.toggle_group = preset_toggle_state.index(self.toggle)
        if self.midi_message is not None:
            midi_message = message_catalog.lookup(self.midi_message)
            midi_message.to_base(base_message, bank_catalog, midi_channels, intuitive_bank, intuitive_preset)
        return base_message


# This is the bank component of a MIDI message
# Only has a trigger, not a toggle
class IntuitiveBankMessage(jg.JsonGrammarModel):

    @staticmethod
    def make_on_startup(name):
        msg = IntuitiveBankMessage()
        msg.trigger = bank_message_trigger[3]  # on enter bank, execute only once
        msg.midi_message = name
        return msg

    def __init__(self):
        super().__init__('IntuitiveBankMessage')
        self.trigger = None
        self.midi_message = None

    def __eq__(self, other):
        result = isinstance(other, IntuitiveBankMessage) and self.trigger == other.trigger
        if not result:
            self.modified = True
        return result

    def from_base(self, base_message, base_bank, message_catalog, bank_catalog, midi_channels):
        if base_message.trigger is not None:
            if base_message.trigger == 1:
                self.trigger = None
            else:
                self.trigger = bank_message_trigger[base_message.trigger]
        else:
            self.trigger = bank_message_trigger[0]
        midi_message = im.IntuitiveMessage()
        self.midi_message = midi_message.from_base(base_message, base_bank, message_catalog, bank_catalog,
                                                   midi_channels)

    # Pull the MIDI message out of the dictionary, then convert it to the base model
    def to_base(self, message_catalog, bank_catalog, midi_channels, intuitive_bank, intuitive_preset):
        base_message = MC6Pro_grammar.MidiMessage()
        if self.trigger is not None:
            base_message.trigger = bank_message_trigger.index(self.trigger)
        else:
            base_message.trigger = bank_message_trigger.index(bank_message_trigger_default)
        if self.midi_message is not None:
            midi_message = message_catalog.lookup(self.midi_message)
            midi_message.to_base(base_message, bank_catalog, midi_channels, intuitive_bank, intuitive_preset)
        return base_message


class IntuitivePreset(jg.JsonGrammarModel):
    @staticmethod
    def make(short_name, messages, colors):
        result = IntuitivePreset()
        result.short_name = short_name
        result.messages = messages
        result.colors = colors
        return result

    def __init__(self):
        super().__init__('IntuitivePreset')
        self.short_name = None
        self.long_name = None
        self.toggle_name = None
        self.message_scroll = None
        self.colors = None
        self.strip_color = None
        self.strip_toggle_color = None
        self.toggle_mode = None
        self.toggle_group = None
        self.messages = None

    def __eq__(self, other):
        result = (isinstance(other, IntuitivePreset) and self.short_name == other.short_name and
                  self.long_name == other.long_name and self.toggle_name == other.toggle_name and
                  self.message_scroll == other.message_scroll and self.colors == other.colors and
                  self.strip_color == other.strip_color and self.strip_toggle_color == other.strip_toggle_color and
                  self.toggle_mode == other.toggle_mode and self.toggle_group == other.toggle_group and
                  self.messages == other.messages)
        if not result:
            self.modified = True
        return result

    def from_base(self, base_preset, base_bank, message_catalog, colors_catalog, bank_color_schema, bank_catalog,
                  midi_channels):
        self.short_name = base_preset.short_name
        self.long_name = base_preset.long_name
        self.toggle_name = base_preset.toggle_name
        self.toggle_group = base_preset.toggle_group
        if base_preset.to_msg_scroll is not None and base_preset.to_msg_scroll:
            self.message_scroll = "On"
        self.colors = colors_catalog.add_preset_schema(bank_color_schema,
                                                       base_preset.name_color, base_preset.name_toggle_color,
                                                       base_preset.shifted_name_color,
                                                       base_preset.background_color,
                                                       base_preset.background_toggle_color)
        if base_preset.strip_color is not None:
            self.strip_color = preset_colors[base_preset.strip_color]
        if base_preset.strip_toggle_color is not None:
            self.strip_toggle_color = preset_colors[base_preset.strip_toggle_color]
        self.toggle_mode = base_preset.to_toggle
        if base_preset.messages is not None:
            self.messages = [None] * 32
            for pos, base_message in enumerate(base_preset.messages):
                if base_message is not None:
                    self.messages[pos] = IntuitivePresetMessage()
                    self.messages[pos].from_base(base_message, base_bank, message_catalog, bank_catalog, midi_channels)
            jg.prune_list(self.messages)
            for message_name in message_catalog.catalog:
                message = message_catalog.catalog[message_name]
                if message.type == 'Select Exp Message':
                    message.specific_message.from_base_cleanup(self.messages)

    def to_base(self, message_catalog, colors_catalog, bank_colors_schema, bank_catalog, midi_channels, intuitive_bank):
        base_preset = MC6Pro_grammar.Preset()
        base_preset.short_name = self.short_name
        base_preset.long_name = self.long_name
        base_preset.toggle_name = self.toggle_name
        base_preset.toggle_group = self.toggle_group
        if self.message_scroll is not None and self.message_scroll == "On":
            base_preset.to_msg_scroll = True
        if self.colors is None:
            preset_colors_schema = bank_colors_schema
        else:
            preset_colors_schema = colors_catalog.lookup(self.colors)
        base_preset.name_color = preset_colors_schema.to_base_preset_color(preset_colors_schema.preset_color, False)
        base_preset.name_toggle_color = (
            preset_colors_schema.to_base_preset_color(preset_colors_schema.preset_toggle_color, False))
        base_preset.shifted_name_color = (
            preset_colors_schema.to_base_preset_color(preset_colors_schema.preset_shifted_color, False))
        base_preset.background_color = (
            preset_colors_schema.to_base_preset_color(preset_colors_schema.preset_background_color, True))
        base_preset.background_toggle_color = (
            preset_colors_schema.to_base_preset_color(preset_colors_schema.preset_toggle_background_color, True))
        if self.strip_color is not None:
            base_preset.strip_color = preset_colors.index(self.strip_color)
        if self.strip_toggle_color is not None:
            base_preset.strip_toggle_color = preset_colors.index(self.strip_toggle_color)
        base_preset.to_toggle = self.toggle_mode
        if self.messages is not None:
            for pos, message in enumerate(self.messages):
                if message is not None:
                    base_message = message.to_base(message_catalog, bank_catalog, midi_channels, intuitive_bank, self)
                    base_preset.set_message(base_message, pos)
        return base_preset

    def lookup_message(self, message_name):
        for index, message in enumerate(self.messages):
            if message.midi_message == message_name:
                return index
        raise IntuitiveException("message_not_found", "message_not_found")


class IntuitiveBank(jg.JsonGrammarModel):
    def __init__(self):
        super().__init__('IntuitiveBank')
        self.name = None
        self.description = None
        self.colors = None
        self.display_description = None
        self.clear_toggle = None
        self.messages = None
        self.presets = None
        self.exp_presets = None

    def __eq__(self, other):
        result = (isinstance(other, IntuitiveBank) and self.name == other.name and
                  self.description == other.description and
                  self.colors == other.colors and
                  self.display_description == other.display_description and
                  self.clear_toggle == other.clear_toggle and
                  self.messages == other.messages and
                  self.presets == other.presets and
                  self.exp_presets == other.exp_presets)
        if not result:
            self.modified = True
        return result

    def from_base(self, base_bank, message_catalog, colors_catalog, bank_catalog, midi_channels):
        if base_bank.short_name is not None:
            raise IntuitiveException('unimplemented', 'bank short_name')
        self.name = base_bank.name
        self.description = base_bank.description
        color_schema = ColorSchema()
        color_schema.from_base_bank(base_bank)
        self.display_description = base_bank.to_display
        self.clear_toggle = base_bank.clear_toggle
        if base_bank.messages is not None:
            self.messages = [None] * 32
            for pos, base_message in enumerate(base_bank.messages):
                if base_message is not None:
                    self.messages[pos] = IntuitiveBankMessage()
                    self.messages[pos].from_base(base_message, base_bank, message_catalog, bank_catalog, midi_channels)
            jg.prune_list(self.messages)
        if base_bank.presets is not None:
            self.presets = [None] * 24
            for pos, base_preset in enumerate(base_bank.presets):
                if base_preset is not None:
                    self.presets[pos] = IntuitivePreset()
                    self.presets[pos].from_base(base_preset, base_bank, message_catalog, colors_catalog, color_schema,
                                                bank_catalog, midi_channels)
            jg.prune_list(self.presets)
            for message_name in message_catalog.catalog:
                message = message_catalog.catalog[message_name]
                if message.type == "Trigger Messages":
                    message.specific_message.from_base_cleanup(self.presets)
        if base_bank.exp_presets is not None:
            self.exp_presets = [None] * 4
            for pos, base_preset in enumerate(base_bank.exp_presets):
                if base_preset is not None:
                    self.exp_presets[pos] = IntuitivePreset()
                    self.exp_presets[pos].from_base(base_preset, base_bank, message_catalog, colors_catalog,
                                                    color_schema, bank_catalog, midi_channels)
            jg.prune_list(self.exp_presets)
            for message_name in message_catalog.catalog:
                message = message_catalog.catalog[message_name]
                if message.type == "Trigger Messages":
                    message.specific_message.from_base_cleanup(self.exp_presets)
        self.colors = colors_catalog.add_bank_schema(color_schema)

    def to_base(self, message_catalog, colors_catalog, bank_catalog, midi_channels):
        base_bank = MC6Pro_grammar.Bank()
        base_bank.name = self.name
        base_bank.description = self.description
        bank_colors_schema = colors_catalog.lookup(self.colors)
        base_bank.text_color = bank_colors_schema.to_base_bank_color(bank_colors_schema.bank_color)
        base_bank.background_color = bank_colors_schema.to_base_bank_color(bank_colors_schema.bank_background_color)
        base_bank.to_display = self.display_description
        base_bank.clear_toggle = self.clear_toggle
        if self.messages is not None:
            for pos, message in enumerate(self.messages):
                if message is not None:
                    base_message = message.to_base(message_catalog, bank_catalog, midi_channels, self, None)
                    base_bank.set_message(base_message, pos)
        if self.presets is not None:
            for pos, preset in enumerate(self.presets):
                if preset is not None:
                    base_preset = preset.to_base(message_catalog, colors_catalog, bank_colors_schema, bank_catalog,
                                                 midi_channels, self)
                    base_bank.set_preset(base_preset, pos)
        if self.exp_presets is not None:
            for pos, preset in enumerate(self.exp_presets):
                if preset is not None:
                    base_preset = preset.to_base(message_catalog, colors_catalog, bank_colors_schema, bank_catalog,
                                                 midi_channels, self)
                    base_bank.set_exp_preset(base_preset, pos)
        return base_bank

    def lookup_preset(self, target_preset):
        for index, preset in enumerate(self.presets):
            if preset.short_name == target_preset:
                return index
        raise IntuitiveException('preset_not_found', 'Preset not found')


class MC6ProIntuitive(jg.JsonGrammarModel):
    page_size = 6

    def __init__(self):
        super().__init__('MC6ProIntuitive')
        self.midi_channels = None
        self.messages = None
        self.message_catalog = None
        self.colors = None
        self.colors_catalog = None
        self.banks = None
        self.midi_channel = None
        self.navigator = None
        self.version = None
        self.on_startup = None

    # Do not check version in equality
    def __eq__(self, other):
        result = (isinstance(other, MC6ProIntuitive) and
                  self.midi_channels == other.midi_channels and
                  self.messages == other.messages and
                  self.colors == other.colors and
                  self.banks == other.banks and
                  self.midi_channel == other.midi_channel and
                  self.navigator == other.navigator)
        if not result:
            self.modified = True
        return result

    # Parse the MIDI channels (names) first, as these are needed for MIDI messages
    # Then process the banks, gathering messages as we go, and handling bank arrangement
    # Then add all the gathered messages
    def from_base(self, base_model):
        self.midi_channels = [None] * 16
        if base_model.midi_channels is not None:
            for pos in range(0, 15):
                if base_model.midi_channels[pos] is not None:
                    self.midi_channels[pos] = intuitive_midi_channel.IntuitiveMidiChannel()
                    self.midi_channels[pos].from_base(base_model.midi_channels[pos])
        jg.prune_list(self.midi_channels)
        if base_model.banks is not None:
            self.banks = [None] * 128
            self.message_catalog = MessageCatalog()
            self.colors_catalog = ColorsCatalog()
            bank_catalog = []
            for bank in base_model.banks:
                if bank is not None:
                    bank_catalog.append(bank.name)
                else:
                    bank_catalog.append(None)
            for pos, bank in enumerate(base_model.banks):
                if bank is not None:
                    self.banks[pos] = IntuitiveBank()
                    self.banks[pos].from_base(bank, self.message_catalog, self.colors_catalog, bank_catalog,
                                              self.midi_channels)
                    if base_model.bank_arrangement is not None:
                        if pos < len(base_model.bank_arrangement) and base_model.bank_arrangement[pos] is None:
                            raise IntuitiveException('bank_arrangement_mismatch',
                                                     'have bank but no bank arrangement')
                        if (pos < len(base_model.bank_arrangement) and
                                base_model.bank_arrangement[pos].name != self.banks[pos].name):
                            raise IntuitiveException('bank_order', 'bank and arrangement do not agree on order')
                elif (base_model.bank_arrangement is not None and pos < len(base_model.bank_arrangement) and
                      base_model.bank_arrangement[pos] is not None):
                    raise IntuitiveException('bank_arrangement_mismatch', 'have bank arrangement but no bank')
            jg.prune_list(self.banks)
            self.colors = self.colors_catalog.to_list()
            self.messages = self.message_catalog.to_list()
        elif base_model.bank_arrangement is not None:
            raise IntuitiveException('banks_missing', 'bank arrangement present but banks missing')
        if len(self.midi_channels) == 0:
            self.midi_channels = None
        if base_model.midi_channel is not None:
            self.midi_channel = base_model.midi_channel + 1

    # Do the MIDI channel names first
    # Gather the messages into a dictionary
    # Convert the banks using that dictionary
    def to_base(self, navigator_override=None):
        config = MC6Pro_grammar.MC6Pro()

        # Create the channel list, mapping names to indices
        channels_list = []
        if self.midi_channels is not None:
            config_channels = [None] * 16
            for pos, channel in enumerate(self.midi_channels):
                if channel is not None:
                    channels_list.append(channel.name)
                    config_channels[pos] = channel.to_base()
                else:
                    channels_list.append(None)
            config.midi_channels_from_list(config_channels)

        # Create the MIDI dictionary, mapping MIDI message names to the message objects
        # And the colors dictionary, mapping names to color schemas
        self.message_catalog = MessageCatalog(self.messages)
        self.colors_catalog = ColorsCatalog(self.colors)

        # If navigator is set, create the roadmap
        if self.navigator and self.navigator != 'None':
            if navigator_override is not None:
                self.navigator = navigator_override
            navigator = Navigator(self.navigator, self.banks, self.colors_catalog, self.message_catalog)
            navigator.build()

        # now add on startup messages
        if self.on_startup:
            if self.banks is None:
                raise IntuitiveException('no_banks', "Must have at least one bank to use on_startup messages.")
            if self.banks[0].messages is None:
                self.banks[0].messages = []
            for startup_message in self.on_startup:
                self.banks[0].messages.append(IntuitiveBankMessage.make_on_startup(startup_message))

        # Convert the model to a base model
        if self.banks is not None:
            bank_catalog = {}
            for pos, bank in enumerate(self.banks):
                if bank is not None:
                    bank_catalog[bank.name] = pos
            for pos, bank in enumerate(self.banks):
                if bank is not None:
                    base_bank = bank.to_base(self.message_catalog, self.colors_catalog, bank_catalog, channels_list)
                    config.set_bank(base_bank, pos)
                    bank_arrangement = MC6Pro_grammar.BankArrangementItem()
                    bank_arrangement.name = bank.name
                    config.set_bank_arrangement(bank_arrangement, pos)
        if self.midi_channel is not None:
            config.midi_channel = self.midi_channel - 1
        return config


colors_schema = \
    jg.Dict(
        'colors',
        [jg.Dict.make_key('name', jg.Atom('Name', str, var='name')),
         jg.Dict.make_key('bank_color', jg.Enum('Bank Color', preset_colors, None, var='bank_color')),
         jg.Dict.make_key('bank_background_color',
                          jg.Enum('Bank Background Color', preset_colors, None, var='bank_background_color')),
         jg.Dict.make_key('preset_color',
                          jg.Enum('Preset Color', preset_colors, None, var='preset_color')),
         jg.Dict.make_key('preset_background_color',
                          jg.Enum('Preset Background Color', preset_colors, None, var='preset_background_color')),
         jg.Dict.make_key('preset_toggle_color',
                          jg.Enum('Preset Toggle Color', preset_colors, None, var='preset_toggle_color')),
         jg.Dict.make_key('preset_toggle_background_color',
                          jg.Enum('Preset Toggle Background Color', preset_colors, None,
                                  var='preset_toggle_background_color')),
         jg.Dict.make_key('preset_shifted_color',
                          jg.Enum('Preset Shifted Color', preset_colors, None, var='preset_shifted_color'))],
        model=ColorSchema)

# MIDI channel grammar, just a name
midi_channel_schema = \
    jg.Dict(
        'midi_channel',
        [jg.Dict.make_key('name', jg.Atom('Name', str, '', var='name'))],
        model=intuitive_midi_channel.IntuitiveMidiChannel)

# MIDI message: This is misnamed, should be controller message?
# It is MIDI messages (PC and CC with one or two values)
# Or controller messages (Jump Bank or Toggle Page with page and bank values)
message_switch_key = jg.SwitchDict.make_key('type',
                                            jg.Enum('Type', im.intuitive_message_type,
                                                    im.intuitive_message_default, var='type'))
message_common_keys = [jg.SwitchDict.make_key('name', jg.Atom('Name', str, '', var='name'))]
message_case_keys = {
    'PC': [im.PCModel,
           jg.SwitchDict.make_key('number', jg.Atom('Number', int, var='number')),
           jg.SwitchDict.make_key('channel', jg.Atom('Channel', str, '', var='channel'))],
    'CC': [im.CCModel,
           jg.SwitchDict.make_key('number', jg.Atom('Number', int, var='number')),
           jg.SwitchDict.make_key('value', jg.Atom('Value', int, var='value')),
           jg.SwitchDict.make_key('channel', jg.Atom('Channel', str, '', var='channel'))],
    'PC Multichannel': [im.PCMultichannelModel,
                        jg.SwitchDict.make_key('multichannel',
                                               jg.List('Multichannel', 0, jg.Atom('Channel', str),
                                                       var='channels')),
                        jg.SwitchDict.make_key('number', jg.Atom('Number', int, var='number'))],
    'Bank Up': [],
    'Bank Down': [],
    'Bank Jump': [im.BankJumpModel,
                  jg.SwitchDict.make_key('bank', jg.Atom('Bank', str, var='bank')),
                  jg.SwitchDict.make_key('page', jg.Atom('Page', int, default=0, var='page'))],
    'Page Jump': [im.PageJumpModel,
                  jg.SwitchDict.make_key('page', jg.Atom('Page', int, var='page'))],
    'Toggle Page': [im.TogglePageModel,
                    jg.SwitchDict.make_key('page_up', jg.Atom('Page Up', bool, var='page_up'))],
    'Note On': [im.NoteOnModel] +  im.NoteOnModel.get_keys(),
    'Note Off': [im.NoteOffModel] + im.NoteOffModel.get_keys(),
    'Real Time': [im.RealTimeModel,
                  jg.SwitchDict.make_key('real_time',
                                         jg.Enum('Real Time', im.realtime_message_type, im.realtime_message_default,
                                                 var='real_time_type'))],
    'Preset Rename': [im.PresetRenameModel,
                      jg.SwitchDict.make_key('new_name', jg.Atom('New Name', str, var='new_name'))],
    'Song Position': [im.SongPositionModel,
                      jg.SwitchDict.make_key('song_position',
                                             jg.Atom('Song Position', int, var='song_position'))],
    'MIDI MMC': [im.MIDIMMCModel,
                 jg.SwitchDict.make_key('MMC Type',
                                        jg.Enum('MMC Type', im.midi_mmc_type, im.midi_mmc_default,
                                                var='midi_mmc_type'))],
    'MIDI Clock': [im.MIDIClockModel,
                   jg.SwitchDict.make_key('stop_clock',
                                          jg.Atom('Stop MIDI Clock', bool, var='stop_clock')),
                   jg.SwitchDict.make_key('bpm', jg.Atom('BPM', int, 0, var='bpm')),
                   jg.SwitchDict.make_key('bpm_decimal',
                                          jg.Enum('BPM Decimal', im.bpm_decimal, im.bpm_decimal_default,
                                                  var='bpm_decimal'))],
    'MIDI Clock Tap Menu': [im.MIDIClockTapMenuModel,
                            jg.SwitchDict.make_key('use_current_bpm',
                                                   jg.Atom('Use Current BPM', bool, var='use_current_bpm')),
                            jg.SwitchDict.make_key('bpm', jg.Atom('BPM', int, 0, var='bpm')),
                            jg.SwitchDict.make_key('bpm_decimal',
                                                   jg.Enum('BPM Decimal', im.bpm_decimal, im.bpm_decimal_default,
                                                           var='bpm_decimal'))],
    'MIDI Clock Tap': [],
    'Delay': [im.DelayModel,
              jg.SwitchDict.make_key('delay', jg.Atom('Delay', int, var='delay'))],
    'Relay Switching': [im.RelaySwitchingModel,
                        jg.SwitchDict.make_key('relay',
                                               jg.Enum('Relay', im.relay_type, im.relay_default, var='relay')),
                        jg.SwitchDict.make_key('tip_action',
                                               jg.Enum('Tip Action', im.tip_ring_action_type,
                                                       im.tip_ring_action_default, var='tip_action')),
                        jg.SwitchDict.make_key('ring_action',
                                               jg.Enum('Ring Action', im.tip_ring_action_type,
                                                       im.tip_ring_action_default, var='ring_action'))],
    'Set MIDI Thru': [im.MIDIThruModel,
                      jg.SwitchDict.make_key('value',
                                             jg.Enum('Set MIDI Thru', im.onoff_type, im.onoff_default, var='value'))],
    'Preset Scroll Message Count': [im.PresetScrollMessageCountModel,
                                    jg.SwitchDict.make_key('message_count',
                                                           jg.Atom('Message Count', int, var='message_count'))],
    'PC Number Scroll': [im.PCNumberScrollModel] + im.PCNumberScrollModel.get_keys(),
    'CC Value Scroll': [im.CCValueScrollModel] + im.CCValueScrollModel.get_keys(),
    'PC Number Scroll Update': [im.PCNumberScrollUpdateModel] + im.PCNumberScrollUpdateModel.get_keys(),
    'CC Value Scroll Update': [im.PCNumberScrollUpdateModel] + im.CCValueScrollUpdateModel.get_keys(),
    'Bank Change Mode': [],
    'Stop CC Waveform Generator': [im.StopWaveformModel] + im.StopWaveformModel.get_keys(),
    'Stop CC Sequence Generator': [im.StopSequenceModel] + im.StopSequenceModel.get_keys(),
    'Stop All CC Waveform Generator': [im.StopAllWaveformModel],
    'Stop All CC Sequence Generator': [im.StopAllSequenceModel],
    'Start CC Waveform Generator': [im.StartWaveformModel] + im.StartWaveformModel.get_keys(),
    'Start CC Sequence Generator': [im.StartSequenceModel] + im.StartSequenceModel.get_keys(),
    'Start CC Waveform Generator No MIDI Clock':
        [im.StartWaveformNoMIDIClockModel] + im.StartWaveformNoMIDIClockModel.get_keys(),
    'Start CC Sequence Generator No MIDI Clock':
        [im.StartSequenceNoMIDIClockModel] + im.StartSequenceNoMIDIClockModel.get_keys(),
    'Engage Preset': [im.EngagePresetModel,
                      jg.SwitchDict.make_key('bank', jg.Atom('Bank', str, var='bank')),
                      jg.SwitchDict.make_key('preset', jg.Atom('Preset', str, var='preset')),
                      jg.SwitchDict.make_key('Action',
                                             jg.Enum('Action', engage_preset_action, engage_preset_action_default,
                                                     var='action'))],
    'Toggle Preset': [],
    'Set Toggle': [im.SetToggleModel,
                   jg.SwitchDict.make_key('position',
                                          jg.Enum('Position', im.set_toggle_type, im.set_toggle_default,
                                                  var='position')),
                   jg.SwitchDict.make_key('presets',
                                          jg.List('Presets', 24, jg.Atom('Preset', str), var='presets'))],
    'Trigger Messages': [im.TriggerMessagesModel,
                         jg.SwitchDict.make_key('preset', jg.Atom('Preset', str, var='preset')),
                         jg.SwitchDict.make_key('messages',
                                                jg.List('Messages', 32, jg.Atom('Message', str),
                                                        var='messages'))],
    'Select Exp Message': [im.SelectExpMessageModel,
                           jg.SwitchDict.make_key('input', jg.Atom('Input', int, 1, var='input')),
                           jg.SwitchDict.make_key('messages',
                                                  jg.List('Messages', 32, jg.Atom('Message', str),
                                                          var='messages'))],
    'Looper Mode': [im.LooperModeModel,
                    jg.SwitchDict.make_key('Mode', jg.Enum('Mode', im.looper_mode, im.looper_mode_default, var='mode')),
                    jg.SwitchDict.make_key('Selected Switches', jg.Atom('Selected Switches', bool, False,
                                                                        var='selected_switches')),
                    jg.SwitchDict.make_key('switches',
                                           jg.List('Switches', 6, jg.Atom('Switch', str), var='switches')),
                    jg.SwitchDict.make_key('disable_message',
                                           jg.Atom('Disable Message', bool, False, var='disable_message'))],
    'Disengage Looper Mode': [im.DisengageLooperModeModel,
                              jg.SwitchDict.make_key('disable_message',
                                                     jg.Atom('Disable Message', bool, False,
                                                             var='disable_message'))],
    'SysEx': [im.SysExModel,
              jg.SwitchDict.make_key('data',
                                     jg.List('Data', 18, jg.Atom('Data Element', int), var='data'))]
}
message_schema = jg.SwitchDict('message_schema', message_switch_key,
                               message_case_keys, message_common_keys,
                               model=im.IntuitiveMessage, model_var='specific_message')

# The Preset Message is a preset message, includes trigger and toggle state as well as the included MIDI message
preset_message_schema = \
    jg.Dict('preset_message',
            [jg.Dict.make_key('trigger',
                              jg.Enum('Trigger', preset_message_trigger, preset_message_trigger_default,
                                      var='trigger')),
             jg.Dict.make_key('toggle',
                              jg.Enum('Toggle', preset_toggle_state, preset_toggle_state_default, var='toggle')),
             jg.Dict.make_key('midi_message', jg.Atom('MIDI Message', str, var='midi_message'))],
            model=IntuitivePresetMessage)

# All the information associated with a preset
preset_schema = \
    jg.Dict('preset',
            [jg.Dict.make_key('short_name',
                              jg.Atom('Short Name', str, 'EMPTY', var='short_name')),
             jg.Dict.make_key('long_name',
                              jg.Atom('Long Name', str, '', var='long_name')),
             jg.Dict.make_key('toggle_name',
                              jg.Atom('Toggle Name', str, '', var='toggle_name')),
             jg.Dict.make_key('toggle_mode',
                              jg.Atom('Toggle Mode', bool, False, var='toggle_mode')),
             jg.Dict.make_key('toggle_group',
                              jg.Atom('Toggle Group', int, 0, var='toggle_group')),
             jg.Dict.make_key('message_scroll',
                              jg.Enum('Message Scroll', im.onoff_type, im.onoff_default, var='message_scroll')),
             jg.Dict.make_key('colors',
                              jg.Atom('Colors', str, '', var='colors')),
             jg.Dict.make_key('strip_color',
                              jg.Enum('Strip Color', preset_colors, preset_empty_color, var='strip_color')),
             jg.Dict.make_key('strip_toggle_color',
                              jg.Enum('Strip Toggle Color', preset_colors, preset_empty_color,
                                      var='strip_toggle_color')),
             jg.Dict.make_key('messages',
                              jg.List('Message List', 32, preset_message_schema, var='messages'))],
            model=IntuitivePreset)

# The Bank Message is a bank message, includes only trigger state (no toggle) as well as the included MIDI message
bank_message_schema = \
    jg.Dict('bank_message',
            [jg.Dict.make_key('trigger',
                              jg.Enum('Trigger', bank_message_trigger, bank_message_trigger_default, var='trigger')),
             jg.Dict.make_key('midi_message', jg.Atom('MIDI Message', str, var='midi_message'))],
            model=IntuitiveBankMessage)

# All the information associated with a bank
bank_schema = \
    jg.Dict('bank',
            [jg.Dict.make_key('name', jg.Atom('Name', str, '', var='name')),
             jg.Dict.make_key('description', jg.Atom('Description', str, '', var='description')),
             jg.Dict.make_key('colors', jg.Atom('Colors', str, '', var='colors')),
             jg.Dict.make_key('clear_toggle',
                              jg.Atom('Clear Toggle', bool, False, var='clear_toggle')),
             jg.Dict.make_key('display_description',
                              jg.Atom('Display Description', bool, False, var='display_description')),
             jg.Dict.make_key('messages',
                              jg.List('Message List', 32, bank_message_schema, var='messages')),
             jg.Dict.make_key('presets', jg.List('Preset List', 0, preset_schema, var='presets')),
             jg.Dict.make_key('exp_presets', jg.List('Exp Preset List', 0, preset_schema, var='exp_presets'))],
            model=IntuitiveBank)


def version_verify(elem, _ctxt, _lp):
    # This should only happen when genning an MC6Pro base file, no version specified
    if elem is None:
        return intuitive_version
    desired_version = semver.Version.parse(intuitive_version)
    have_version = semver.Version.parse(elem)
    if have_version.is_compatible(desired_version):
        return elem
    raise jg.JsonGrammarException('bad_version', "Intuitive config file version is wrong. Currently on " +
                                  intuitive_version + " but got " + elem)


# The whole schema
mc6pro_intuitive_schema = \
    jg.Dict('mc6pro_intuitive',
            [jg.Dict.make_key('midi_channels',
                              jg.List('MIDI Channel List', 16, midi_channel_schema, var='midi_channels')),
             jg.Dict.make_key('messages', jg.List('Message List', 0, message_schema, var='messages')),
             jg.Dict.make_key('banks', jg.List('Bank List', 128, bank_schema, var='banks')),
             jg.Dict.make_key('midi_channel', jg.Atom('MIDI Channel', int, 1, var='midi_channel')),
             jg.Dict.make_key('colors', jg.List('Color List', 0, colors_schema, var='colors')),
             jg.Dict.make_key('navigator', jg.Enum('Navigator', navigator_mode, "None", var='navigator')),
             jg.Dict.make_key('on_startup',
                              jg.List('On Startup List', 0, jg.Atom('Message', str), var='on_startup')),
             jg.Dict.make_key('version',
                              jg.Atom('Version', str, value=version_verify, var='version'), required=True)],
            model=MC6ProIntuitive)

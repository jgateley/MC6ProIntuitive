import copy

import MC6Pro_grammar
import semver
import json_grammar as jg

# This is the intuitive grammar, it is a minimal grammar
# It also includes to_base and from_base methods, these convert intuitive models to base models
#
# The main features:
# It is minimal, you only include what is significant, making it easier to edit the config file
# It is not deeply nested, again for ease of editing
# MIDI messages are named and are at the top level
# Naming makes them more intuitive
# At the top level: they are easily resused

intuitive_version = '0.1.0'

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

midi_message_type = ["unused", "PC", "CC", "message3", "message4", "message5", "message6",
                     "message7", "message8", "message9", "message10", "message11",
                     "message12", "Bank Jump", "Toggle Page", "Page Jump"]
midi_message_default = midi_message_type[0]

preset_message_trigger = ["No Action", "Press", "Release", "Long Press", "Long Press Scroll", "Long Press Release",
                          "Release All", "Double Tap", "Double Tap Release", "Long Double Tap",
                          "Long Double Tap Release", "On First Engage", "On First Engage (send only this)",
                          "On Disengage"]
preset_message_trigger_default = preset_message_trigger[1]

bank_message_trigger = ["unused", "On Enter Bank", "On Exit Bank", "On Enter Bank - Execute Once Only",
                        "On Exit Bank - Execute Once Only", "On Enter Bank - Page 1", "On Enter Bank - Page 2",
                        "On Toggle Page - Page 1", "On Toggle Page - Page 2"]
bank_message_trigger_default = bank_message_trigger[1]


class IntuitiveException(Exception):
    """used for exceptions raised during Intuitive operations"""
    pass


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
        return self.catalog[name]

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

    def add_preset_schema(self, bank_color_schema, name_color, name_toggle_color, background_color,
                          background_toggle_color):
        name_color = ColorSchema.from_base_preset_color(name_color, False)
        name_toggle_color = ColorSchema.from_base_preset_color(name_toggle_color, False)
        background_color = ColorSchema.from_base_preset_color(background_color, True)
        background_toggle_color = ColorSchema.from_base_preset_color(background_toggle_color, True)
        schema = ColorSchema.make_preset_schema(bank_color_schema.bank_color, bank_color_schema.bank_background_color,
                                                name_color, name_toggle_color,
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
    def make_preset_schema(bank_color, bank_background_color, preset_color, toggle_color, preset_background_color,
                           toggle_background_color, name=None):
        schema = ColorSchema()
        if name is not None:
            schema.name = name
        schema.bank_color = bank_color
        schema.bank_background_color = bank_background_color
        schema.preset_color = preset_color
        schema.preset_background_color = preset_background_color
        schema.preset_toggle_color = toggle_color
        schema.preset_toggle_background_color = toggle_background_color
        return schema

    def __init__(self):
        super().__init__()
        self.name = None
        self.bank_color = None
        self.bank_background_color = None
        self.preset_color = None
        self.preset_background_color = None
        self.preset_toggle_color = None
        self.preset_toggle_background_color = None

    def __eq__(self, other):
        result = isinstance(other, ColorSchema)
        result = result and self.name == other.name
        result = result and self.bank_color == other.bank_color
        result = result and self.bank_background_color == other.bank_background_color
        result = result and self.preset_color == other.preset_color
        result = result and self.preset_background_color == other.preset_background_color
        result = result and self.preset_toggle_color == other.preset_toggle_color
        result = result and self.preset_toggle_background_color == other.preset_toggle_background_color
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


# MIDI and controller messages are their own top level category, and are named
# This class is messages, including MIDI messages
# But also including other messages such as those which control the MC6Pro
# They can be referenced in banks etc.
#
class IntuitiveMessage(jg.JsonGrammarModel):

    @staticmethod
    def make_bank_jump_message(name, bank, page, message_catalog):
        result = IntuitiveMessage()
        result.name = name
        result.type = 'Bank Jump'
        result.bank = bank
        result.page = page
        if message_catalog is not None:
            return message_catalog.add(result)
        return result

    @staticmethod
    def make_toggle_page_message(name, page_up, message_catalog):
        result = IntuitiveMessage()
        result.name = name
        result.type = 'Toggle Page'
        result.page_up = page_up
        return message_catalog.add(result)

    def __init__(self):
        super().__init__()
        self.name = None
        self.channel = None
        self.type = None
        self.number = None
        self.value = None
        self.bank = None
        self.page = None
        self.page_up = None

    def __eq__(self, other):
        result = isinstance(other, IntuitiveMessage) and self.type == other.type
        if self.type == 'PC' or self.type == 'CC':
            result = result and self.channel == other.channel and self.number == other.number
        if self.type == 'CC':
            result = result and self.value == other.value
        if self.type == "Bank Jump":
            result = result and self.bank == other.bank
        if self.type == "Bank Jump" or self.type == "Page Jump":
            result = result and self.page == other.page
        if self.type == "Toggle Page":
            result = result and self.page_up == other.page_up
        if not result:
            self.modified = True
        return result

    # From/To Base info
    # For Bank Jump in the base:
    #  data[0] is the bank number, base 0
    #  data[1] should be 0, it is 127 for last used
    #  data[2] is the page number (6 = 1, 7 = 2, 14 = 3, 15 = 4)
    # For Toggle Page in the base
    #  data[0] is the page number (1 = up, 2 = down, 3 = 1, 4 = 2, 5 = 3, 6 = 4
    # PC takes a number
    # CC takes a number and a value

    # This creates a name out of the MIDI message parameters
    def from_base(self, base_message, message_catalog, banks, midi_channels):

        if base_message.type is not None:
            self.type = midi_message_type[base_message.type]
        else:
            raise IntuitiveException('unimplemented', 'Fix me')

        self.name = self.type + ':'
        if self.type in ['PC', 'CC']:
            base_channel = base_message.channel
            if base_channel is None:
                base_channel = 1
            base_channel -= 1
            self.channel = midi_channels[base_channel].name
            self.name += self.channel + ':'

            if self.type == "PC":
                if base_message.msg_array_data is None:
                    self.number = 0
                else:
                    self.number = base_message.msg_array_data[0]
                    if self.number is None:
                        self.number = 0
                self.name += str(self.number)
            elif self.type == 'CC':
                if base_message.msg_array_data is None:
                    self.number = 0
                    self.value = 0
                else:
                    self.number = base_message.msg_array_data[0]
                    if self.number is None:
                        self.number = 0
                    self.value = base_message.msg_array_data[1]
                    if self.value is None:
                        self.value = 0
                self.name += str(self.number) + ':' + str(self.value)
        elif self.type == 'Bank Jump':
            bank_number = 0
            if base_message.msg_array_data[0] is not None:
                bank_number = base_message.msg_array_data[0]
            self.bank = banks[bank_number]
            if base_message.msg_array_data[2] == 6:
                self.page = 0
            elif base_message.msg_array_data[2] == 7:
                self.page = 1
            elif base_message.msg_array_data[2] == 14:
                self.page = 2
            elif base_message.msg_array_data[2] == 15:
                self.page = 3
            else:
                raise IntuitiveException('missing case', 'missing case')
            self.name += self.bank + ':' + str(self.page)
            if base_message.msg_array_data[1] is not None:
                raise IntuitiveException('bad_message', 'data array is nonzero')
        elif self.type == 'Toggle Page':
            if base_message.msg_array_data[0] == 1 or base_message.msg_array_data[0] == 2:
                self.page_up = base_message.msg_array_data[0] == 1
                if self.page_up:
                    self.name += " Up"
                else:
                    self.name += " Down"
            else:
                self.type = "Page Jump"
                self.name = self.type + ':'
                self.page = base_message.msg_array_data[0] - 3
                self.name += str(self.page)
        else:
            raise IntuitiveException('unrecognized', 'Invalid message type')

        return message_catalog.add(self)

    # Add the MIDI message directly to the base message
    def to_base(self, base_message, bank_catalog, midi_channels):
        base_message.type = midi_message_type.index(self.type)
        base_message.msg_array_data = [None] * 18

        if self.type in ["PC", "CC"]:
            base_message.channel = midi_channels.index(self.channel)
            base_message.channel += 1
            if base_message.channel == 1:
                base_message.channel = None

            base_message.msg_array_data[0] = self.number
            if base_message.msg_array_data[0] == 0:
                base_message.msg_array_data[0] = None

            if self.type == "CC":
                base_message.msg_array_data[1] = self.value
                if base_message.msg_array_data[1] == 0:
                    base_message.msg_array_data[1] = None
        elif self.type == 'Bank Jump':
            base_message.msg_array_data[0] = bank_catalog[self.bank]
            if base_message.msg_array_data[0] == 0:
                base_message.msg_array_data[0] = None
            if self.page == 0:
                base_message.msg_array_data[2] = 6
            elif self.page == 1:
                base_message.msg_array_data[2] = 7
            elif self.page == 2:
                base_message.msg_array_data[2] = 14
            elif self.page == 3:
                base_message.msg_array_data[2] = 15
            else:
                raise IntuitiveException('invalid_page_number', "Invalid page number in bank jump")
        elif self.type == "Toggle Page":
            if self.page_up:
                base_message.msg_array_data[0] = 1
            else:
                base_message.msg_array_data[0] = 2
        elif self.type == 'Page Jump':
            base_message.type = midi_message_type.index('Toggle Page')
            base_message.msg_array_data[0] = self.page + 3
        else:
            raise IntuitiveException('unknown_messagetype', "Unknown message type")

        empty = True
        for elem in base_message.msg_array_data:
            if elem is not None:
                empty = False
                break
        if empty:
            base_message.msg_array_data = None


# This is the preset component of a MIDI message
# The trigger, and the toggle state
class IntuitivePresetMessage(jg.JsonGrammarModel):

    @staticmethod
    def make(message_name):
        result = IntuitivePresetMessage()
        result.midi_message = message_name
        result.trigger = "Press"
        return result

    def __init__(self):
        super().__init__()
        self.trigger = None
        self.toggle = None
        self.midi_message = None

    def __eq__(self, other):
        result = (isinstance(other, IntuitivePresetMessage) and self.trigger == other.trigger and
                  self.toggle == other.toggle)
        if not result:
            self.modified = True
        return result

    def from_base(self, base_message, message_catalog, bank_catalog, midi_channels):
        if base_message.trigger is not None:
            if base_message.trigger == 1:
                self.trigger = None
            else:
                self.trigger = preset_message_trigger[base_message.trigger]
        else:
            self.trigger = preset_message_trigger[0]
        if base_message.toggle_group is not None:
            self.toggle = preset_toggle_state[base_message.toggle_group]
        midi_message = IntuitiveMessage()
        self.midi_message = midi_message.from_base(base_message, message_catalog, bank_catalog, midi_channels)

    # Pull the MIDI message out of the dictionary, then convert it to the base model
    def to_base(self, message_catalog, bank_catalog, midi_channels):
        base_message = MC6Pro_grammar.MidiMessage()
        if self.trigger is not None:
            base_message.trigger = preset_message_trigger.index(self.trigger)
        else:
            base_message.trigger = preset_message_trigger.index("Press")
        if self.toggle is not None:
            base_message.toggle_group = preset_toggle_state.index(self.toggle)
        if self.midi_message is not None:
            midi_message = message_catalog.lookup(self.midi_message)
            midi_message.to_base(base_message, bank_catalog, midi_channels)
        return base_message


# This is the bank component of a MIDI message
# Only has a trigger, not a toggle
class IntuitiveBankMessage(jg.JsonGrammarModel):

    def __init__(self):
        super().__init__()
        self.trigger = None
        self.midi_message = None

    def __eq__(self, other):
        result = isinstance(other, IntuitiveBankMessage) and self.trigger == other.trigger
        if not result:
            self.modified = True
        return result

    def from_base(self, base_message, message_catalog, bank_catalog, midi_channels):
        if base_message.trigger is not None:
            if base_message.trigger == 1:
                self.trigger = None
            else:
                self.trigger = bank_message_trigger[base_message.trigger]
        else:
            self.trigger = bank_message_trigger[0]
        midi_message = IntuitiveMessage()
        self.midi_message = midi_message.from_base(base_message, message_catalog, bank_catalog, midi_channels)

    # Pull the MIDI message out of the dictionary, then convert it to the base model
    def to_base(self, message_catalog, bank_catalog, midi_channels):
        base_message = MC6Pro_grammar.MidiMessage()
        if self.trigger is not None:
            base_message.trigger = bank_message_trigger.index(self.trigger)
        else:
            base_message.trigger = bank_message_trigger.index(bank_message_trigger_default)
        if self.midi_message is not None:
            midi_message = message_catalog.lookup(self.midi_message)
            midi_message.to_base(base_message, bank_catalog, midi_channels)
        return base_message


class IntuitivePreset(jg.JsonGrammarModel):
    @staticmethod
    def make(short_name, messages, colors):
        result = IntuitivePreset()
        result.short_name = short_name
        result.messages = messages
        if colors is None or isinstance(colors, str):
            result.colors = colors
        else:
            result.colors = colors.name
        return result

    def __init__(self):
        super().__init__()
        self.short_name = None
        self.long_name = None
        self.toggle_name = None
        self.colors = None
        self.strip_color = None
        self.strip_toggle_color = None
        self.toggle_mode = None
        self.messages = None

    def __eq__(self, other):
        result = (isinstance(other, IntuitivePreset) and self.short_name == other.short_name and
                  self.long_name == other.long_name and self.toggle_name == other.toggle_name and
                  self.colors == other.colors and
                  self.strip_color == other.strip_color and self.strip_toggle_color == other.strip_toggle_color and
                  self.toggle_mode == other.toggle_mode and self.messages == other.messages)
        if not result:
            self.modified = True
        return result

    def from_base(self, base_preset, message_catalog, colors_catalog, bank_color_schema, bank_catalog, midi_channels):
        if base_preset.short_name is None:
            raise IntuitiveException("unimplemented", "preset short name is None")
        self.short_name = base_preset.short_name
        self.long_name = base_preset.long_name
        self.toggle_name = base_preset.toggle_name
        self.colors = colors_catalog.add_preset_schema(bank_color_schema,
                                                       base_preset.name_color, base_preset.name_toggle_color,
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
                    self.messages[pos].from_base(base_message, message_catalog, bank_catalog, midi_channels)
            jg.prune_list(self.messages)

    def to_base(self, message_catalog, colors_catalog, bank_colors_schema, bank_catalog, midi_channels):
        base_preset = MC6Pro_grammar.Preset()
        base_preset.short_name = self.short_name
        base_preset.long_name = self.long_name
        base_preset.toggle_name = self.toggle_name
        if self.colors is None:
            preset_colors_schema = bank_colors_schema
        else:
            preset_colors_schema = colors_catalog.lookup(self.colors)
        base_preset.name_color = preset_colors_schema.to_base_preset_color(preset_colors_schema.preset_color, False)
        base_preset.name_toggle_color = (
            preset_colors_schema.to_base_preset_color(preset_colors_schema.preset_toggle_color, False))
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
                    base_message = message.to_base(message_catalog, bank_catalog, midi_channels)
                    base_preset.set_message(base_message, pos)
        return base_preset


class IntuitiveBank(jg.JsonGrammarModel):
    def __init__(self):
        super().__init__()
        self.name = None
        self.description = None
        self.colors = None
        self.display_description = None
        self.clear_toggle = None
        self.messages = None
        self.presets = None

    def __eq__(self, other):
        result = (isinstance(other, IntuitiveBank) and self.name == other.name and
                  self.description == other.description and
                  self.colors == other.colors and
                  self.display_description == other.display_description and
                  self.clear_toggle == other.clear_toggle and
                  self.messages == other.messages and
                  self.presets == other.presets)
        if not result:
            self.modified = True
        return result

    @staticmethod
    def build_roadmap_bank(bank_number, colors):
        result = IntuitiveBank()
        result.name = "Home"
        if bank_number > 0:
            result.name += " (" + str(bank_number + 1) + ")"
        result.description = "Navigation Home"
        result.presets = []
        if colors is None or isinstance(colors, str):
            result.colors = colors
        else:
            result.colors = colors.name
        return result

    @staticmethod
    def build_overflow_bank(name, description, overflow_number):
        result = IntuitiveBank()
        result.name = name + " (" + str(overflow_number + 1) + ")"
        result.description = description
        return result

    def from_base(self, base_bank, message_catalog, colors_catalog, bank_catalog, midi_channels):
        if base_bank.short_name is not None:
            raise IntuitiveException('unimplemented', 'bank short_name')
        if base_bank.name is None:
            raise IntuitiveException('missing_bank_name', 'bank has no name')
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
                    self.messages[pos].from_base(base_message, message_catalog, bank_catalog, midi_channels)
            jg.prune_list(self.messages)
        if base_bank.presets is not None:
            self.presets = [None] * 24
            for pos, base_preset in enumerate(base_bank.presets):
                if base_preset is not None:
                    self.presets[pos] = IntuitivePreset()
                    self.presets[pos].from_base(base_preset, message_catalog, colors_catalog, color_schema,
                                                bank_catalog, midi_channels)
            jg.prune_list(self.presets)
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
        if self.presets is not None:
            for pos, preset in enumerate(self.presets):
                if preset is not None:
                    base_preset = preset.to_base(message_catalog, colors_catalog, bank_colors_schema, bank_catalog,
                                                 midi_channels)
                    base_bank.set_preset(base_preset, pos)
        return base_bank

    def add_navigator_home_preset(self, return_to_home_preset, blank_preset):
        if self.presets is None:
            self.presets = []
        while len(self.presets) < 2:
            self.presets.append(blank_preset)
        self.presets.insert(2, return_to_home_preset)

    def add_paging_preset_pair(self, pos, next_page_preset, prev_page_preset):
        self.presets.insert(pos, next_page_preset)
        while len(self.presets) < pos + 3:
            self.presets.append(self.blank_preset)
        self.presets.insert(pos + 3, prev_page_preset)

    def add_paging_presets(self, next_page_preset, prev_page_preset, bank_number, banks, message_catalog,
                           navigators_colors_schema):
        if len(self.presets) <= 6:
            return []
        self.add_paging_preset_pair(5, next_page_preset, prev_page_preset)
        if len(self.presets) <= 12:
            return []
        self.add_paging_preset_pair(11, next_page_preset, prev_page_preset)
        if len(self.presets) <= 18:
            return []
        self.add_paging_preset_pair(17, next_page_preset, prev_page_preset)
        if len(self.presets) <= 24:
            return []
        # Need a jump to next bank, page 0 and prior bank, page 3
        next_page_message = IntuitiveMessage.make_bank_jump_message('next_bank_' + str(bank_number+1),
                                                                    banks[bank_number+1].name, 0, message_catalog)
        next_page_preset = IntuitivePreset.make('Next',
                                                [IntuitivePresetMessage.make(next_page_message)],
                                                navigators_colors_schema)
        prev_page_message = IntuitiveMessage.make_bank_jump_message('prev_bank_' + str(bank_number),
                                                                    banks[bank_number].name, 3, message_catalog)
        prev_page_preset = IntuitivePreset.make('Previous',
                                                [IntuitivePresetMessage.make(prev_page_message)],
                                                navigators_colors_schema)
        self.add_paging_preset_pair(23, next_page_preset, prev_page_preset)
        result = self.presets[24:]
        self.presets = self.presets[0:24]
        return result


class IntuitiveMidiChannel(jg.JsonGrammarModel):
    def __init__(self):
        super().__init__()
        self.name = None

    def __eq__(self, other):
        result = isinstance(other, IntuitiveMidiChannel) and self.name == other.name
        if not result:
            self.modified = True
        return result

    def from_base(self, base_midi_channel):
        self.name = base_midi_channel.name

    def to_base(self):
        base_midi_channel = MC6Pro_grammar.MidiChannel()
        base_midi_channel.name = self.name
        return base_midi_channel


class MC6ProIntuitive(jg.JsonGrammarModel):
    page_size = 6

    def __init__(self):
        super().__init__()
        self.midi_channels = None
        self.messages = None
        self.message_catalog = None
        self.colors = None
        self.colors_catalog = None
        self.banks = None
        self.midi_channel = None
        self.navigator = None
        self.version = None

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

    @staticmethod
    def number_overflow_pages(bank_presets):
        presets_len = 0
        if bank_presets is not None:
            presets_len = len(bank_presets)
        result = (presets_len + (MC6ProIntuitive.page_size - 4)) // (MC6ProIntuitive.page_size - 2)
        if result < 1:
            result = 1
        return result

    @staticmethod
    def number_pages(nmr_banks):
        result = (nmr_banks + (MC6ProIntuitive.page_size - 5)) // (MC6ProIntuitive.page_size - 2)
        if result == 0:
            result = 1
        return result

    @staticmethod
    def number_banks(nmr_pages):
        return (nmr_pages + 3) // 4

    number_pages_per_bank = 16

    # Clean up the bank list (remove internal Nones)
    # Add in the roadmap banks at the beginning
    # Fill in the roadmap presets
    # Go through each roadmap bank:
    #   Add the home preset or prev page preset
    #   Add next page preset if needed
    # Go through each real bank and add the home preset, and page moving presets
    def build_roadmap(self):
        if 'navigator' in self.colors_catalog.catalog:
            navigator_colors_schema = self.colors_catalog.catalog['navigator']
        elif 'default' in self.colors_catalog.catalog:
            navigator_colors_schema = self.colors_catalog.catalog['default']
        else:
            navigator_colors_schema = ColorSchema()
        blank_preset = IntuitivePreset.make('', [], None)
        return_to_home_message = IntuitiveMessage.make_bank_jump_message('navigator_home', 'Home',
                                                                         0, self.message_catalog)
        return_to_home_preset = IntuitivePreset.make('Home',
                                                     [IntuitivePresetMessage.make(return_to_home_message)],
                                                     navigator_colors_schema)
        next_page_message = IntuitiveMessage.make_toggle_page_message('next_page', True, self.message_catalog)
        next_page_preset = IntuitivePreset.make('Next', [IntuitivePresetMessage.make(next_page_message)],
                                                navigator_colors_schema)
        prev_page_message = IntuitiveMessage.make_toggle_page_message('prev_page', False, self.message_catalog)
        prev_page_preset = IntuitivePreset.make('Previous', [IntuitivePresetMessage.make(prev_page_message)],
                                                navigator_colors_schema)

        # Clean up the bank list
        jg.compact_list(self.banks)
        number_non_navigation_banks = len(self.banks)

        # Compute the number of roadmap pages
        nmr_roadmap_pages = MC6ProIntuitive.number_pages(number_non_navigation_banks)
        nmr_roadmap_banks = MC6ProIntuitive.number_banks(nmr_roadmap_pages)

        # Create the roadmap banks
        for i in range(nmr_roadmap_banks):
            self.banks.insert(i, IntuitiveBank.build_roadmap_bank(i, navigator_colors_schema))

        # And add in the navigator presets
        for bank in self.banks[nmr_roadmap_banks:]:
            jump_to_bank_message = IntuitiveMessage.make_bank_jump_message('navigator ' + bank.name,
                                                                           bank.name, 0,
                                                                           self.message_catalog)
            jump_to_bank_preset = IntuitivePreset.make(bank.name, [IntuitivePresetMessage.make(jump_to_bank_message)],
                                                       navigator_colors_schema)
            self.banks[0].presets.append(jump_to_bank_preset)

        # Now add in the prev/next buttons
        remaining_presets = self.banks[0].add_paging_presets(next_page_preset, prev_page_preset, 0,
                                                             self.banks, self.message_catalog, navigator_colors_schema)
        for i in range(1, nmr_roadmap_banks):
            self.banks[i].presets = remaining_presets
            remaining_presets = self.banks[i].add_paging_presets(next_page_preset, prev_page_preset, i,
                                                                 self.banks, self.message_catalog,
                                                                 navigator_colors_schema)
        if remaining_presets:
            raise IntuitiveException('programmer_error', "extra presets")

        # Create the overflow banks
        i = nmr_roadmap_banks
        while i < len(self.banks):
            bank = self.banks[i]
            nmr_pages = self.number_overflow_pages(bank.presets)
            nmr_overflow_banks = (nmr_pages + 3) // 4 - 1
            for j in range(nmr_overflow_banks):
                self.banks.insert(i + 1 + j, IntuitiveBank.build_overflow_bank(bank.name, bank.description, j + 1))
            bank.add_navigator_home_preset(return_to_home_preset, blank_preset)
            remaining_presets = bank.add_paging_presets(next_page_preset, prev_page_preset,
                                                        i, self.banks, self.message_catalog, navigator_colors_schema)
            for j in range(nmr_overflow_banks):
                self.banks[i + 1 + j].presets = remaining_presets
                remaining_presets = self.banks[i + 1 + j].add_paging_presets(next_page_preset,
                                                                             prev_page_preset,
                                                                             i,
                                                                             self.banks,
                                                                             self.message_catalog,
                                                                             navigator_colors_schema)
            i += 1 + nmr_overflow_banks
            if remaining_presets:
                raise IntuitiveException('programmer_error', "extra presets")

    # Parse the MIDI channels (names) first, as these are needed for MIDI messages
    # Then process the banks, gathering messages as we go, and handling bank arrangement
    # Then add all the gathered messages
    def from_base(self, base_model):
        if base_model.midi_channels is not None:
            self.midi_channels = []
            pos = -1
            for pos in range(15, -1, -1):
                if base_model.midi_channels[pos] is not None:
                    break
            for pos2 in range(pos+1):
                if base_model.midi_channels[pos2] is not None:
                    self.midi_channels.append(IntuitiveMidiChannel())
                    self.midi_channels[pos2].from_base(base_model.midi_channels[pos2])
                else:
                    self.midi_channels.append(None)
        if base_model.banks is not None:
            if base_model.bank_arrangement is None:
                raise IntuitiveException('bank_arrangement_missing', "missing bank arrangement")
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
                    if pos < len(base_model.bank_arrangement) and base_model.bank_arrangement[pos] is None:
                        raise IntuitiveException('bank_arrangement_mismatch',
                                                 'have bank but no bank arrangement')
                    if (pos < len(base_model.bank_arrangement) and
                            base_model.bank_arrangement[pos].name != self.banks[pos].name):
                        raise IntuitiveException('bank_order', 'bank and arrangement do not agree on order')
                elif pos < len(base_model.bank_arrangement) and base_model.bank_arrangement[pos] is not None:
                    raise IntuitiveException('bank_arrangement_mismatch', 'have bank arrangement but no bank')
            jg.prune_list(self.banks)
            self.colors = self.colors_catalog.to_list()
            self.messages = self.message_catalog.to_list()
        elif base_model.bank_arrangement is not None:
            raise IntuitiveException('banks_missing', 'bank arrangement present but banks missing')
        if base_model.midi_channel is not None:
            self.midi_channel = base_model.midi_channel + 1

    # Do the MIDI channel names first
    # Gather the messages into a dictionary
    # Convert the banks using that dictionary
    def to_base(self):
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
        if self.navigator:
            self.build_roadmap()

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
        [jg.Dict.make_key('name', jg.Atom(str, var='name')),
         jg.Dict.make_key('bank_color', jg.Enum(preset_colors, None, var='bank_color')),
         jg.Dict.make_key('bank_background_color', jg.Enum(preset_colors, None, var='bank_background_color')),
         jg.Dict.make_key('preset_color', jg.Enum(preset_colors, None, var='preset_color')),
         jg.Dict.make_key('preset_background_color', jg.Enum(preset_colors, None, var='preset_background_color')),
         jg.Dict.make_key('preset_toggle_color', jg.Enum(preset_colors, None, var='preset_toggle_color')),
         jg.Dict.make_key('preset_toggle_background_color', jg.Enum(preset_colors, None,
                                                                    var='preset_toggle_background_color'))],
        model=ColorSchema)

# MIDI channel grammar, just a name
midi_channel_schema = \
    jg.Dict(
        'midi_channel',
        [jg.Dict.make_key('name', jg.Atom(str, '', var='name'))],
        model=IntuitiveMidiChannel)


# MIDI message: This is misnamed, should be controller message?
# It is MIDI messages (PC and CC with one or two values)
# Or controller messages (Jump Bank or Toggle Page with page and bank values)
message_switch_key = jg.SwitchDict.make_key('type', jg.Enum(midi_message_type, midi_message_default, var='type'))
message_common_keys = [jg.SwitchDict.make_key('name', jg.Atom(str, '', var='name')),
                       jg.SwitchDict.make_key('channel', jg.Atom(str, '', var='channel'))]
message_case_keys = {
    'PC': [jg.SwitchDict.make_key('number', jg.Atom(int, var='number'))],
    'CC': [jg.SwitchDict.make_key('number', jg.Atom(int, var='number')),
           jg.SwitchDict.make_key('value', jg.Atom(int, var='value'))],
    'Bank Jump': [jg.SwitchDict.make_key('bank', jg.Atom(str, var='bank')),
                  jg.SwitchDict.make_key('page', jg.Atom(int, var='page'))],
    'Page Jump': [jg.SwitchDict.make_key('page', jg.Atom(int, var='page'))],
    'Toggle Page': [jg.SwitchDict.make_key('page_up', jg.Atom(bool, var='page_up'))]
}
message_schema = jg.SwitchDict('message_schema', message_switch_key,
                               message_case_keys, message_common_keys,
                               model=IntuitiveMessage)

# The Preset Message is a preset message, includes trigger and toggle state as well as the included MIDI message
preset_message_schema = \
    jg.Dict('preset_message',
            [jg.Dict.make_key('trigger',
                              jg.Enum(preset_message_trigger, preset_message_trigger_default, var='trigger')),
             jg.Dict.make_key('toggle',
                              jg.Enum(preset_toggle_state, preset_toggle_state_default, var='toggle')),
             jg.Dict.make_key('midi_message', jg.Atom(str, var='midi_message'))],
            model=IntuitivePresetMessage)

# All the information associated with a preset
preset_schema = \
    jg.Dict('preset',
            [jg.Dict.make_key('short_name', jg.Atom(str, 'EMPTY', var='short_name')),
             jg.Dict.make_key('long_name', jg.Atom(str, '', var='long_name')),
             jg.Dict.make_key('toggle_name', jg.Atom(str, '', var='toggle_name')),
             jg.Dict.make_key('toggle_mode', jg.Atom(bool, False, var='toggle_mode')),
             jg.Dict.make_key('colors', jg.Atom(str, '', var='colors')),
             jg.Dict.make_key('strip_color', jg.Enum(preset_colors, preset_empty_color, var='strip_color')),
             jg.Dict.make_key('strip_toggle_color',
                              jg.Enum(preset_colors, preset_empty_color, var='strip_toggle_color')),
             jg.Dict.make_key('messages', jg.List(32, preset_message_schema, var='messages'))],
            model=IntuitivePreset)

# The Bank Message is a bank message, includes only trigger state (no toggle) as well as the included MIDI message
bank_message_schema = \
    jg.Dict('bank_message',
            [jg.Dict.make_key('trigger',
                              jg.Enum(bank_message_trigger, bank_message_trigger_default, var='trigger')),
             jg.Dict.make_key('midi_message', jg.Atom(str, var='midi_message'))],
            model=IntuitiveBankMessage)

# All the information associated with a bank
bank_schema = \
    jg.Dict('bank',
            [jg.Dict.make_key('name', jg.Atom(str, '', var='name')),
             jg.Dict.make_key('description', jg.Atom(str, '', var='description')),
             jg.Dict.make_key('colors', jg.Atom(str, '', var='colors')),
             jg.Dict.make_key('clear_toggle', jg.Atom(bool, False, var='clear_toggle')),
             jg.Dict.make_key('display_description', jg.Atom(bool, False, var='display_description')),
             jg.Dict.make_key('messages', jg.List(32, bank_message_schema, var='messages')),
             jg.Dict.make_key('presets', jg.List(0, preset_schema, var='presets'))],
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
            [jg.Dict.make_key('midi_channels', jg.List(16, midi_channel_schema, var='midi_channels')),
             jg.Dict.make_key('messages', jg.List(0, message_schema, var='messages')),
             jg.Dict.make_key('banks', jg.List(128, bank_schema, var='banks')),
             jg.Dict.make_key('midi_channel', jg.Atom(int, 1, var='midi_channel')),
             jg.Dict.make_key('colors', jg.List(0, colors_schema, var='colors')),
             jg.Dict.make_key('navigator', jg.Atom(bool, False, var='navigator')),
             jg.Dict.make_key('version', jg.Atom(str, value=version_verify, var='version'), required=True)],
            model=MC6ProIntuitive)

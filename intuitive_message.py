import copy

import json_grammar as jg
import intuitive_midi_channel


def midi_channel_from_base(base_midi_channel, midi_channels):
    if base_midi_channel is None:
        base_midi_channel = 1
    base_midi_channel -= 1
    if base_midi_channel >= len(midi_channels) or midi_channels[base_midi_channel] is None:
        new_elem = intuitive_midi_channel.IntuitiveMidiChannel('MIDI Channel ' + str(base_midi_channel + 1))
        while len(midi_channels) <= base_midi_channel:
            midi_channels.append(None)
        midi_channels[base_midi_channel] = new_elem
    return midi_channels[base_midi_channel].name


intuitive_message_type = ["unused", "PC", "CC", "Note On", "Note Off",
                          "Real Time", "SysEx", "MIDI Clock", "message8",
                          "message9", "Bank Up", "Bank Down", "Bank Change Mode",
                          # 13
                          "Bank Jump", "Toggle Page", "Set Toggle", "Set MIDI Thru",
                          # 17
                          "Select Exp Message", "Looper Mode", "message19", "message20",
                          "message21", "Toggle Preset", "Delay", "MIDI Clock Tap",
                          "Song Position", "CC Waveform Generator", "Engage Preset", "message28",
                          "message29", "message30", "CC Sequence Generator", "CC Value Scroll",
                          # 33
                          "PC Number Scroll", "PC Multichannel", "message35", "Utility",
                          "message37", "message38", "message39", "Relay Switching",
                          "MIDI MMC", "Trigger Messages", "message43", "Preset Rename",
                          # Below here are Intuitive Only actions
                          # 45
                          "Page Jump", "Preset Scroll Message Count", "Disengage Looper Mode",
                          # 48
                          'Stop CC Waveform Generator', 'Stop CC Sequence Generator',
                          # 50
                          'Stop All CC Waveform Generator', 'Stop All CC Sequence Generator',
                          # 52
                          'Start CC Waveform Generator', 'Start CC Sequence Generator',
                          # 54
                          'Start CC Waveform Generator No MIDI Clock', 'Start CC Sequence Generator No MIDI Clock',
                          # 56
                          'MIDI Clock Tap Menu', 'PC Number Scroll Update', 'CC Value Scroll Update']
intuitive_message_default = intuitive_message_type[0]

pc_number_scroll_change = ["", "Increase", "Decrease"]
pc_number_scroll_change_default = pc_number_scroll_change[0]


utility_message_type = ["Set Message Scroll Counter", "Clear Global Preset Toggles", "Increase MIDI Clock BPM by 1",
                        "Decrease MIDI Clock BPM by 1", "Set Scroll Counter Values", "Set MIDI Output Mask",
                        "Manage Preset Scroll", "Set Preset Background/Text/Strip Color",
                        "Set Bank Background/Text Color"]
utility_message_preset_scroll_type = ["Do Nothing", "Toggle Scroll Direction", "Toggle Scroll Direction and Execute",
                                      "Reverse Direction Once and Execute", "Set number of messages to scroll"]

realtime_message_type = ["Nothing", "Start", "Stop", "Continue"]
realtime_message_default = realtime_message_type[0]

midi_mmc_type = ["Nothing", "Stop", "Play", "Deferred PLay", "Fast Forward", "Rewind", "Record Strobe", "Record Exit",
                 "Record Pause", "Pause", "Eject", "Chase", "MMC Reset"]
midi_mmc_default = midi_mmc_type[0]

set_toggle_type = ["Dis-engage Toggle", "Unused", "Engage Toggle", "Toggle", "Shift", "Shift+", "Unshift"]
set_toggle_default = set_toggle_type[0]

onoff_type = ["Off", "On"]
onoff_default = onoff_type[0]

tip_ring_action_type = ["Nothing", "Tap - NO", "Tap - NC", "Engage", "Disengage", "Toggle", "Sync Clock 8 Taps"]
tip_ring_action_default = tip_ring_action_type[0]

relay_type = ['Omniport 1', 'Omniport 2', 'Omniport 3', 'Omniport 4', 'Relay Port A', 'Relay Port B']
relay_default = relay_type[0]

bpm_decimal = ['+0', '+0.25', '+0.5', '0.75']
bpm_decimal_default = bpm_decimal[0]

note_divisions = ["Whole", "Half", "Quarter", "Eighth", "Triplets", "Sixteenth", "2 Whole", "3 Whole", "4 Whole"]
note_divisions_default = note_divisions[0]

looper_mode = ['Toggle', 'Engage']
looper_mode_default = looper_mode[0]

# This may seem like it doesn't belong, but it does appear INSIDE messages
preset_message_trigger = ["No Action", "Press", "Release", "Long Press", "Long Press Scroll", "Long Press Release",
                          "Release All", "Double Tap", "Double Tap Release", "Long Double Tap",
                          "Long Double Tap Release", "On First Engage", "On First Engage (send only this)",
                          "On Disengage"]
preset_message_trigger_default = preset_message_trigger[0]


class PCCCBaseModel(jg.JsonGrammarModel):
    def __init__(self):
        super().__init__('PCCCBaseModel')
        self.number = None
        self.value = None
        self.channel = None

    def eq_common(self, other):
        result = isinstance(other, PCCCBaseModel) and self.number == other.number and self.channel == other.channel
        if not result:
            self.modified = True
        return result

    def eq_value(self, other):
        result = isinstance(other, PCCCBaseModel) and self.value == other.value
        if not result:
            self.modified = True
        return result

    def from_base_common(self, channel, base_message):
        name = channel + ':'
        self.channel = channel
        if base_message.msg_array_data is None:
            self.number = 0
        else:
            self.number = base_message.msg_array_data[0]
            if self.number is None:
                self.number = 0
        name += str(self.number)
        return name

    def to_base_common(self, base_message, midi_channels):
        base_message.channel = midi_channels.index(self.channel)
        base_message.channel += 1
        if base_message.channel == 1:
            base_message.channel = None

        base_message.msg_array_data[0] = self.number


class PCModel(PCCCBaseModel):
    def __init__(self):
        super().__init__()

    def __eq__(self, other):
        result = isinstance(other, PCModel) and self.eq_common(other)
        if not result:
            self.modified = True
        return result

    def from_base(self, channel, base_message):
        return self.from_base_common(channel, base_message)

    def to_base(self, base_message, _bank_catalog, midi_channels, _intuitive_bank, _intuitive_preset):
        self.to_base_common(base_message, midi_channels)


class CCModel(PCCCBaseModel):
    def __init__(self):
        super().__init__()

    def __eq__(self, other):
        result = isinstance(other, CCModel) and self.eq_common(other) and self.eq_value(other)
        if not result:
            self.modified = True
        return result

    def from_base(self, channel, base_message):
        name = self.from_base_common(channel, base_message)
        if base_message.msg_array_data is None:
            self.value = 0
        else:
            self.value = base_message.msg_array_data[1]
            if self.value is None:
                self.value = 0
        name += ':' + str(self.value)
        return name

    def to_base(self, base_message, _bank_catalog, midi_channels, _intuitive_bank, _intuitive_preset):
        self.to_base_common(base_message, midi_channels)
        base_message.msg_array_data[1] = self.value


class PCMultichannelModel(jg.JsonGrammarModel):

    def __init__(self):
        super().__init__('PCMultichannelModel')
        self.number = None
        self.channels = None

    def __eq__(self, other):
        result = isinstance(other, PCMultichannelModel) and self.number == other.number
        result = result and self.channels == other.channels
        if not result:
            self.modified = True
        return result

    def midi_multichannel_from_base(self, base_message, midi_channels):
        multichannel = base_message.msg_array_data[1]
        if multichannel is None:
            multichannel = 0
        channel = 0
        self.channels = []
        while multichannel > 0:
            if multichannel & 1:
                self.channels.append(midi_channels[channel].name)
            multichannel = multichannel >> 1
            channel += 1

    def from_base(self, base_message, midi_channels):
        self.number = base_message.msg_array_data[0]
        if self.number is None:
            self.number = 0
        self.midi_multichannel_from_base(base_message, midi_channels)
        return ','.join(self.channels) + ':' + str(self.number)

    def to_base(self, base_message, _bank_catalog, midi_channels, _intuitive_bank, _intuitive_preset):
        base_message.msg_array_data[0] = self.number
        base_message.msg_array_data[1] = 0
        for channel in self.channels:
            pos = midi_channels.index(channel)
            base_message.msg_array_data[1] |= 1 << pos


# pc_number_scroll_type = ['Send Only', 'Increase and Send', 'Decrease and Send', 'Update Only', 'Reset Only',
#                          'Increase Only', 'Decrease Only']
# Opcode is byte 0 upper 4 bits
# Counter is byte 0 lower 4 bits
# If change, wrap is byte 2 == 0
# If CC, CC number is byte 1
class PCCCNumberValueScrollBaseModel(jg.JsonGrammarModel):
    @staticmethod
    def common_keys():
        return [jg.SwitchDict.make_key('send', jg.Atom('Send', bool, var='send')),
                jg.SwitchDict.make_key('change',
                                       jg.Enum('Change', pc_number_scroll_change,
                                               pc_number_scroll_change_default, var='change')),
                jg.SwitchDict.make_key('counter',
                                       jg.Atom('Counter', int, 0, var='counter')),
                jg.SwitchDict.make_key('channel', jg.Atom('Channel', str, '', var='channel')),
                jg.SwitchDict.make_key('wrap', jg.Atom('Wrap', bool, True, var='wrap'))]

    @staticmethod
    def cc_keys():
        return [jg.SwitchDict.make_key('number', jg.Atom('Number', int, var='number')),
                jg.SwitchDict.make_key('step', jg.Atom('Step', int, var='step'))]

    @staticmethod
    def update_keys():
        return [jg.SwitchDict.make_key('counter', jg.Atom('Counter', int, 0, var='counter')),
                jg.SwitchDict.make_key('value', jg.Atom('Value', int, 0, var='value'))]

    @staticmethod
    def get_opcode(base_message):
        if base_message.msg_array_data is None or base_message.msg_array_data[0] is None:
            opcode = 0
        else:
            opcode = (base_message.msg_array_data[0] & 0b11110000) >> 4
        return opcode

    @staticmethod
    def get_specific_message(intuitive_message, base_message):
        opcode = PCCCNumberValueScrollBaseModel.get_opcode(base_message)
        if opcode == 3 or opcode == 4:
            if intuitive_message.type == 'PC Number Scroll':
                intuitive_message.type = 'PC Number Scroll Update'
                intuitive_message.specific_message = PCNumberScrollUpdateModel()
            else:
                intuitive_message.type = 'CC Value Scroll Update'
                intuitive_message.specific_message = CCValueScrollUpdateModel()
            intuitive_message.name = intuitive_message.type + ':'
        else:
            if intuitive_message.type == 'PC Number Scroll':
                intuitive_message.specific_message = PCNumberScrollModel()
            else:
                intuitive_message.specific_message = CCValueScrollModel()

    def __init__(self):
        super().__init__('PCCCNumberValueScrollBaseModel')
        self.send = None
        self.change = None
        self.counter = None
        self.value = None
        self.channel = None
        self.wrap = None
        self.number = None
        self.step = None

    def __eq__(self, other):
        result = isinstance(other, PCCCNumberValueScrollBaseModel) and self.send == other.send
        result = result and self.change == other.change and self.counter == other.counter
        result = result and self.value == other.value and self.channel == other.channel and self.wrap == other.wrap
        result = result and self.number == other.number and self.step == other.step
        if not result:
            self.modified = True
        return result

    def eq_common(self, other):
        result = isinstance(other, PCCCNumberValueScrollBaseModel) and self.send == other.send
        result = result and self.change == other.change and self.counter == other.counter
        result = result and self.channel == other.channel and self.wrap == other.wrap
        if not result:
            self.modified = True
        return result

    def eq_cc(self, other):
        result = isinstance(other, PCCCNumberValueScrollBaseModel)
        result = result and self.number == other.number and self.step == other.step
        if not result:
            self.modified = True
        return result

    def eq_update(self, other):
        result = isinstance(other, PCCCNumberValueScrollBaseModel)
        result = result and self.value == other.value and self.counter == other.counter
        if not result:
            self.modified = True
        return result

    def from_base_common(self, midi_channels, base_message, name):
        opcode = PCCCNumberValueScrollBaseModel.get_opcode(base_message)
        self.send = opcode < 3
        if self.send:
            name.append('Send')
        if opcode == 1 or opcode == 5:
            self.change = "Increase"
        elif opcode == 2 or opcode == 6:
            self.change = "Decrease"
        if self.change is not None:
            name.append(self.change)
        if self.change == pc_number_scroll_change_default:
            self.change = None
        if self.send:
            self.channel = midi_channel_from_base(base_message.channel, midi_channels)
            name.append(self.channel)

    def from_base_wrap(self, is_cc, base_message, name):
        if is_cc:
            if self.change is not None:
                if base_message.msg_array_data is None or base_message.msg_array_data[2] is None:
                    self.wrap = True
                else:
                    self.wrap = (base_message.msg_array_data[2] & 64) != 0
        else:
            if self.change is not None:
                if base_message.msg_array_data is None or base_message.msg_array_data[2] is None:
                    self.wrap = True
                else:
                    self.wrap = base_message.msg_array_data[2] == 0
        if self.wrap is None or self.wrap:
            name.append("Wrap")
            self.wrap = None
        else:
            name.append("No Wrap")
        if is_cc:
            name.append(str(self.step))

    def from_base_cc(self, base_message, name):
        self.number = 0
        if base_message.msg_array_data is not None and base_message.msg_array_data[1] is not None:
            self.number = base_message.msg_array_data[1]
        name.append('CC' + str(self.number))
        if base_message.msg_array_data is None or base_message.msg_array_data[2] is None:
            self.step = 0
        else:
            self.step = base_message.msg_array_data[2] & 63
        name.append('Step ' + str(self.step))

    def from_base_counter(self, base_message, name):
        if base_message.msg_array_data is None or base_message.msg_array_data[0] is None:
            self.counter = 0
        else:
            self.counter = (base_message.msg_array_data[0] & 0b1111)
        name.append('Counter ' + str(self.counter))
        if self.counter == 0:
            self.counter = None

    def from_base_update(self, base_message, name):
        opcode = PCCCNumberValueScrollBaseModel.get_opcode(base_message)
        self.value = 0
        if opcode == 3 and base_message.msg_array_data is not None and base_message.msg_array_data[1] is not None:
            self.value = base_message.msg_array_data[1]
        name.append(str(self.value))
        if self.value == 0:
            self.value = None

    def to_base_common(self, base_message, midi_channels):
        if self.send:
            if self.change == 'Increase':
                opcode = 1
            elif self.change == 'Decrease':
                opcode = 2
            else:
                opcode = 0
        else:
            if self.change == 'Increase':
                opcode = 5
            else:
                opcode = 6
        base_message.msg_array_data[0] = opcode << 4
        if self.channel is not None:
            base_message.channel = midi_channels.index(self.channel)
            if base_message.channel == 0:
                base_message.channel = None
            else:
                base_message.channel += 1

    def to_base_wrap(self, is_cc, base_message):
        if self.change is not None:
            if is_cc:
                if self.step != 1:
                    if self.wrap is None or self.wrap:
                        wrap = 1
                    else:
                        wrap = 0
                    base_message.msg_array_data[2] |= wrap << 6
            else:
                if self.wrap is not None and not self.wrap:
                    base_message.msg_array_data[2] = 1

    def to_base_cc(self, base_message):
        base_message.msg_array_data[1] = self.number
        if self.step is not None and self.step != 0:
            base_message.msg_array_data[2] = self.step

    def to_base_counter(self, base_message):
        counter = self.counter
        if counter is None:
            counter = 0
        if base_message.msg_array_data[0] is None:
            base_message.msg_array_data[0] = 0
        base_message.msg_array_data[0] |= counter

    def to_base_update(self, base_message):
        opcode = 4
        if self.value is not None and self.value != 0:
            opcode = 3
            base_message.msg_array_data[1] = self.value
        base_message.msg_array_data[0] = (base_message.msg_array_data[0] & 0xF) | (opcode << 4)


class PCNumberScrollModel(PCCCNumberValueScrollBaseModel):
    @staticmethod
    def get_keys():
        return PCCCNumberValueScrollBaseModel.common_keys()

    def __init__(self):
        super().__init__()

    def __eq__(self, other):
        result = isinstance(other, PCNumberScrollModel) and self.eq_common(other)
        if not result:
            self.modified = True
        return result

    def from_base(self, midi_channels, base_message):
        name = []
        self.from_base_common(midi_channels, base_message, name)
        self.from_base_counter(base_message, name)
        self.from_base_wrap(False, base_message, name)
        return ':'.join(name)

    def to_base(self, base_message, _bank_catalog, midi_channels, _intuitive_bank, _intuitive_preset):
        self.to_base_common(base_message, midi_channels)
        self.to_base_counter(base_message)
        self.to_base_wrap(False, base_message)


class CCValueScrollModel(PCCCNumberValueScrollBaseModel):
    @staticmethod
    def get_keys():
        return PCCCNumberValueScrollBaseModel.common_keys() + PCCCNumberValueScrollBaseModel.cc_keys()

    def __init__(self):
        super().__init__()

    def __eq__(self, other):
        result = isinstance(other, CCValueScrollModel) and self.eq_common(other) and self.eq_cc(other)
        if not result:
            self.modified = True
        return result

    def from_base(self, midi_channels, base_message):
        name = []
        self.from_base_common(midi_channels, base_message, name)
        self.from_base_counter(base_message, name)
        self.from_base_cc(base_message, name)
        self.from_base_wrap(True, base_message, name)
        return ':'.join(name)

    def to_base(self, base_message, _bank_catalog, midi_channels, _intuitive_bank, _intuitive_preset):
        self.to_base_common(base_message, midi_channels)
        self.to_base_counter(base_message)
        self.to_base_cc(base_message)
        self.to_base_wrap(True, base_message)


class PCNumberScrollUpdateModel(PCCCNumberValueScrollBaseModel):
    @staticmethod
    def get_keys():
        return PCCCNumberValueScrollBaseModel.update_keys()

    def __init__(self):
        super().__init__()

    def __eq__(self, other):
        result = isinstance(other, PCNumberScrollUpdateModel) and self.eq_update(other)
        if not result:
            self.modified = True
        return result

# Opcode 3 is update, opcode 4 is reset
    def from_base(self, _midi_channels, base_message):
        name = []
        self.from_base_counter(base_message, name)
        self.from_base_update(base_message, name)
        return ':'.join(name)

    def to_base(self, base_message, _bank_catalog, midi_channels, _intuitive_bank, _intuitive_preset):
        base_message.type = intuitive_message_type.index("PC Number Scroll")
        self.to_base_common(base_message, midi_channels)
        self.to_base_counter(base_message)
        self.to_base_update(base_message)


class CCValueScrollUpdateModel(PCCCNumberValueScrollBaseModel):
    @staticmethod
    def get_keys():
        return PCCCNumberValueScrollBaseModel.update_keys()

    def __init__(self):
        super().__init__()

    def __eq__(self, other):
        result = isinstance(other, CCValueScrollUpdateModel) and self.eq_update(other)
        if not result:
            self.modified = True
        return result

    def from_base(self, _midi_channels, base_message):
        name = []
        self.from_base_counter(base_message, name)
        self.from_base_update(base_message, name)
        return ':'.join(name)

    def to_base(self, base_message, _bank_catalog, midi_channels, _intuitive_bank, _intuitive_preset):
        self.to_base_common(base_message, midi_channels)
        self.to_base_counter(base_message)
        self.to_base_update(base_message)


# For Bank Jump in the base:
#  data[0] is the bank number, base 0
#  data[1] should be 0, it is 127 for last used
#  data[2] is the page number (6 = 1, 7 = 2, 14 = 3, 15 = 4)
class BankJumpModel(jg.JsonGrammarModel):
    @staticmethod
    def mk_bank_jump_message(bank, page):
        result = BankJumpModel()
        result.bank = bank
        result.page = page
        return result

    def __init__(self):
        super().__init__('BankJumpModel')
        self.bank = None
        self.page = None

    def __eq__(self, other):
        result = isinstance(other, BankJumpModel) and self.bank == other.bank and self.page == other.page
        if not result:
            self.modified = True
        return result

    def from_base(self, base_message, banks):
        bank_number = 0
        if base_message.msg_array_data[0] is not None:
            bank_number = base_message.msg_array_data[0]
        self.bank = banks[bank_number]
        if base_message.msg_array_data[2] == 6:
            self.page = None
        elif base_message.msg_array_data[2] == 7:
            self.page = 1
        elif base_message.msg_array_data[2] == 14:
            self.page = 2
        elif base_message.msg_array_data[2] == 15:
            self.page = 3
        else:
            raise IntuitiveException('missing case', 'missing case')
        name = self.bank
        if self.page is not None:
            name += ':' + str(self.page)
        if base_message.msg_array_data[1] is not None:
            raise IntuitiveException('bad_message', 'data array is nonzero')
        return name

    def to_base(self, base_message, bank_catalog, _midi_channels, _intuitive_bank, _intuitive_preset):
        base_message.msg_array_data[0] = bank_catalog[self.bank]
        if self.page == 0 or self.page is None:
            base_message.msg_array_data[2] = 6
        elif self.page == 1:
            base_message.msg_array_data[2] = 7
        elif self.page == 2:
            base_message.msg_array_data[2] = 14
        elif self.page == 3:
            base_message.msg_array_data[2] = 15
        else:
            raise IntuitiveException('invalid_page_number', "Invalid page number in bank jump")


class PageJumpModel(jg.JsonGrammarModel):
    def __init__(self):
        super().__init__('PageJumpModel')
        self.page = None

    def __eq__(self, other):
        result = isinstance(other, PageJumpModel) and self.page == other.page
        if not result:
            self.modified = True
        return result

    def from_base(self, base_message):
        self.page = base_message.msg_array_data[0] - 3
        return str(self.page)

    def to_base(self, base_message, _bank_catalog, _midi_channels, _intuitive_bank, _intuitive_preset):
        base_message.type = intuitive_message_type.index('Toggle Page')
        base_message.msg_array_data[0] = self.page + 3


class TogglePageModel(jg.JsonGrammarModel):
    @staticmethod
    def mk_toggle_page_message(page_up):
        result = TogglePageModel()
        result.page_up = page_up
        return result

    def __init__(self):
        super().__init__('TogglePageModel')
        self.page_up = None

    def __eq__(self, other):
        result = isinstance(other, TogglePageModel) and self.page_up == other.page_up
        if not result:
            self.modified = True
        return result

    def from_base(self, base_message):
        self.page_up = base_message.msg_array_data[0] == 1
        if self.page_up:
            return "Up"
        else:
            return "Down"

    def to_base(self, base_message, _bank_catalog, _midi_channels, _intuitive_bank, _intuitive_preset):
        if self.page_up:
            base_message.msg_array_data[0] = 1
        else:
            base_message.msg_array_data[0] = 2


class NoteOnModel(jg.JsonGrammarModel):
    @staticmethod
    def get_common_keys():
        return [jg.SwitchDict.make_key('note', jg.Atom('Note', int, var='note')),
                jg.SwitchDict.make_key('velocity', jg.Atom('Velocity', int, var='velocity')),
                jg.SwitchDict.make_key('channel', jg.Atom('Channel', str, '', var='channel'))]

    @staticmethod
    def get_keys():
        return NoteOnModel.get_common_keys()

    def __init__(self):
        super().__init__('NoteOnModel')
        self.channel = None
        self.note = None
        self.velocity = None

    def __eq__(self, other):
        result = isinstance(other, NoteOnModel) and self.channel == other.channel and self.note == other.note
        result = result and self.velocity == other.velocity
        if not result:
            self.modified = True
        return result

    def from_base(self, channel, base_message):
        self.channel = channel
        if base_message.msg_array_data is None:
            self.note = 0
            self.velocity = 0
        else:
            if base_message.msg_array_data[0] is None:
                self.note = 0
            else:
                self.note = base_message.msg_array_data[0]
            if base_message.msg_array_data[1] is None:
                self.velocity = 0
            else:
                self.velocity = base_message.msg_array_data[1]
        note_name = str(self.note)
        return note_name + ':' + str(self.velocity) + ':' + self.channel

    def to_base(self, base_message, _bank_catalog, midi_channels, _intuitive_bank, _intuitive_preset):
        base_message.msg_array_data[0] = self.note
        base_message.msg_array_data[1] = self.velocity
        base_message.channel = midi_channels.index(self.channel)
        if base_message.channel == 0:
            base_message.channel = None
        else:
            base_message.channel += 1


class NoteOffModel(jg.JsonGrammarModel):
    @staticmethod
    def get_keys():
        all_notes_key = jg.SwitchDict.make_key('all_notes', jg.Atom('All Notes', bool, var='all_notes'))
        return NoteOnModel.get_common_keys() + [all_notes_key]

    def __init__(self):
        super().__init__('NoteOffModel')
        self.channel = None
        self.note = None
        self.velocity = None
        self.all_notes = None

    def __eq__(self, other):
        result = isinstance(other, NoteOffModel) and self.channel == other.channel and self.note == other.note
        result = result and self.velocity == other.velocity and self.all_notes == other.all_notes
        if not result:
            self.modified = True
        return result

    def from_base(self, channel, base_message):
        self.channel = channel
        if base_message.msg_array_data is None:
            self.note = 0
            self.velocity = 0
            self.all_notes = False
        else:
            if base_message.msg_array_data[0] is None:
                self.note = 0
            else:
                self.note = base_message.msg_array_data[0]
            if base_message.msg_array_data[1] is None:
                self.velocity = 0
            else:
                self.velocity = base_message.msg_array_data[1]
            if base_message.msg_array_data[2] == 1:
                self.all_notes = True
        note_name = str(self.note)
        if self.all_notes:
            note_name = 'all'
        return note_name + ':' + str(self.velocity) + ':' + self.channel

    def to_base(self, base_message, _bank_catalog, midi_channels, _intuitive_bank, _intuitive_preset):
        base_message.channel = midi_channels.index(self.channel)
        if base_message.channel == 0:
            base_message.channel = None
        else:
            base_message.channel += 1
        base_message.msg_array_data[0] = self.note
        base_message.msg_array_data[1] = self.velocity
        if self.all_notes:
            base_message.msg_array_data[2] = 1


class RealTimeModel(jg.JsonGrammarModel):
    def __init__(self):
        super().__init__('RealTimeModel')
        self.real_time_type = None

    def __eq__(self, other):
        result = isinstance(other, RealTimeModel) and self.real_time_type == other.real_time_type
        if not result:
            self.modified = True
        return result

    def from_base(self, base_message):
        if base_message.msg_array_data is None or base_message.msg_array_data[0] is None:
            self.real_time_type = realtime_message_default
        else:
            self.real_time_type = realtime_message_type[base_message.msg_array_data[0]]
        return self.real_time_type

    def to_base(self, base_message, _bank_catalog, _midi_channels, _intuitive_bank, _intuitive_preset):
        base_message.msg_array_data[0] = realtime_message_type.index(self.real_time_type)


class PresetRenameModel(jg.JsonGrammarModel):
    def __init__(self):
        super().__init__('PresetRenameModel')
        self.new_name = None

    def __eq__(self, other):
        result = isinstance(other, PresetRenameModel) and self.new_name == other.new_name
        if not result:
            self.modified = True
        return result

    def from_base(self, base_message):
        chars = copy.deepcopy(base_message.msg_array_data)
        jg.prune_list(chars)
        self.new_name = ''.join(map(chr, chars))
        return self.new_name

    def to_base(self, base_message, _bank_catalog, _midi_channels, _intuitive_bank, _intuitive_preset):
        data = map(ord, [*self.new_name])
        for i, val in enumerate(data):
            base_message.msg_array_data[i] = val


class SongPositionModel(jg.JsonGrammarModel):
    def __init__(self):
        super().__init__('SongPositionModel')
        self.song_position = None

    def __eq__(self, other):
        result = isinstance(other, SongPositionModel) and self.song_position == other.song_position
        if not result:
            self.modified = True
        return result

    def from_base(self, base_message):
        if base_message.msg_array_data is None or base_message.msg_array_data[1] is None:
            self.song_position = 0
        else:
            self.song_position = base_message.msg_array_data[1]
        return str(self.song_position)

    def to_base(self, base_message, _bank_catalog, _midi_channels, _intuitive_bank, _intuitive_preset):
        base_message.msg_array_data[1] = self.song_position


class MIDIMMCModel(jg.JsonGrammarModel):
    def __init__(self):
        super().__init__('MIDIMMCModel')
        self.midi_mmc_type = None

    def __eq__(self, other):
        result = isinstance(other, MIDIMMCModel) and self.midi_mmc_type == other.midi_mmc_type
        if not result:
            self.modified = True
        return result

    def from_base(self, base_message):
        if base_message.msg_array_data is None or base_message.msg_array_data[0] is None:
            self.midi_mmc_type = midi_mmc_default
        else:
            self.midi_mmc_type = midi_mmc_type[base_message.msg_array_data[0]]
        return self.midi_mmc_type

    def to_base(self, base_message, _bank_catalog, _midi_channels, _intuitive_bank, _intuitive_preset):
        base_message.msg_array_data[0] = midi_mmc_type.index(self.midi_mmc_type)


class MIDIClockModel(jg.JsonGrammarModel):
    @staticmethod
    def is_tap_menu(message, msg_array_data):
        if msg_array_data is None:
            is_tap_menu = False
        elif msg_array_data[2] is None:
            is_tap_menu = False
        else:
            is_tap_menu = (msg_array_data[2] & 0b1) != 0
        if is_tap_menu:
            message.type = 'MIDI Clock Tap Menu'
            message.name = message.type + ':'
            message.specific_message = MIDIClockTapMenuModel()
        else:
            message.specific_message = MIDIClockModel()

    def __init__(self):
        super().__init__('MIDIClockModel')
        self.stop_clock = None
        self.bpm = None
        self.bpm_decimal = None

    def __eq__(self, other):
        result = isinstance(other, MIDIClockModel) and self.stop_clock == other.stop_clock and self.bpm == other.bpm
        result = result and self.bpm_decimal == other.bpm_decimal
        if not result:
            self.modified = True
        return result

    def from_base(self, base_message):
        name = []
        if base_message.msg_array_data is None:
            self.stop_clock = True
            name.append('Stop MIDI Clock')
        else:
            flags = base_message.msg_array_data[2]
            if flags is None:
                flags = 0
            if flags & 0b1111 != flags:
                raise IntuitiveException('bad_midi_clock', "Got a MIDI Clock message with flags I cannot parse")
            self.stop_clock = flags & 0b10 == 0
            if self.stop_clock:
                name.append("Stop MIDI Clock")
            else:
                name.append("Don't Stop MIDI Clock")
            if base_message.msg_array_data[0] is not None:
                raise IntuitiveException('bad_midi_clock', "Got a MIDI Clock message I cannot parse")
            if not self.stop_clock:
                bpm = base_message.msg_array_data[1]
                if bpm is None:
                    bpm = 0
                self.bpm = bpm
                name.append(str(self.bpm))
                bpm_decimal_index = (flags & 0b1100) >> 2
                self.bpm_decimal = bpm_decimal[bpm_decimal_index]
                name.append(self.bpm_decimal)
        return ':'.join(name)

    def to_base(self, base_message, _bank_catalog, _midi_channels, _intuitive_bank, _intuitive_preset):
        if self.bpm is None:
            base_message.msg_array_data[1] = None
        else:
            base_message.msg_array_data[1] = self.bpm
        if self.bpm_decimal is not None:
            bpm_index = bpm_decimal.index(self.bpm_decimal)
        else:
            bpm_index = bpm_decimal.index(bpm_decimal_default)
        flags = bpm_index << 2
        if not self.stop_clock:
            flags = flags | 0b10
        if flags != 0:
            base_message.msg_array_data[2] = flags


class MIDIClockTapMenuModel(jg.JsonGrammarModel):
    def __init__(self):
        super().__init__('MIDIClockTapMenuModel')
        self.use_current_bpm = None
        self.bpm = None
        self.bpm_decimal = None

    def __eq__(self, other):
        result = isinstance(other, MIDIClockTapMenuModel) and self.use_current_bpm == other.use_current_bpm
        result = result and self.bpm == other.bpm and self.bpm_decimal == other.bpm_decimal
        if not result:
            self.modified = True
        return result

    def from_base(self, base_message):
        name = []
        if base_message.msg_array_data is None:
            self.use_current_bpm = True
            name.append('Use Current BPM')
            self.bpm = 0
            name.append('0')
            self.bpm_decimal = bpm_decimal_default
            name.append(self.bpm_decimal)
        else:
            flags = base_message.msg_array_data[2]
            if flags is None:
                flags = 0
            if flags & 0b1111 != flags:
                raise IntuitiveException('bad_midi_clock', "Got a MIDI Clock message with flags I cannot parse")
            self.use_current_bpm = flags & 0b10 != 0
            if self.use_current_bpm:
                name.append('Use Current BPM')
            else:
                name.append("Don't Use Current BPM")
            if not self.use_current_bpm:
                bpm = base_message.msg_array_data[1]
                if bpm is None:
                    bpm = 0
                self.bpm = bpm
                name.append(str(self.bpm))
                bpm_decimal_index = (flags & 0b1100) >> 2
                self.bpm_decimal = bpm_decimal[bpm_decimal_index]
                name.append(self.bpm_decimal)
        if self.bpm == 0:
            self.bpm = None
        if self.bpm_decimal == bpm_decimal_default:
            self.bpm_decimal = None
        return ':'.join(name)

    def to_base(self, base_message, _bank_catalog, _midi_channels, _intuitive_bank, _intuitive_preset):
        base_message.type = intuitive_message_type.index('MIDI Clock')
        if self.bpm is None:
            base_message.msg_array_data[1] = None
        else:
            base_message.msg_array_data[1] = self.bpm
        if self.bpm_decimal is not None:
            bpm_index = bpm_decimal.index(self.bpm_decimal)
        else:
            bpm_index = bpm_decimal.index(bpm_decimal_default)
        flags = bpm_index << 2
        if self.use_current_bpm:
            flags = flags | 2
        flags = flags | 1
        base_message.msg_array_data[2] = flags


class DelayModel(jg.JsonGrammarModel):
    def __init__(self):
        super().__init__('DelayModel')
        self.delay = None

    def __eq__(self, other):
        result = isinstance(other, DelayModel) and self.delay == other.delay
        if not result:
            self.modified = True
        return result

    def from_base(self, base_message):
        if base_message.msg_array_data is None or base_message.msg_array_data[0] is None:
            self.delay = 0
        else:
            self.delay = base_message.msg_array_data[0] * 10
        return str(self.delay)

    def to_base(self, base_message, _bank_catalog, _midi_channels, _intuitive_bank, _intuitive_preset):
        if self.delay is not None:
            base_message.msg_array_data[0] = self.delay // 10


class RelaySwitchingModel(jg.JsonGrammarModel):
    def __init__(self):
        super().__init__('RelaySwitchingModel')
        self.relay = None
        self.tip_action = None
        self.ring_action = None

    def __eq__(self, other):
        result = isinstance(other, RelaySwitchingModel) and self.relay == other.relay
        result = result and self.tip_action == other.tip_action and self.ring_action == other.ring_action
        if not result:
            self.modified = True
        return result

    def from_base(self, base_message):
        if base_message.msg_array_data is None:
            self.relay = relay_default
            self.tip_action = tip_ring_action_default
            self.ring_action = tip_ring_action_default
        else:
            if base_message.msg_array_data[0] is None:
                self.relay = relay_default
            else:
                self.relay = relay_type[base_message.msg_array_data[0]]
            if base_message.msg_array_data[1] is None:
                self.tip_action = tip_ring_action_default
            else:
                self.tip_action = tip_ring_action_type[base_message.msg_array_data[1]]
            if base_message.msg_array_data[2] is None:
                self.ring_action = tip_ring_action_default
            else:
                self.ring_action = tip_ring_action_type[base_message.msg_array_data[2]]
        relay_type_name = self.relay
        if self.relay == relay_default:
            self.relay = None
        return relay_type_name + ':' + self.tip_action + ':' + self.ring_action

    def to_base(self, base_message, _bank_catalog, _midi_channels, _intuitive_bank, _intuitive_preset):
        if self.relay is not None and self.relay != relay_default:
            base_message.msg_array_data[0] = relay_type.index(self.relay)
        if self.tip_action is not None and self.tip_action != tip_ring_action_default:
            base_message.msg_array_data[1] = tip_ring_action_type.index(self.tip_action)
        if self.ring_action is not None and self.ring_action != tip_ring_action_default:
            base_message.msg_array_data[2] = tip_ring_action_type.index(self.ring_action)


class PresetScrollMessageCountModel(jg.JsonGrammarModel):
    def __init__(self):
        super().__init__('PresetScrollMessageCountModel')
        self.message_count = None

    def __eq__(self, other):
        result = isinstance(other, PresetScrollMessageCountModel) and self.message_count == other.message_count
        if not result:
            self.modified = True
        return result

    def from_base(self, base_message):
        self.message_count = base_message.msg_array_data[2]
        return str(self.message_count)

    def to_base(self, base_message, _bank_catalog, _midi_channels, _intuitive_bank, _intuitive_preset):
        base_message.type = intuitive_message_type.index("Utility")
        base_message.msg_array_data[0] = utility_message_type.index("Manage Preset Scroll")
        base_message.msg_array_data[1] = utility_message_preset_scroll_type.index("Set number of messages to scroll")
        base_message.msg_array_data[2] = self.message_count


class MIDIThruModel(jg.JsonGrammarModel):
    def __init__(self):
        super().__init__('MIDIThruModel')
        self.value = None

    def __eq__(self, other):
        result = isinstance(other, MIDIThruModel) and self.value == other.value
        if not result:
            self.modified = True
        return result

    def from_base(self, base_message):
        if base_message.msg_array_data is None or base_message.msg_array_data[0] is None:
            self.value = onoff_default
        else:
            self.value = onoff_type[base_message.msg_array_data[0]]
        name = self.value
        if self.value == onoff_default:
            self.value = None
        return name

    def to_base(self, base_message, _bank_catalog, _midi_channels, _intuitive_bank, _intuitive_preset):
        if self.value is not None and self.value != onoff_default:
            base_message.msg_array_data[0] = onoff_type.index(self.value)


class WaveformSequenceBaseModel(jg.JsonGrammarModel):
    @staticmethod
    def engine_keys():
        return [jg.SwitchDict.make_key('engine', jg.Atom('Engine', int, var='engine'))]

    @staticmethod
    def common_keys():
        return [jg.SwitchDict.make_key('perpetual', jg.Atom('Perpetual', bool, False, var='perpetual')),
                jg.SwitchDict.make_key('number', jg.Atom('Number', int, var='number')),
                jg.SwitchDict.make_key('channel', jg.Atom('Channel', str, '', var='channel'))]

    @staticmethod
    def waveform_keys():
        return [jg.SwitchDict.make_key('reverse_waveform',
                                       jg.Atom('Reverse Waveform', bool, False,
                                               var='reverse_waveform'))]

    @staticmethod
    def midi_clock_keys():
        return [jg.SwitchDict.make_key('note_division',
                                       jg.Enum('Note Division', note_divisions,
                                               note_divisions_default, var='note_division'))]

    @staticmethod
    def no_midi_clock_keys():
        return [jg.SwitchDict.make_key('cps',
                                       jg.Atom('Cycles Per Second', int, var='cpm')),
                jg.SwitchDict.make_key('multiplier',
                                       jg.Atom('Speed Multiplier', int,
                                               var='multiplier'))]

    @staticmethod
    def is_stop(data):
        if data is None or data[1] is None or (data[1] & 0xF0) == 0:
            return True
        return False

    @staticmethod
    def determine_start_type(intuitive_message, data):
        follow_midi_clock = (data[1] & 0x4) != 0
        if intuitive_message.type == 'CC Waveform Generator':
            if follow_midi_clock:
                intuitive_message.type = 'Start CC Waveform Generator'
                intuitive_message.specific_message = StartWaveformModel()
            else:
                intuitive_message.type = 'Start CC Waveform Generator No MIDI Clock'
                intuitive_message.specific_message = StartWaveformNoMIDIClockModel()
        else:
            if follow_midi_clock:
                intuitive_message.type = 'Start CC Sequence Generator'
                intuitive_message.specific_message = StartSequenceModel()
            else:
                intuitive_message.type = 'Start CC Sequence Generator No MIDI Clock'
                intuitive_message.specific_message = StartSequenceNoMIDIClockModel()
        intuitive_message.name = intuitive_message.type + ':'

    @staticmethod
    def determine_stop_type(intuitive_message, data):
        stop_all = data is not None and data[4] is not None and data[4] == 15
        if intuitive_message.type == 'CC Waveform Generator':
            if stop_all:
                intuitive_message.type = 'Stop All CC Waveform Generator'
                intuitive_message.specific_message = StopAllWaveformModel()
            else:
                intuitive_message.type = 'Stop CC Waveform Generator'
                intuitive_message.specific_message = StopWaveformModel()
        else:
            if stop_all:
                intuitive_message.type = 'Stop All CC Sequence Generator'
                intuitive_message.specific_message = StopAllSequenceModel()
            else:
                intuitive_message.type = 'Stop CC Sequence Generator'
                intuitive_message.specific_message = StopSequenceModel()
        intuitive_message.name = intuitive_message.type
        if intuitive_message.specific_message is not None:
            intuitive_message.name += ':'

    def __init__(self):
        super().__init__('WaveformSequenceBaseModel')
        self.engine = None
        self.perpetual = None
        self.note_division = None
        self.cpm = None
        self.multiplier = None
        self.reverse_waveform = None
        self.number = None
        self.channel = None

    def __eq__(self, other):
        result = isinstance(other, WaveformSequenceBaseModel)
        if not result:
            self.modified = True
        return result

    def eq_engine(self, other):
        return self.engine == other.engine

    def eq_common(self, other):
        return self.perpetual == other.perpetual and self.number == other.number and self.channel == other.channel

    def eq_midi_clock(self, other):
        return self.note_division == other.note_division

    def eq_no_midi_clock(self, other):
        return self.cpm == other.cpm and self.multiplier == other.multiplier

    def eq_waveform(self, other):
        return self.reverse_waveform == other.reverse_waveform

    def from_base_engine(self, base_message):
        if base_message.msg_array_data is None:
            self.engine = 0
        else:
            if base_message.msg_array_data[4] is None:
                self.engine = 0
            else:
                self.engine = base_message.msg_array_data[4]
        self.engine += 1
        return str(self.engine)

    def from_base_common(self, base_message, channel, name):
        self.channel = channel
        if base_message.msg_array_data is None:
            self.perpetual = False
            self.number = 0
        else:
            if base_message.msg_array_data[1] is None:
                raise IntuitiveException('unexpected', 'unexpected')
            self.perpetual = base_message.msg_array_data[1] & 0x20 != 0
            if base_message.msg_array_data[0] is None:
                self.number = 0
            else:
                self.number = base_message.msg_array_data[0]
        if self.perpetual:
            name.append('Perpetual')
        else:
            name.append('Once Only')
        if not self.perpetual:
            self.perpetual = None
        name.append(str(self.number))
        name.append(self.channel)

    def from_base_midi_clock(self, base_message, name):
        if base_message.msg_array_data is None or base_message.msg_array_data[2] is None:
            note_division = 0
        else:
            note_division = base_message.msg_array_data[2]
        self.note_division = note_divisions[note_division]
        name.append(self.note_division)
        if self.note_division == note_divisions_default:
            self.note_division = None

    def from_base_no_midi_clock(self, base_message, name):
        if base_message.msg_array_data is None or base_message.msg_array_data[2] is None:
            cpm = 0
        else:
            cpm = base_message.msg_array_data[2]
        self.cpm = cpm + 1
        self.multiplier = 1 << ((base_message.msg_array_data[1] & 0x18) >> 3)
        name.append(str(self.cpm) + ' CPM')
        name.append(str(self.multiplier) + 'x')

    def from_base_waveform(self, base_message, name):
        if base_message.msg_array_data is None or base_message.msg_array_data[3] is None:
            self.reverse_waveform = False
        else:
            self.reverse_waveform = base_message.msg_array_data[3] != 0
        if self.reverse_waveform:
            name.append('Reverse')
        else:
            name.append('No Reverse')
        if not self.reverse_waveform:
            self.reverse_waveform = None

    def to_base_engine(self, base_message):
        if self.engine is not None:
            base_message.msg_array_data[4] = self.engine - 1

    def to_base_common(self, base_message, midi_channels):
        base_message.channel = midi_channels.index(self.channel)
        if base_message.channel == 0:
            base_message.channel = None
        else:
            base_message.channel += 1
        if base_message.msg_array_data[1] is None:
            base_message.msg_array_data[1] = 0
        if self.perpetual:
            base_message.msg_array_data[1] |= 0x20
        if self.number is not None and self.number != 0:
            base_message.msg_array_data[0] = self.number

    def to_base_midi_clock(self, base_message):
        if self.note_division is not None and self.note_division != note_divisions_default:
            base_message.msg_array_data[2] = note_divisions.index(self.note_division)

    def to_base_no_midi_clock(self, base_message):
        if self.cpm is not None and self.cpm != 1:
            base_message.msg_array_data[2] = self.cpm - 1
        if self.multiplier is not None and self.multiplier != 0:
            multiplier = self.multiplier
            val = 0
            while multiplier > 1:
                val += 1
                multiplier >>= 1
            if base_message.msg_array_data[1] is None:
                base_message.msg_array_data[1] = 0
            base_message.msg_array_data[1] |= val << 3

    def to_base_waveform(self, base_message):
        if self.reverse_waveform:
            base_message.msg_array_data[3] = 1


class StopWaveformModel(WaveformSequenceBaseModel):
    @staticmethod
    def get_keys():
        return WaveformSequenceBaseModel.engine_keys()

    def __init__(self):
        super().__init__()

    def __eq__(self, other):
        result = isinstance(other, StopWaveformModel)
        result = result and self.eq_engine(other)
        if not result:
            self.modified = True
        return result

    def from_base(self, base_message):
        name = [self.from_base_engine(base_message)]
        return ':'.join(name)

    def to_base(self, base_message, _bank_catalog, _midi_channels, _intuitive_bank, _intuitive_preset):
        base_message.type = intuitive_message_type.index("CC Waveform Generator")
        self.to_base_engine(base_message)


class StopAllWaveformModel(WaveformSequenceBaseModel):
    def __init__(self):
        super().__init__()

    def __eq__(self, other):
        result = isinstance(other, StopAllWaveformModel)
        if not result:
            self.modified = True
        return result

    def from_base(self, _base_message):
        return ''

    def to_base(self, base_message, _bank_catalog, _midi_channels, _intuitive_bank, _intuitive_preset):
        base_message.type = intuitive_message_type.index("CC Waveform Generator")
        base_message.msg_array_data[4] = 15


class StopSequenceModel(WaveformSequenceBaseModel):
    @staticmethod
    def get_keys():
        return WaveformSequenceBaseModel.engine_keys()

    def __init__(self):
        super().__init__()

    def __eq__(self, other):
        result = isinstance(other, StopSequenceModel)
        result = result and self.eq_engine(other)
        if not result:
            self.modified = True
        return result

    def from_base(self, base_message):
        name = [self.from_base_engine(base_message)]
        return ':'.join(name)

    def to_base(self, base_message, _bank_catalog, _midi_channels, _intuitive_bank, _intuitive_preset):
        base_message.type = intuitive_message_type.index("CC Sequence Generator")
        self.to_base_engine(base_message)


class StopAllSequenceModel(WaveformSequenceBaseModel):
    def __init__(self):
        super().__init__()

    def __eq__(self, other):
        result = isinstance(other, StopAllSequenceModel)
        if not result:
            self.modified = True
        return result

    def from_base(self, _base_message):
        return ''

    def to_base(self, base_message, _bank_catalog, _midi_channels, _intuitive_bank, _intuitive_preset):
        base_message.type = intuitive_message_type.index("CC Sequence Generator")
        base_message.msg_array_data[4] = 15


class StartWaveformModel(WaveformSequenceBaseModel):
    @staticmethod
    def get_keys():
        return (WaveformSequenceBaseModel.engine_keys() + WaveformSequenceBaseModel.common_keys() +
                WaveformSequenceBaseModel.midi_clock_keys() + WaveformSequenceBaseModel.waveform_keys())

    def __init__(self):
        super().__init__()

    def __eq__(self, other):
        result = isinstance(other, StartWaveformModel)
        result = result and self.eq_engine(other)
        result = result and self.eq_common(other)
        result = result and self.eq_midi_clock(other)
        result = result and self.eq_waveform(other)
        if not result:
            self.modified = True
        return result

    def from_base(self, base_message, channel):
        name = []
        self.from_base_common(base_message, channel, name)
        self.from_base_midi_clock(base_message, name)
        self.from_base_waveform(base_message, name)
        name.append(self.from_base_engine(base_message))
        return ':'.join(name)

    def to_base(self, base_message, _bank_catalog, midi_channels, _intuitive_bank, _intuitive_preset):
        base_message.type = intuitive_message_type.index("CC Waveform Generator")
        base_message.msg_array_data[1] = 0x43  # start, don't stop, unknown 2 bits at end
        self.to_base_common(base_message, midi_channels)
        self.to_base_midi_clock(base_message)
        self.to_base_waveform(base_message)
        self.to_base_engine(base_message)


class StartSequenceModel(WaveformSequenceBaseModel):
    @staticmethod
    def get_keys():
        return (WaveformSequenceBaseModel.engine_keys() + WaveformSequenceBaseModel.common_keys() +
                WaveformSequenceBaseModel.midi_clock_keys())

    def __init__(self):
        super().__init__()

    def __eq__(self, other):
        result = isinstance(other, StartSequenceModel)
        result = result and self.eq_engine(other)
        result = result and self.eq_common(other)
        result = result and self.eq_midi_clock(other)
        if not result:
            self.modified = True
        return result

    def from_base(self, base_message, channel):
        name = []
        self.from_base_common(base_message, channel, name)
        self.from_base_midi_clock(base_message, name)
        name.append(self.from_base_engine(base_message))
        return ':'.join(name)

    def to_base(self, base_message, _bank_catalog, midi_channels, _intuitive_bank, _intuitive_preset):
        base_message.type = intuitive_message_type.index("CC Sequence Generator")
        base_message.msg_array_data[1] = 0x43  # start, don't stop, unknown 2 bits at end
        self.to_base_common(base_message, midi_channels)
        self.to_base_midi_clock(base_message)
        self.to_base_engine(base_message)


class StartWaveformNoMIDIClockModel(WaveformSequenceBaseModel):
    @staticmethod
    def get_keys():
        return (WaveformSequenceBaseModel.engine_keys() + WaveformSequenceBaseModel.common_keys() +
                WaveformSequenceBaseModel.no_midi_clock_keys() + WaveformSequenceBaseModel.waveform_keys())

    def __init__(self):
        super().__init__()

    def __eq__(self, other):
        result = isinstance(other, StartWaveformNoMIDIClockModel)
        result = result and self.eq_engine(other)
        result = result and self.eq_common(other)
        result = result and self.eq_no_midi_clock(other)
        result = result and self.eq_waveform(other)
        if not result:
            self.modified = True
        return result

    def from_base(self, base_message, channel):
        name = []
        self.from_base_common(base_message, channel, name)
        self.from_base_waveform(base_message, name)
        self.from_base_no_midi_clock(base_message, name)
        name.append(self.from_base_engine(base_message))
        return ':'.join(name)

    def to_base(self, base_message, _bank_catalog, midi_channels, _intuitive_bank, _intuitive_preset):
        base_message.type = intuitive_message_type.index("CC Waveform Generator")
        base_message.msg_array_data[1] = 0x43  # start, don't stop, unknown 2 bits at end
        self.to_base_common(base_message, midi_channels)
        self.to_base_waveform(base_message)
        self.to_base_no_midi_clock(base_message)
        self.to_base_engine(base_message)


class StartSequenceNoMIDIClockModel(WaveformSequenceBaseModel):
    @staticmethod
    def get_keys():
        return (WaveformSequenceBaseModel.engine_keys() + WaveformSequenceBaseModel.common_keys() +
                WaveformSequenceBaseModel.no_midi_clock_keys())

    def __init__(self):
        super().__init__()

    def __eq__(self, other):
        result = isinstance(other, StartSequenceNoMIDIClockModel)
        result = result and self.eq_engine(other)
        result = result and self.eq_common(other)
        result = result and self.eq_no_midi_clock(other)
        if not result:
            self.modified = True
        return result

    def from_base(self, base_message, channel):
        name = []
        self.from_base_common(base_message, channel, name)
        self.from_base_no_midi_clock(base_message, name)
        name.append(self.from_base_engine(base_message))
        return ':'.join(name)

    def to_base(self, base_message, _bank_catalog, midi_channels, _intuitive_bank, _intuitive_preset):
        base_message.type = intuitive_message_type.index("CC Sequence Generator")
        base_message.msg_array_data[1] = 0x43  # start, don't stop, unknown 2 bits at end
        self.to_base_common(base_message, midi_channels)
        self.to_base_no_midi_clock(base_message)
        self.to_base_engine(base_message)


class EngagePresetModel(jg.JsonGrammarModel):
    def __init__(self):
        super().__init__('EngagePresetModel')
        self.bank = None
        self.preset = None
        self.action = None

    def __eq__(self, other):
        result = isinstance(other, EngagePresetModel) and self.bank == other.bank and self.preset == other.preset
        result = result and self.action == other.action
        if not result:
            self.modified = True
        return result

    def from_base(self, banks, base_message):
        if base_message.msg_array_data is None:
            self.bank = banks[0]
            self.preset = 'A'
            self.action = engage_preset_action_default
        else:
            if base_message.msg_array_data[0] is None:
                self.bank = banks[0]
            else:
                self.bank = banks[base_message.msg_array_data[0]]
            if base_message.msg_array_data[1] is None:
                self.preset = 'A'
            else:
                self.preset = chr(base_message.msg_array_data[1])
            if base_message.msg_array_data[2] is None:
                self.action = preset_message_trigger[0]
            else:
                self.action = preset_message_trigger[base_message.msg_array_data[2]]
        return self.bank + ':' + self.preset + ':' + self.action

    def to_base(self, base_message, bank_catalog, _midi_channels, _intuitive_bank, _intuitive_preset):
        bank_number = bank_catalog[self.bank]
        if bank_number != 0:
            base_message.msg_array_data[0] = bank_number
        if self.preset != 'A':
            base_message.msg_array_data[1] = ord(self.preset)
        if self.action != preset_message_trigger_default:
            base_message.msg_array_data[2] = preset_message_trigger.index(self.action)


class SetToggleModel(jg.JsonGrammarModel):
    preset_mapping = [[0, 0x1],   # 0, A
                      [0, 0x2],   # 1, B
                      [0, 0x4],   # 2, C
                      [0, 0x8],   # 3, D
                      [0, 0x10],  # 4, E
                      [0, 0x20],  # 5, F
                      [0, 0x40],  # 6, G
                      [1, 0x1],   # 7, H
                      [1, 0x2],   # 8, I
                      [1, 0x4],   # 9, J
                      [1, 0x8],   # 10, K
                      [1, 0x10],  # 11, L
                      [1, 0x20],  # 12, M
                      [1, 0x40],  # 13, N
                      [2, 0x1],   # 14, O
                      [2, 0x2],   # 15, P
                      [2, 0x4],   # 16, Q
                      [2, 0x8],   # 17, R
                      [2, 0x10],  # 18, S
                      [2, 0x20],  # 19, T
                      [2, 0x40],  # 20, U
                      [3, 0x1],   # 21, V
                      [3, 0x2],   # 22, W
                      [3, 0x4],   # 23, X
                      ]

    def __init__(self):
        super().__init__('SetToggleModel')
        self.position = None
        self.presets = None

    def __eq__(self, other):
        result = isinstance(other, SetToggleModel) and self.position == other.position and self.presets == other.presets
        if not result:
            self.modified = True
        return result

    # Set Toggle has a toggle position and a set of presets
    # In the base message, the toggle position is stored in the channel (weird),
    # and the presets are bytes 0-3 of the msg_array_data (one bit per preset)
    # The toggle position is
    #    Disengage Toggle: Channel None (0)
    #    Engage Toggle: Channel 2
    #    Toggle: Channel 3
    #    Shift: Channel 4
    #    Shift+: Channel 5
    #    Unshift: Channel 6
    # Because of the weird 0 to 2 jump, the intuitive implementation has "unused" in position 1
    # Presets are stored low to high (preset A is bit 0 of the first byte), and each byte uses 7 bits
    # msg_array_data[0]: A, B, C, D, E, F, G
    # msg_array_data[1]: H, I, J, K, L, M, N
    # msg_array_data[2]: O, P, Q, R, S, T, U
    # msg_array_data[3]: V, W, X
    def from_base(self, base_message, base_bank):
        if base_message.channel is None:
            self.position = set_toggle_default
        else:
            self.position = set_toggle_type[base_message.channel]
        name = self.position + ':'
        if self.position == set_toggle_default:
            self.position = None
        if base_message.msg_array_data is not None:
            self.from_base_presets(base_message, base_bank)
            name += ','.join(self.presets)
        return name

    def from_base_presets(self, base_message, base_bank):
        self.presets = []
        for preset_number, preset_map in enumerate(self.preset_mapping):
            if (base_message.msg_array_data[preset_map[0]] is not None and
                    base_message.msg_array_data[preset_map[0]] & preset_map[1]):
                self.presets.append(base_bank.presets[preset_number].short_name)

    def to_base(self, base_message, _bank_catalog, _midi_channels, intuitive_bank, _intuitive_preset):
        if self.position is not None:
            base_message.channel = set_toggle_type.index(self.position)
        base_message.msg_array_data[0] = 0
        base_message.msg_array_data[1] = 0
        base_message.msg_array_data[2] = 0
        base_message.msg_array_data[3] = 0
        for preset in self.presets:
            preset_number = intuitive_bank.lookup_preset(preset)
            preset_map = self.preset_mapping[preset_number]
            base_message.msg_array_data[preset_map[0]] |= preset_map[1]


class TriggerMessagesModel(jg.JsonGrammarModel):
    def __init__(self):
        super().__init__('TriggerMessagesModel')
        self.preset = None
        self.messages = None
        self.message_numbers = None

    def __eq__(self, other):
        result = isinstance(other, TriggerMessagesModel) and self.preset == other.preset
        result = result and self.messages == other.messages
        if not result:
            self.modified = True
        return result

    def from_base(self, base_message, base_bank):
        preset_number = 0
        if base_message.msg_array_data is not None and base_message.msg_array_data[0] is not None:
            preset_number = base_message.msg_array_data[0]
        self.preset = base_bank.presets[preset_number].short_name
        if base_message.msg_array_data is None:
            self.message_numbers = 0
        else:
            if base_message.msg_array_data[5] is None:
                self.message_numbers = 0
            else:
                self.message_numbers = base_message.msg_array_data[5]
        return self.preset + ':' + str(self.message_numbers)

    def from_base_cleanup(self, presets):
        if self.messages is not None:
            return
        for preset in presets:
            if preset is not None and preset.short_name == self.preset:
                self.messages = []
                message_number = 0
                message_numbers = self.message_numbers
                while message_numbers > 0:
                    if message_numbers & 1:
                        if message_number < len(preset.messages):
                            self.messages.append(preset.messages[message_number].midi_message)
                        else:
                            print("Warning, message " + str(message_number) +
                                  " is not populated in preset. Ignoring in Trigger Messages.")
                    message_number += 1
                    message_numbers >>= 1
                return
        raise IntuitiveException('preset_not_found', 'In cleanup, preset not found')

    def to_base(self, base_message, _bank_catalog, _midi_channels, intuitive_bank, _intuitive_preset):
        preset_number = intuitive_bank.lookup_preset(self.preset)
        if preset_number != 0:
            base_message.msg_array_data[0] = preset_number
        preset = intuitive_bank.presets[preset_number]
        base_message.msg_array_data[5] = 0
        for message in self.messages:
            base_message.msg_array_data[5] |= 1 << preset.lookup_message(message)


class SelectExpMessageModel(jg.JsonGrammarModel):

    message_map = [[4, 0x1],   # message 1
                   [4, 0x2],   # message 2
                   [4, 0x4],   # message 3
                   [4, 0x8],   # message 4
                   [4, 0x10],  # message 5
                   [4, 0x20],  # message 6
                   [3, 0x1],   # message 7
                   [3, 0x2],   # message 8
                   [3, 0x4],   # message 9
                   [3, 0x8],   # message 10
                   [3, 0x10],  # message 11
                   [3, 0x20],  # message 12
                   [3, 0x40],  # message 13
                   [2, 0x1],   # message 14
                   [2, 0x2],   # message 15
                   [2, 0x4],   # message 16
                   [2, 0x8],   # message 17
                   [2, 0x10],  # message 18
                   [2, 0x20],  # message 19
                   [2, 0x40],  # message 20
                   [1, 0x1],   # message 21
                   [1, 0x2],   # message 22
                   [1, 0x4],   # message 23
                   [1, 0x8],   # message 24
                   [1, 0x10],  # message 25
                   [1, 0x20],  # message 26
                   [1, 0x40],  # message 27
                   [0, 0x4],   # message 28
                   [0, 0x8],   # message 29
                   [0, 0x10],  # message 30
                   [0, 0x20],  # message 31
                   [0, 0x40],  # message 32
                   ]

    def __init__(self):
        super().__init__('SelectExpMessageModel')
        self.input = None
        self.messages = None
        self.message_numbers = None

    # eq will not be accurate in the period between from_base and from_base_cleanup, not sure if this is an issue
    def __eq__(self, other):
        result = isinstance(other, SelectExpMessageModel) and self.input == other.input
        result = result and self.messages == other.messages
        if not result:
            self.modified = True
        return result

    # The base message contains an exp (no 1 -4), and up to 32 messages
    # These are stored in msg_array_data places 0 through 4:
    # 0aaa aaxx 0bbb bbbb 0ccc cccc 0ddd dddd 00ee eeee
    # xx is the exp number (0 based, for 1-4)
    # ee eeee is messages number 1 through 6
    # ddd dddd is messages 7 through 13
    # ccc cccc is messages 14 through 20
    # bbb bbbb is messages 21 through 27
    # aaa aa is messages 28 through 32
    def from_base(self, base_message):
        self.message_numbers = []
        if base_message.msg_array_data is None:
            self.input = 0
        else:
            if base_message.msg_array_data[0] is None:
                self.input = 0
            else:
                self.input = base_message.msg_array_data[0] & 0x3
            for message_number, message in enumerate(self.message_map):
                if base_message.msg_array_data[message[0]] is not None:
                    if base_message.msg_array_data[message[0]] & message[1]:
                        self.message_numbers.append(message_number)
        self.input += 1
        input_name = str(self.input)
        if self.input == 1:
            self.input = None
        return input_name + ':' + str(self.message_numbers)

    def from_base_cleanup(self, messages):
        if self.messages is not None:
            return
        self.messages = []
        for message_number in self.message_numbers:
            if message_number < len(messages):
                self.messages.append(messages[message_number].midi_message)
            else:
                print("Warning, message " + str(message_number) +
                      " is not populated in preset. Ignoring in Select Exp Message.")
        if self.messages == []:
            self.messages = None
        return

    def to_base(self, base_message, _bank_catalog, _midi_channels, _intuitive_bank, intuitive_preset):
        base_message.msg_array_data[0] = 0
        base_message.msg_array_data[1] = 0
        base_message.msg_array_data[2] = 0
        base_message.msg_array_data[3] = 0
        base_message.msg_array_data[4] = 0
        if self.input is not None:
            base_message.msg_array_data[0] |= self.input - 1
        if self.messages is not None:
            for message in self.messages:
                message_number = intuitive_preset.lookup_message(message)
                map_entry = self.message_map[message_number]
                base_message.msg_array_data[map_entry[0]] |= map_entry[1]


class LooperModeModel(jg.JsonGrammarModel):
    def __init__(self):
        super().__init__('LooperModeModel')
        self.mode = None
        self.selected_switches = None
        self.switches = None
        self.disable_message = None

    def __eq__(self, other):
        result = isinstance(other, LooperModeModel) and self.mode == other.mode
        result = result and self.selected_switches == other.selected_switches and self.switches == other.switches
        result = result and self.disable_message == other.disable_message
        if not result:
            self.modified = True
        return result

    def from_base(self, base_message):
        if base_message.msg_array_data is None:
            self.mode = looper_mode_default
            self.selected_switches = False
            self.switches = []
            self.disable_message = False
        else:
            if base_message.msg_array_data[0] is None:
                self.mode = looper_mode_default
                self.selected_switches = False
                self.disable_message = False
            else:
                self.mode = looper_mode[base_message.msg_array_data[0] & 3]
                self.selected_switches = (base_message.msg_array_data[0] & 4) != 0
                self.disable_message = (base_message.msg_array_data[0] & 8) != 0
            self.switches = []
            if base_message.msg_array_data[1] is not None:
                switch = 0
                switches = base_message.msg_array_data[1]
                while switches > 0:
                    if switches & 1:
                        self.switches.append(chr(ord('A') + switch))
                    switch += 1
                    switches >>= 1
        name = self.mode + ':'
        if self.mode == looper_mode_default:
            self.mode = None
        if self.selected_switches:
            name += ','.join(self.switches)
        else:
            name += 'all'
            self.selected_switches = None
        if self.disable_message:
            name += ':disableLCD'
        else:
            name += ':enableLCD'
            self.disable_message = None
        if self.switches == []:
            self.switches = None
        return name

    def to_base(self, base_message, _bank_catalog, _midi_channels, _intuitive_bank, _intuitive_preset):
        base_message.msg_array_data[0] = 0
        if self.mode is not None:
            base_message.msg_array_data[0] |= looper_mode.index(self.mode)
        if self.selected_switches is not None and self.selected_switches:
            base_message.msg_array_data[0] |= 4
        if self.disable_message is not None and self.disable_message:
            base_message.msg_array_data[0] |= 8
        if self.switches is not None:
            base_message.msg_array_data[1] = 0
            for switch in self.switches:
                base_message.msg_array_data[1] |= 1 << ord(switch) - ord('A')


class DisengageLooperModeModel(jg.JsonGrammarModel):
    def __init__(self):
        super().__init__('DisengageLooperModeModel')
        self.disable_message = None

    def __eq__(self, other):
        result = isinstance(other, DisengageLooperModeModel) and self.disable_message == other.disable_message
        if not result:
            self.modified = True
        return result

    def from_base(self, base_message):
        if base_message.msg_array_data is None or base_message.msg_array_data[0] is None:
            self.disable_message = False
        else:
            self.disable_message = (base_message.msg_array_data[0] & 8) != 0
        if self.disable_message:
            return "disableLCD"
        else:
            return "enableLCD"

    def to_base(self, base_message, _bank_catalog, _midi_channels, _intuitive_bank, _intuitive_preset):
        base_message.type = intuitive_message_type.index("Looper Mode")
        base_message.msg_array_data[0] = 2
        if self.disable_message is not None and self.disable_message:
            base_message.msg_array_data[0] |= 8


class SysExModel(jg.JsonGrammarModel):
    def __init__(self):
        super().__init__('SysExModel')
        self.data = None

    def __eq__(self, other):
        result = isinstance(other, SysExModel) and self.data == other.data
        if not result:
            self.modified = True
        return result

    def from_base(self, base_message):
        if base_message.msg_array_data is None:
            self.data = None
        else:
            raise IntuitiveException('not_implemented', 'Not Implemented')
        return str(self.data)

    def to_base(self, _base_message, _bank_catalog, _midi_channels, _intuitive_bank, _intuitive_preset):
        if self.data is not None:
            raise IntuitiveException('not_implemented', 'Not Implemented')


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
        if page is None or page == 0:
            page = None
        result.specific_message = BankJumpModel.mk_bank_jump_message(bank, page)
        if message_catalog is not None:
            return message_catalog.add(result)
        return result

    @staticmethod
    def make_toggle_page_message(name, page_up, message_catalog):
        result = IntuitiveMessage()
        result.name = name
        result.type = 'Toggle Page'
        result.specific_message = TogglePageModel().mk_toggle_page_message(page_up)
        return message_catalog.add(result)

    def __init__(self):
        super().__init__('IntuitiveMessage')
        self.name = None
        self.specific_message = None
        self.type = None

    def __eq__(self, other):
        result = isinstance(other, IntuitiveMessage) and self.type == other.type
        result = result and self.specific_message == other.specific_message
        if not result:
            self.modified = True
        return result

    # This creates a name out of the MIDI message parameters
    def from_base(self, base_message, base_bank, message_catalog, banks, midi_channels):

        if base_message.type is not None:
            self.type = intuitive_message_type[base_message.type]
        else:
            raise IntuitiveException('unimplemented', 'Fix me')

        self.name = self.type + ':'
        if self.type in ['PC', 'CC']:
            base_channel = base_message.channel
            channel = midi_channel_from_base(base_channel, midi_channels)
            if self.type == "PC":
                self.specific_message = PCModel()
                self.name += self.specific_message.from_base(channel, base_message)
            elif self.type == 'CC':
                self.specific_message = CCModel()
                self.name += self.specific_message.from_base(channel, base_message)
        elif self.type == 'PC Multichannel':
            self.specific_message = PCMultichannelModel()
            self.name += self.specific_message.from_base(base_message, midi_channels)
        elif self.type == 'Bank Jump':
            self.specific_message = BankJumpModel()
            self.name += self.specific_message.from_base(base_message, banks)
        elif self.type == 'Toggle Page':
            if base_message.msg_array_data[0] == 1 or base_message.msg_array_data[0] == 2:
                self.specific_message = TogglePageModel()
                self.name += self.specific_message.from_base(base_message)
            else:
                self.type = "Page Jump"
                self.name = self.type + ':'
                self.specific_message = PageJumpModel()
                self.name += self.specific_message.from_base(base_message)
        elif self.type == 'Note On' or self.type == 'Note Off':
            if self.type == 'Note On':
                self.specific_message = NoteOnModel()
            else:
                self.specific_message = NoteOffModel()
            channel = midi_channel_from_base(base_message.channel, midi_channels)
            self.name += self.specific_message.from_base(channel, base_message)
        elif self.type == 'Real Time':
            self.specific_message = RealTimeModel()
            self.name += self.specific_message.from_base(base_message)
        elif self.type == 'Preset Rename':
            self.specific_message = PresetRenameModel()
            self.name += self.specific_message.from_base(base_message)
        elif self.type == 'Song Position':
            self.specific_message = SongPositionModel()
            self.name += self.specific_message.from_base(base_message)
        elif self.type == 'MIDI MMC':
            self.specific_message = MIDIMMCModel()
            self.name += self.specific_message.from_base(base_message)
        elif self.type == 'MIDI Clock':
            MIDIClockModel.is_tap_menu(self, base_message.msg_array_data)
            self.name += self.specific_message.from_base(base_message)
        elif self.type == 'MIDI Clock Tap':
            # N0 data, no specific message
            self.name = self.name.replace(':', '')
        elif self.type == 'PC Number Scroll' or self.type == 'CC Value Scroll':
            PCCCNumberValueScrollBaseModel.get_specific_message(self, base_message)
            self.name += self.specific_message.from_base(midi_channels, base_message)
        elif self.type == 'CC Waveform Generator' or self.type == 'CC Sequence Generator':
            if WaveformSequenceBaseModel.is_stop(base_message.msg_array_data):
                WaveformSequenceBaseModel.determine_stop_type(self, base_message.msg_array_data)
                if self.specific_message is not None:
                    self.name += self.specific_message.from_base(base_message)
            else:
                WaveformSequenceBaseModel.determine_start_type(self, base_message.msg_array_data)
                channel = midi_channel_from_base(base_message.channel, midi_channels)
                self.name += self.specific_message.from_base(base_message, channel)
        elif self.type == 'Engage Preset':
            self.specific_message = EngagePresetModel()
            self.name += self.specific_message.from_base(banks, base_message)
        elif self.type == 'Trigger Messages':
            self.specific_message = TriggerMessagesModel()
            self.name += self.specific_message.from_base(base_message, base_bank)
        elif self.type == 'Bank Up':
            self.name = self.name.replace(':', '')
        elif self.type == 'Bank Down':
            self.name = self.name.replace(':', '')
        elif self.type == 'Bank Change Mode':
            self.name = self.name.replace(':', '')
        elif self.type == 'Toggle Preset':
            self.name = self.name.replace(':', '')
        elif self.type == 'Set Toggle':
            self.specific_message = SetToggleModel()
            self.name += self.specific_message.from_base(base_message, base_bank)
        elif self.type == 'Set MIDI Thru':
            self.specific_message = MIDIThruModel()
            self.name += self.specific_message.from_base(base_message)
        elif self.type == 'Select Exp Message':
            self.specific_message = SelectExpMessageModel()
            self.name += self.specific_message.from_base(base_message)
        elif self.type == 'Looper Mode':
            if base_message.msg_array_data is None or base_message.msg_array_data[0] is None:
                self.specific_message = LooperModeModel()
            else:
                if base_message.msg_array_data[0] & 3 == 2:
                    self.type = 'Disengage Looper Mode'
                    self.name = self.type + ':'
                    self.specific_message = DisengageLooperModeModel()
                else:
                    self.specific_message = LooperModeModel()
            self.name += self.specific_message.from_base(base_message)
        elif self.type == 'Delay':
            self.specific_message = DelayModel()
            self.name += self.specific_message.from_base(base_message)
        elif self.type == 'Relay Switching':
            self.specific_message = RelaySwitchingModel()
            self.name += self.specific_message.from_base(base_message)
        elif self.type == 'SysEx':
            self.specific_message = SysExModel()
            self.name += self.specific_message.from_base(base_message)
        elif self.type == 'Utility':
            utility_type = utility_message_type[base_message.msg_array_data[0]]
            if utility_type == utility_message_type[6]:
                # Manage preset scroll
                subtype = utility_message_preset_scroll_type[base_message.msg_array_data[1]]
                if subtype == utility_message_preset_scroll_type[4]:
                    self.type = "Preset Scroll Message Count"
                    self.name = self.type + ':'
                    self.specific_message = PresetScrollMessageCountModel()
                    self.name += self.specific_message.from_base(base_message)
                else:
                    raise IntuitiveException('Not implemented')
            else:
                raise IntuitiveException('Not implemented')
        else:
            raise IntuitiveException('unrecognized', 'Invalid message type: ' + self.type)

        return message_catalog.add(self)

    # Add the MIDI message directly to the base message
    def to_base(self, base_message, bank_catalog, midi_channels, intuitive_bank, intuitive_preset):
        base_message.type = intuitive_message_type.index(self.type)
        base_message.msg_array_data = [None] * 18
        if self.specific_message is not None:
            self.specific_message.to_base(base_message, bank_catalog, midi_channels, intuitive_bank, intuitive_preset)

        # Canonicalize the base_message
        # Trigger
        if base_message.trigger == 0:
            base_message.trigger = None
        # msg_array_data: replace 0 elements with None, and truncate to the first non-None element (from the end)
        empty = True
        for pos, elem in enumerate(base_message.msg_array_data):
            if elem == 0:
                base_message.msg_array_data[pos] = None
            elif elem is not None:
                empty = False
        if empty:
            base_message.msg_array_data = None

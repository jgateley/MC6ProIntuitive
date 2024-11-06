import datetime

import grammar as jg

# The models for Morningstar controller backup files
# It may apply to other morningstar controllers (besides the MC6Prop), but hasn't been tested with them.


# Get a byte out of the data array, handling none appropriately, and masking if desired
def msg_array_data_byte(msg_array_data, byte, mask=None):
    if msg_array_data is None:
        val = 0
    elif msg_array_data[byte] is None:
        val = 0
    else:
        val = msg_array_data[byte]
    if mask is None:
        return val
    return val & mask


# Model object for MIDI messages
class MidiMessage(jg.GrammarModel):
    def __init__(self):
        super().__init__('MidiMessage')
        self.msg_array_data = None
        self.channel = None
        self.type = None
        self.trigger = None
        self.toggle_state = None

    # compare one byte with another, handling none, and masking if desired
    def eq_helper(self, other, pos, mask=None):
        self_byte = msg_array_data_byte(self.msg_array_data, pos, mask)
        other_byte = msg_array_data_byte(other.msg_array_data, pos, mask)
        return self_byte == other_byte

    def __eq__(self, other):
        result = (isinstance(other, MidiMessage) and
                  self.type == other.type and
                  self.channel == other.channel and
                  self.trigger == other.trigger and self.toggle_state == other.toggle_state)
        if self.type in [1, 2, 13, 14, 15]:
            if self.msg_array_data is None:
                if other.msg_array_data is not None:
                    result = result and other.msg_array_data[0] is None and other.msg_array_data[1] is None
            elif other.msg_array_data is None:
                if self.msg_array_data is not None:
                    result = result and self.msg_array_data[0] is None and self.msg_array_data[1] is None
            else:
                result = result and self.msg_array_data[0:2] == other.msg_array_data[0:2]
        elif self.type == 7:
            # Message type 7 has some combos that don't make sense, where the MIDI clock is used but BPM is set
            result = result and self.eq_helper(other, 0)
            result = result and self.eq_helper(other, 2, 0b11)
            if msg_array_data_byte(self.msg_array_data, 2, 0b10):
                result = result and self.eq_helper(other, 1) and self.eq_helper(other, 2, 0b1100)
        elif self.type == 42:
            # 42 Trigger Messages can lose messages if they don't exist in the source
            result = result and self.eq_helper(other, 0) and self.eq_helper(other, 1)
            result = result and self.eq_helper(other, 2) and self.eq_helper(other, 3)
            result = result and self.eq_helper(other, 4)
            self_messages = msg_array_data_byte(self.msg_array_data, 5)
            other_messages = msg_array_data_byte(other.msg_array_data, 5)
            while self_messages > 0 and other_messages > 0:
                if not other_messages & 1:
                    result = result and not self_messages & 1
                self_messages >>= 1
                other_messages >>= 1
            result = result and self_messages == 0
        elif self.type in [26, 31]:
            result = result and self.eq_helper(other, 0)
            result = result and self.eq_helper(other, 1, 0xf8) and self.eq_helper(other, 2)
            result = result and self.eq_helper(other, 3) and self.eq_helper(other, 4)
        elif self.type in [3, 4, 5, 6, 10, 11, 12, 16, 17, 18, 22, 23, 24, 25, 26, 27, 32, 33, 34, 36, 40, 41, 44]:
            result = result and self.msg_array_data == other.msg_array_data
        else:
            raise jg.GrammarException('not implemented')
        # Debugging: set a breakpoint on the self.modified line to discovery where two items differ
        if not result:
            self.modified = True
        return result


# Model for a Preset
class Preset(jg.GrammarModel):
    def __init__(self):
        super().__init__('Preset')
        self.short_name = None
        self.toggle_name = None
        self.long_name = None
        self.name_color = None
        self.name_toggle_color = None
        self.shifted_name_color = None
        self.background_color = None
        self.background_toggle_color = None
        self.strip_color = None
        self.strip_toggle_color = None
        self.to_toggle = None
        self.toggle_group = None
        self.to_msg_scroll = None
        self.messages = None

    def __eq__(self, other):
        result = (isinstance(other, Preset) and
                  self.short_name == other.short_name and
                  self.toggle_name == other.toggle_name and
                  self.long_name == other.long_name and
                  self.name_color == other.name_color and
                  self.shifted_name_color == other.shifted_name_color and
                  self.name_toggle_color == other.name_toggle_color and
                  self.background_color == other.background_color and
                  self.background_toggle_color == other.background_toggle_color and
                  self.strip_color == other.strip_color and
                  self.strip_toggle_color == other.strip_toggle_color and
                  self.to_toggle == other.to_toggle and
                  self.toggle_group == other.toggle_group and
                  self.to_msg_scroll == other.to_msg_scroll and
                  self.messages == other.messages)
        # Debugging: set a breakpoint on the self.modified line to discovery where two items differ
        if not result:
            self.modified = True
        return result

    def set_message(self, message, pos):
        if self.messages is None:
            self.messages = [None] * 32
        self.messages[pos] = message


# Model for a Bank
class Bank(jg.GrammarModel):
    def __init__(self):
        super().__init__('Bank')
        self.name = None
        self.description = None
        self.short_name = None
        self.text_color = None
        self.background_color = None
        self.to_display = None
        self.clear_toggle = None
        self.messages = None
        self.presets = None
        self.exp_presets = None

    def __eq__(self, other):
        result = (isinstance(other, Bank) and
                  self.name == other.name and
                  self.description == other.description and
                  self.short_name == other.short_name and
                  self.text_color == other.text_color and
                  self.background_color == other.background_color and
                  self.to_display == other.to_display and
                  self.clear_toggle == other.clear_toggle and
                  self.messages == other.messages and
                  self.presets == other.presets and
                  self.exp_presets == other.exp_presets)
        # Debugging: set a breakpoint on the self.modified line to discovery where two items differ
        if not result:
            self.modified = True
        return result

    def set_preset(self, preset, pos):
        if self.presets is None:
            self.presets = [None] * 24
        self.presets[pos] = preset

    def set_exp_preset(self, preset, pos):
        if self.exp_presets is None:
            self.exp_presets = [None] * 4
        self.exp_presets[pos] = preset

    def set_message(self, message, pos):
        if self.messages is None:
            self.messages = [None] * 32
        self.messages[pos] = message


# Model for a MIDI Channel Name mapping
class MidiChannel(jg.GrammarModel):
    def __init__(self):
        super().__init__('MidiChannel')
        self.name = None

    def __eq__(self, other):
        result = self.name == other.name
        # Debugging: set a breakpoint on the self.modified line to discovery where two items differ
        if not result:
            self.modified = True
        return result


# Model for a Bank Arrangement Item
class BankArrangementItem(jg.GrammarModel):
    def __init__(self):
        super().__init__('BankArrangementItem')
        self.name = None

    def __eq__(self, other):
        result = self.name == other.name
        # Debugging: set a breakpoint on the self.modified line to discovery where two items differ
        if not result:
            self.modified = True
        return result


# Model for the entire backup/config file
class Backup(jg.GrammarModel):
    def __init__(self):
        super().__init__('Backup')
        self.hash = None
        self.download_date = None
        self.banks = None
        # Midi Channels
        self.midi_channels = None
        # Bank Arrangement
        self.bank_arrangement = None
        # General Configuration
        self.midi_channel = None

    def __eq__(self, other):
        if self.bank_arrangement is None or other.bank_arrangement is None:
            result = True
        else:
            result = self.bank_arrangement == other.bank_arrangement
        if self.midi_channels is None or other.midi_channels is None:
            result = True
        else:
            result = result and self.midi_channels == other.midi_channels
        result = (result and self.banks == other.banks and
                  self.midi_channel == other.midi_channel)
        # Debugging: set a breakpoint on the self.modified line to discovery where two items differ
        if not result:
            self.modified = True
        return result

    def midi_channels_from_list(self, midi_channels):
        self.midi_channels = midi_channels

    def set_bank(self, bank, pos):
        if self.banks is None:
            self.banks = [None] * 128
        self.banks[pos] = bank

    def set_bank_arrangement(self, bank_arrangement, pos):
        if pos >= 127:
            return
        if self.bank_arrangement is None:
            self.bank_arrangement = [None] * 127
        self.bank_arrangement[pos] = bank_arrangement

import datetime

import json_grammar as jg


# The JSON grammar and models for MC6Pro
# It may apply to other morningstar controllers, but hasn't been tested with them.
# It is a complete grammar: portions that are not implemented are constants, and
# if a config includes one of these unimplemented features, it will trigger a
# grammar error

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
class MidiMessage(jg.JsonGrammarModel):
    def __init__(self):
        super().__init__('MidiMessage')
        self.msg_array_data = None
        self.channel = None
        self.type = None
        self.trigger = None
        self.toggle_group = None

    # compare one byte with another, handling none, and masking if desired
    def eq_helper(self, other, pos, mask=None):
        self_byte = msg_array_data_byte(self.msg_array_data, pos, mask)
        other_byte = msg_array_data_byte(other.msg_array_data, pos, mask)
        return self_byte == other_byte

    def __eq__(self, other):
        result = (isinstance(other, MidiMessage) and
                  self.type == other.type and
                  self.channel == other.channel and
                  self.trigger == other.trigger and self.toggle_group == other.toggle_group)
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
            raise jg.JsonGrammarException('not implemented')
        # Debugging: set a breakpoint on the self.modified line to discovery where two items differ
        if not result:
            self.modified = True
        return result


# Model for a Preset
class Preset(jg.JsonGrammarModel):
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
class Bank(jg.JsonGrammarModel):
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
class MidiChannel(jg.JsonGrammarModel):
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
class BankArrangementItem(jg.JsonGrammarModel):
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
class MC6Pro(jg.JsonGrammarModel):
    def __init__(self):
        super().__init__('MC6Pro')
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
        result = (result and self.banks == other.banks and
                  self.midi_channels == other.midi_channels and
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


# The MIDI messages received from the MC6Pro sometimes have garbage data in the unused bytes
# This is a first pass at cleaning them up
# This gets rid of messages that are type None, but the garbage data prevents the entire message from being None
def midi_message_cleanup(message, _ctxt, _lp):
    if message is not None:
        if message.type is None:
            return None
    return message


msg_array_schema = \
    jg.Dict('Message Array',
            [jg.Dict.make_key('data',
                              jg.List('Data List', 18, jg.Atom('Data', int, 0), var='msg_array_data')),
             jg.Dict.make_key('m', jg.Atom('Message Number', int, value=jg.identity)),
             # c is channel
             jg.Dict.make_key('c', jg.Atom('Channel', int, 1, var='channel')),
             # t is the message type (CC or PC)
             jg.Dict.make_key('t', jg.Atom('Type', int, 0, var='type')),
             # a is the trigger
             jg.Dict.make_key('a', jg.Atom('Trigger', int, 0, var='trigger')),
             # tg is toggle group
             jg.Dict.make_key('tg', jg.Atom('Toggle Group', int, 2, var='toggle_group')),
             jg.Dict.make_key('mi', jg.Atom('mi', str, value=''))],
            model=MidiMessage, cleanup=midi_message_cleanup)


def mk_preset_array_schema(is_exp):
    return jg.Dict('Preset Array',
                   [jg.Dict.make_key('presetNum', jg.identity_atom),
                    jg.Dict.make_key('bankNum', jg.identity2_atom),
                    jg.Dict.make_key('isExp', is_exp),
                    jg.Dict.make_key('shortName', jg.Atom('Short Name', str, 'EMPTY', var='short_name')),
                    jg.Dict.make_key('toggleName', jg.Atom('Toggle Name', str, '', var='toggle_name')),
                    jg.Dict.make_key('longName', jg.Atom('Long Name', str, '', var='long_name')),
                    jg.Dict.make_key('shiftName', jg.empty_atom),
                    jg.Dict.make_key('toToggle', jg.Atom('To Toggle', bool, False, var='to_toggle')),
                    jg.Dict.make_key('toBlink', jg.false_atom),
                    jg.Dict.make_key('toMsgScroll', jg.Atom('Message Scroll', bool, False, var='to_msg_scroll')),
                    jg.Dict.make_key('toggleGroup', jg.Atom('Toggle Group', int, 0, var='toggle_group')),
                    # the led is the strip at the bottom (top?) of the window
                    jg.Dict.make_key('ledColor', jg.Atom('Strip Color', int, 0, var='strip_color')),
                    jg.Dict.make_key('ledToggleColor', jg.Atom('Strip Toggle Color', int, 0,
                                                               var='strip_toggle_color')),
                    jg.Dict.make_key('ledShiftColor', jg.zero_atom),
                    jg.Dict.make_key('nameColor', jg.Atom('Name Color', int, 7, var='name_color')),
                    jg.Dict.make_key('nameToggleColor', jg.Atom('Name Toggle Color', int, 7,
                                                                var='name_toggle_color')),
                    jg.Dict.make_key('nameShiftColor', jg.Atom('Shifted Name Color', int, 7, var='shifted_name_color')),
                    jg.Dict.make_key('backgroundColor', jg.Atom('Background Color', int, 0,
                                                                var='background_color')),
                    jg.Dict.make_key('toggleBackgroundColor', jg.Atom('Background toggle Color', int, 0,
                                                                      var='background_toggle_color')),
                    jg.Dict.make_key('shiftBackgroundColor', jg.zero_atom),
                    jg.Dict.make_key('msgArray', jg.List('Message List', 32, msg_array_schema,
                                                         var='messages'))],
                   model=Preset)


preset_array_schema = mk_preset_array_schema(jg.false_atom)
exp_preset_array_schema = mk_preset_array_schema(jg.true_atom)

bank_array_schema = \
    jg.Dict(
        'bankArray',
        [jg.Dict.make_key('bankNumber', jg.identity_atom),
         jg.Dict.make_key('bankName',
                          jg.Atom('Bank Name', str, '', var='name')),
         jg.Dict.make_key('bankClearToggle',
                          jg.Atom('Bank Clear Toggle', bool, False, var='clear_toggle')),
         jg.Dict.make_key('bankMsgArray',
                          jg.List('Bank Message List', 32, msg_array_schema, var='messages')),
         jg.Dict.make_key('presetArray',
                          jg.List('Bank Preset List', 24, preset_array_schema, var='presets')),
         jg.Dict.make_key('expPresetArray',
                          jg.List('Bank Expression Preset List', 4, exp_preset_array_schema, var='exp_presets')),
         jg.Dict.make_key('bankDescription',
                          jg.Atom('Bank Description', str, '', var='description')),
         jg.Dict.make_key('toDisplay',
                          jg.Atom('To Display', bool, False, var='to_display')),
         jg.Dict.make_key('backgroundColor',
                          jg.Atom('Background Color', int, 127, var='background_color')),
         jg.Dict.make_key('textColor',
                          jg.Atom('Text Color', int, 127, var='text_color')),
         jg.Dict.make_key('isColorEnabled', jg.true_atom)],
        model=Bank)

omniport_schema = \
    jg.Dict(
        'omniport',
        [jg.Dict.make_key('type', jg.Atom('Type', str, value='omniport_input')),
         jg.Dict.make_key(
             'data',
             jg.Dict(
                 'omniport_data',
                 [jg.Dict.make_key('portNum', jg.identity_atom),
                  jg.Dict.make_key('type', jg.Atom('Type', int, value=1)),
                  jg.Dict.make_key('fixedSwTip', jg.zero_atom),
                  jg.Dict.make_key('fixedSwRing', jg.zero_atom),
                  jg.Dict.make_key('fixedSwTipRing', jg.zero_atom),
                  jg.Dict.make_key('td1', jg.zero_atom),
                  jg.Dict.make_key('td2', jg.zero_atom),
                  jg.Dict.make_key('rd1', jg.zero_atom),
                  jg.Dict.make_key('rd2', jg.zero_atom),
                  jg.Dict.make_key('trd1', jg.zero_atom),
                  jg.Dict.make_key('trd2', jg.zero_atom)]))])

omniports_schema = \
    jg.Dict(
        'omniports',
        [jg.Dict.make_key('type', jg.Atom('Type', str, value='omniport_all')),
         jg.Dict.make_key('data', jg.List('Data List', 4, omniport_schema))])

usb_host_matrix_schema = \
    jg.Dict('usbHost',
            [jg.Dict.make_key('din5', jg.false_atom),
             jg.Dict.make_key('mm35', jg.false_atom),
             jg.Dict.make_key('omniport', jg.false_atom),
             jg.Dict.make_key('usbDevice', jg.false_atom)])

usb_device_matrix_schema = \
    jg.Dict('usbDevice',
            [jg.Dict.make_key('din5', jg.false_atom),
             jg.Dict.make_key('mm35', jg.false_atom),
             jg.Dict.make_key('omniport', jg.false_atom),
             jg.Dict.make_key('usbHost', jg.false_atom)])

din5_matrix_schema = \
    jg.Dict('din5',
            [jg.Dict.make_key('din5', jg.false_atom),
             jg.Dict.make_key('mm35', jg.false_atom),
             jg.Dict.make_key('omniport', jg.false_atom),
             jg.Dict.make_key('usbDevice', jg.false_atom),
             jg.Dict.make_key('usbHost', jg.false_atom)])

mm35_device_matrix_schema = \
    jg.Dict('mm35',
            [jg.Dict.make_key('din5', jg.false_atom),
             jg.Dict.make_key('mm35', jg.false_atom),
             jg.Dict.make_key('omniport', jg.false_atom),
             jg.Dict.make_key('usbDevice', jg.false_atom),
             jg.Dict.make_key('usbHost', jg.false_atom)])

midi_thru_matrix_schema = \
    jg.Dict(
        'midi_thru_matrix',
        [jg.Dict.make_key('type', jg.Atom('Type', str, value='midiThruMatrix')),
         jg.Dict.make_key('data',
                          jg.Dict('midi_thru_matrix_data',
                                  [jg.Dict.make_key('usbHost', usb_host_matrix_schema),
                                   jg.Dict.make_key('usbDevice', usb_device_matrix_schema),
                                   jg.Dict.make_key('din5', din5_matrix_schema),
                                   jg.Dict.make_key('mm35', mm35_device_matrix_schema)]))])


# Midi clock only uses 11 bits, but often defaults to 12 bits set
# This takes care of that difference
def midi_clock_output_ports(elem, _ctxt, _lp):
    if isinstance(elem, int):
        if elem & 2047 == 2047:
            return elem
    return 4095


general_configuration_schema = \
    jg.Dict(
        'general_configurations',
        [jg.Dict.make_key('type', jg.Atom('Type', str, value='general_configurations')),
         jg.Dict.make_key(
             'data',
             jg.Dict(
                 'general_configurations_data',
                 [jg.Dict.make_key('dualLock', jg.false_atom),
                  jg.Dict.make_key('midiClockPersist', jg.false_atom),
                  jg.Dict.make_key('lcdAlign', jg.true_atom),
                  jg.Dict.make_key('midiThru', jg.false_atom),
                  jg.Dict.make_key('ignoreMidiClock', jg.false_atom),
                  jg.Dict.make_key('crossMidiThru', jg.false_atom),
                  jg.Dict.make_key('savePresetToggle', jg.false_atom),
                  jg.Dict.make_key('midiChannel', jg.Atom('MIDI Channel', int, 0, var='midi_channel')),
                  jg.Dict.make_key('switchSensitivity', jg.Atom('Switch Sensitivity', int, value=2)),
                  jg.Dict.make_key('bankChangeDelayTime', jg.zero_atom),
                  jg.Dict.make_key('bankChangeDisplayTime', jg.Atom('Bank Change Display Time', int, value=60)),
                  jg.Dict.make_key('longPressTime', jg.Atom('Long Press Time', int, value=12)),
                  jg.Dict.make_key('loadLastBankOnStartup', jg.false_atom),
                  jg.Dict.make_key('numMidiCable', jg.Atom('Num Midi Cable', int, value=1)),
                  jg.Dict.make_key('midiSendDelay', jg.zero_atom),
                  jg.Dict.make_key('presetMaxFontSize', jg.Atom('Preset Max Font Size', int, value=3)),
                  jg.Dict.make_key('showPresetLabels', jg.false_atom),
                  jg.Dict.make_key('midiThruMatrix', midi_thru_matrix_schema),
                  jg.Dict.make_key('screenSaverTime', jg.zero_atom),
                  jg.Dict.make_key('midiClockOutputPorts', jg.Atom('MIDI Clock Output Ports', int,
                                                                   value=midi_clock_output_ports)),
                  jg.Dict.make_key('rpA', jg.zero_atom),
                  jg.Dict.make_key('rpB', jg.zero_atom)]))])

waveform_engine_schema = \
    jg.Dict(
        'waveform_engine',
        [jg.Dict.make_key('type', jg.Atom('Type', str, value='waveform_engine')),
         jg.Dict.make_key(
             'data',
             jg.Dict(
                 'waveform_engine_data',
                 [jg.Dict.make_key('max', jg.Atom('Max', int, value=127)),
                  jg.Dict.make_key('min', jg.zero_atom),
                  jg.Dict.make_key('num', jg.identity_atom),
                  jg.Dict.make_key('type', jg.zero_atom)]))])

waveform_engines_schema = \
    jg.Dict(
        'waveform_engines',
        [jg.Dict.make_key('type', jg.Atom('Type', str, value='waveform_engines')),
         jg.Dict.make_key('data', jg.List('Data List', 8, waveform_engine_schema))])


# Some slight randomness in the backup file
def sequencer_engine_len_hack(elem, _ctxt, _lp):
    if isinstance(elem, int):
        if elem == 0 or elem == 1:
            return elem
    return 0


# Some more than slight randomness in the backup file
def sequencer_engine_arr_hack(elem, _ctxt, _lp):
    if isinstance(elem, int):
        if 0 <= elem <= 127:
            return elem
    return 0


sequencer_engine_schema = \
    jg.Dict(
        'sequencer_engine',
        [jg.Dict.make_key('type', jg.Atom('Type', str, value='sequencer_engine')),
         jg.Dict.make_key(
             'data',
             jg.Dict(
                 'sequencer_engine_data',
                 [jg.Dict.make_key('engineNum',
                                   jg.identity_atom),
                  jg.Dict.make_key('len', jg.Atom('Length', int, value=sequencer_engine_len_hack)),
                  jg.Dict.make_key(
                      'arr',
                      jg.List('Data List', 16, jg.Atom('Data Item', int, value=sequencer_engine_arr_hack)))]))])

sequencer_engines_schema = \
    jg.Dict(
        'sequencer_engines',
        [jg.Dict.make_key('type', jg.Atom('Type', str, value='sequencer_engines')),
         jg.Dict.make_key('data', jg.List('Data List', 8, sequencer_engine_schema))])

scroll_counter_schema = \
    jg.Dict(
        'scroll_counter',
        [jg.Dict.make_key('type', jg.Atom('Type', str, value='scroll_counter')),
         jg.Dict.make_key(
             'data',
             jg.Dict(
                 'scroll_counter_data',
                 [jg.Dict.make_key('index', jg.identity_atom),
                  jg.Dict.make_key('min', jg.zero_atom),
                  jg.Dict.make_key('max', jg.Atom('Max', int, value=127)),
                  jg.Dict.make_key('start', jg.zero_atom)]))])

scroll_counters_schema = \
    jg.Dict(
        'scroll_counters',
        [jg.Dict.make_key('type', jg.Atom('Type', str, value='scroll_counters')),
         jg.Dict.make_key(
             'data', jg.List('Data List', 16, scroll_counter_schema))])

midi_channel_schema = \
    jg.Dict(
        'midi_channel',
        [jg.Dict.make_key('type', jg.Atom('Type', str, value='midi_channel')),
         jg.Dict.make_key(
             'data',
             jg.Dict(
                 'midi_channel_data',
                 [jg.Dict.make_key('name', jg.Atom('Name', str, '', var='name')),
                  jg.Dict.make_key('channel', jg.Atom('Channel', int, value=jg.identity_plus_1)),
                  jg.Dict.make_key('sendToPort', jg.Atom('Send To Port', int, value=2047)),
                  jg.Dict.make_key('remap', jg.zero_atom)]))],
        model=MidiChannel)

midi_channels_schema = \
    jg.Dict(
        'midi_channels',
        [jg.Dict.make_key('type', jg.Atom('Type', str, value='midi_channels')),
         jg.Dict.make_key(
             'data',
             jg.List('Data List', 16, midi_channel_schema, var='midi_channels'))])

bank_arrangement_item_schema = \
    jg.Dict(
        'bank_arrangement',
        [jg.Dict.make_key('type', jg.Atom('Type', str, value='bank_arrangement')),
         jg.Dict.make_key(
             'data',
             jg.Dict(
                 'bank_arrangement_data',
                 [jg.Dict.make_key('bankNum', jg.identity_atom),
                  jg.Dict.make_key('bankName', jg.Atom('Bank Name', str, '', var='name'))]))],
        model=BankArrangementItem)

bank_arrangement_schema = \
    jg.Dict(
        'bank_arrangements',
        [jg.Dict.make_key('type', jg.Atom('Type', str, value='bank_arrangement')),
         jg.Dict.make_key('isActive', jg.false_atom),
         jg.Dict.make_key('numBanksActive', jg.zero_atom),
         jg.Dict.make_key('data', jg.List('Data List', 127, bank_arrangement_item_schema, var='bank_arrangement'))])

midi_event_schema = \
    jg.Dict(
        'midi_event',
        [jg.Dict.make_key('type', jg.Atom('Type', str, value='midi_event')),
         jg.Dict.make_key(
             'data',
             jg.Dict(
                 'midi_event_data',
                 [jg.Dict.make_key('typeFrom', jg.zero_atom),
                  jg.Dict.make_key('typeTo', jg.zero_atom),
                  jg.Dict.make_key('numberFrom', jg.zero_atom),
                  jg.Dict.make_key('numberTo', jg.zero_atom),
                  jg.Dict.make_key('channelFrom', jg.zero_atom),
                  jg.Dict.make_key('channelTo', jg.zero_atom),
                  jg.Dict.make_key('valueFrom', jg.zero_atom),
                  jg.Dict.make_key('valueTo', jg.zero_atom),
                  jg.Dict.make_key('toSetOutgoingValue', jg.false_atom),
                  jg.Dict.make_key('toMapInputOutput', jg.false_atom),
                  jg.Dict.make_key('toMapValue', jg.false_atom)]))])

midi_events_schema = \
    jg.Dict(
        'midi_events',
        [jg.Dict.make_key('type', jg.Atom('Type', str, value='midi_events')),
         jg.Dict.make_key('data', jg.List('Data List', 16, midi_event_schema))])

resistor_ladder_aux_data_schema = \
    jg.Dict(
        'resistor_ladder_aux_data',
        [jg.Dict.make_key('type', jg.Atom('Type', str, value='resistor_ladder_aux_switch')),
         jg.Dict.make_key('data', jg.Dict('resistor_switch',
                                          [jg.Dict.make_key('switchNumber', jg.identity_atom),
                                           jg.Dict.make_key('triggerValue', jg.zero_atom),
                                           jg.Dict.make_key('f1', jg.zero_atom),
                                           jg.Dict.make_key('f2', jg.zero_atom)]))]
    )

resistor_ladder_aux_schema = \
    jg.Dict('resistor_ladder_aux',
            [jg.Dict.make_key('type', jg.Atom('Type', str, value='resistor_ladder_aux_switch_all')),
             jg.Dict.make_key('data', jg.List('Data List', 16, resistor_ladder_aux_data_schema))])

controller_settings_schema = \
    jg.Dict(
        'controller_settings',
        [jg.Dict.make_key('type', jg.Atom('Type', str, value='controller_settings_all')),
         jg.Dict.make_key(
             'data',
             jg.Dict('controller_settings_data',
                     [jg.Dict.make_key('omniports', omniports_schema),
                      jg.Dict.make_key('controller_settings', general_configuration_schema),
                      jg.Dict.make_key('waveform_engines', waveform_engines_schema),
                      jg.Dict.make_key('sequencer_engines', sequencer_engines_schema),
                      jg.Dict.make_key('scroll_counters', scroll_counters_schema),
                      jg.Dict.make_key('midi_channels', midi_channels_schema),
                      jg.Dict.make_key('bank_arrangement', bank_arrangement_schema),
                      jg.Dict.make_key('midi_events', midi_events_schema),
                      jg.Dict.make_key('resistor_ladder_aux', resistor_ladder_aux_schema)]))])


def download_date(_elem, _ctxt, _lp):
    return datetime.datetime.now().isoformat()


mc6pro_schema = \
    jg.Dict(
        'mc6pro',
        [jg.Dict.make_key("schemaVersion", jg.Atom('Schema Version', int, value=1)),
         jg.Dict.make_key("dumpType", jg.Atom('Dump Type', str, value='allBanks')),
         jg.Dict.make_key("deviceModel", jg.Atom('Device Model', int, value=6)),
         jg.Dict.make_key("downloadDate", jg.Atom('Download Date', str, download_date, var='download_date')),
         jg.Dict.make_key("hash", jg.Atom('Hash', int, 0, var='hash')),
         jg.Dict.make_key("description", jg.empty_atom),
         jg.Dict.make_key(
             "data",
             jg.Dict('data',
                     [jg.Dict.make_key('bankArray',
                                       jg.List('Bank List', 128, bank_array_schema, var='banks')),
                      jg.Dict.make_key('controller_settings', controller_settings_schema, required=False)]))],
        model=MC6Pro)

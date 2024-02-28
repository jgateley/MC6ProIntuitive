import datetime

import json_grammar as jg


# The JSON grammar and models for MC6Pro
# It may apply to other morningstar controllers, but hasn't been tested with them
# It is a complete grammar


# Model object for MIDI messages
class MidiMessage(jg.JsonGrammarModel):
    def __init__(self):
        super().__init__()
        self.msg_array_data = None
        self.channel = None
        self.type = None
        self.trigger = None
        self.toggle_group = None

    def __eq__(self, other):
        result = (isinstance(other, MidiMessage) and
                  self.msg_array_data == other.msg_array_data and
                  self.channel == other.channel and self.type == other.type and
                  self.trigger == other.trigger and self.toggle_group == other.toggle_group)
        # Debugging: set a breakpoint on the self.modified line to discovery where two items differ
        if not result:
            self.modified = True
        return result


# Model for a Preset
class Preset(jg.JsonGrammarModel):
    def __init__(self):
        super().__init__()
        self.short_name = None
        self.toggle_name = None
        self.long_name = None
        self.name_color = None
        self.name_toggle_color = None
        self.background_color = None
        self.background_toggle_color = None
        self.strip_color = None
        self.strip_toggle_color = None
        self.to_toggle = None
        self.messages = None

    def __eq__(self, other):
        result = (isinstance(other, Preset) and
                  self.short_name == other.short_name and
                  self.toggle_name == other.toggle_name and
                  self.long_name == other.long_name and
                  self.name_color == other.name_color and
                  self.name_toggle_color == other.name_toggle_color and
                  self.background_color == other.background_color and
                  self.background_toggle_color == other.background_toggle_color and
                  self.strip_color == other.strip_color and
                  self.strip_toggle_color == other.strip_toggle_color and
                  self.to_toggle == other.to_toggle and
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
        super().__init__()
        self.name = None
        self.description = None
        self.short_name = None
        self.text_color = None
        self.background_color = None
        self.to_display = None
        self.clear_toggle = None
        self.presets = None

    def __eq__(self, other):
        result = (isinstance(other, Bank) and
                  self.name == other.name and
                  self.description == other.description and
                  self.short_name == other.short_name and
                  self.text_color == other.text_color and
                  self.background_color == other.background_color and
                  self.to_display == other.to_display and
                  self.clear_toggle == other.clear_toggle and
                  self.presets == other.presets)
        # Debugging: set a breakpoint on the self.modified line to discovery where two items differ
        if not result:
            self.modified = True
        return result

    def set_preset(self, preset, pos):
        if self.presets is None:
            self.presets = [None] * 24
        self.presets[pos] = preset


# Model for a MIDI Channel Name mapping
class MidiChannel(jg.JsonGrammarModel):
    def __init__(self):
        super().__init__()
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
        super().__init__()
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
        super().__init__()
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
        result = (self.banks == other.banks and
                  self.midi_channels == other.midi_channels and
                  self.bank_arrangement == other.bank_arrangement and
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


msg_array_schema = \
    jg.make_dict('msgArray',
                 [jg.make_key('data', jg.make_list(18, jg.make_atom(int, 0), 'msg_array_data')),
                  jg.make_key('m', jg.make_atom(int, value=jg.identity)),
                  # c is channel
                  jg.make_key('c', jg.make_atom(int, 1, var='channel')),
                  # t is the message type (CC or PC)
                  jg.make_key('t', jg.make_atom(int, 0, var='type')),
                  # a is the trigger
                  jg.make_key('a', jg.make_atom(int, 0, var='trigger')),
                  # tg is toggle group
                  jg.make_key('tg', jg.make_atom(int, 2, var='toggle_group')),
                  jg.make_key('mi', jg.make_atom(str, value=''))],
                 model=MidiMessage)

preset_array_schema = \
    jg.make_dict('presetArray',
                 [jg.make_key('presetNum', jg.make_atom(int, value=jg.identity)),
                  jg.make_key('bankNum', jg.make_atom(int, value=jg.identity2)),
                  jg.make_key('isExp', jg.false_atom),
                  jg.make_key('shortName', jg.make_atom(str, 'EMPTY', var='short_name')),
                  jg.make_key('toggleName', jg.make_atom(str, '', var='toggle_name')),
                  jg.make_key('longName', jg.make_atom(str, '', var='long_name')),
                  jg.make_key('shiftName', jg.make_atom(str, value='')),
                  jg.make_key('toToggle', jg.make_atom(bool, False, var='to_toggle')),
                  jg.make_key('toBlink', jg.false_atom),
                  jg.make_key('toMsgScroll', jg.false_atom),
                  jg.make_key('toggleGroup', jg.zero_atom),
                  # the led is the strip at the bottom (top?) of the window
                  jg.make_key('ledColor', jg.make_atom(int, 0, var='strip_color')),
                  jg.make_key('ledToggleColor', jg.make_atom(int, 0, var='strip_toggle_color')),
                  jg.make_key('ledShiftColor', jg.zero_atom),
                  jg.make_key('nameColor', jg.make_atom(int, 7, var='name_color')),
                  jg.make_key('nameToggleColor', jg.make_atom(int, 7, var='name_toggle_color')),
                  jg.make_key('nameShiftColor', jg.make_atom(int, value=7)),
                  jg.make_key('backgroundColor', jg.make_atom(int, 0, var='background_color')),
                  jg.make_key('toggleBackgroundColor', jg.make_atom(int, 0, var='background_toggle_color')),
                  jg.make_key('shiftBackgroundColor', jg.zero_atom),
                  jg.make_key('msgArray', jg.make_list(32, msg_array_schema, var='messages'))],
                 model=Preset)

exp_preset_array_schema = \
    jg.make_dict('expPresetArray',
                 [jg.make_key('presetNum', jg.make_atom(int, value=jg.identity)),
                  jg.make_key('bankNum', jg.make_atom(int, value=jg.identity2)),
                  jg.make_key('isExp', jg.make_atom(bool, value=True)),
                  jg.make_key('shortName', jg.make_atom(str, value='EMPTY')),
                  jg.make_key('toggleName', jg.make_atom(str, value='')),
                  jg.make_key('longName', jg.make_atom(str, value='')),
                  jg.make_key('shiftName', jg.make_atom(str, value='')),
                  jg.make_key('toToggle', jg.false_atom),
                  jg.make_key('toBlink', jg.false_atom),
                  jg.make_key('toMsgScroll', jg.false_atom),
                  jg.make_key('toggleGroup', jg.zero_atom),
                  jg.make_key('ledColor', jg.zero_atom),
                  jg.make_key('ledToggleColor', jg.zero_atom),
                  jg.make_key('ledShiftColor', jg.zero_atom),
                  jg.make_key('nameColor', jg.make_atom(int, value=7)),
                  jg.make_key('nameToggleColor', jg.make_atom(int, value=7)),
                  jg.make_key('nameShiftColor', jg.make_atom(int, value=7)),
                  jg.make_key('backgroundColor', jg.zero_atom),
                  jg.make_key('toggleBackgroundColor', jg.zero_atom),
                  jg.make_key('shiftBackgroundColor', jg.zero_atom),
                  jg.make_key('msgArray', jg.make_list(32, msg_array_schema))])


# Sometimes the bank message array data has a 127 value
def bank_msg_array_data_hack(elem, _ctxt, _lp):
    if isinstance(elem, int):
        if elem == 0 or elem == 127:
            return elem
    return 0


bank_msg_array_schema = \
    jg.make_dict(
        'bankMsgArray',
        [jg.make_key('data',
                     jg.make_list(18, jg.make_atom(int, value=bank_msg_array_data_hack))),
         jg.make_key('m', jg.make_atom(int, value=jg.identity)),
         jg.make_key('c', jg.make_atom(int, value=1)),
         jg.make_key('t', jg.zero_atom),
         jg.make_key('a', jg.zero_atom),
         jg.make_key('tg', jg.make_atom(int, value=2)),
         jg.make_key('mi', jg.make_atom(str, value=''))])

bank_array_schema = \
    jg.make_dict(
        'bankArray',
        [jg.make_key('bankNumber', jg.make_atom(int, value=jg.identity)),
         jg.make_key('bankName', jg.make_atom(str, '', var='name')),
         jg.make_key('bankClearToggle', jg.make_atom(bool, False, var='clear_toggle')),
         jg.make_key('bankMsgArray', jg.make_list(32, bank_msg_array_schema)),
         jg.make_key('presetArray', jg.make_list(24, preset_array_schema, var='presets')),
         jg.make_key('expPresetArray', jg.make_list(4, exp_preset_array_schema)),
         jg.make_key('bankDescription', jg.make_atom(str, '', var='description')),
         jg.make_key('toDisplay', jg.make_atom(bool, False, var='to_display')),
         jg.make_key('backgroundColor', jg.make_atom(int, 127, var='background_color')),
         jg.make_key('textColor', jg.make_atom(int, 127, var='text_color')),
         jg.make_key('isColorEnabled', jg.make_atom(bool, True))],
        model=Bank)

omniport_schema = \
    jg.make_dict(
        'omniport',
        [jg.make_key('type', jg.make_atom(str, value='omniport_input')),
         jg.make_key(
             'data',
             jg.make_dict(
                 'omniport_data',
                 [jg.make_key('portNum', jg.make_atom(int, value=jg.identity)),
                  jg.make_key('type', jg.make_atom(int, value=1)),
                  jg.make_key('fixedSwTip', jg.zero_atom),
                  jg.make_key('fixedSwRing', jg.zero_atom),
                  jg.make_key('fixedSwTipRing', jg.zero_atom),
                  jg.make_key('td1', jg.zero_atom),
                  jg.make_key('td2', jg.zero_atom),
                  jg.make_key('rd1', jg.zero_atom),
                  jg.make_key('rd2', jg.zero_atom),
                  jg.make_key('trd1', jg.zero_atom),
                  jg.make_key('trd2', jg.zero_atom)]))])

omniports_schema = \
    jg.make_dict(
        'omniports',
        [jg.make_key('type', jg.make_atom(str, value='omniport_all')),
         jg.make_key('data', jg.make_list(4, omniport_schema))])

usb_host_matrix_schema = \
    jg.make_dict('usbHost',
                 [jg.make_key('din5', jg.false_atom),
                  jg.make_key('mm35', jg.false_atom),
                  jg.make_key('omniport', jg.false_atom),
                  jg.make_key('usbDevice', jg.false_atom)])

usb_device_matrix_schema = \
    jg.make_dict('usbDevice',
                 [jg.make_key('din5', jg.false_atom),
                  jg.make_key('mm35', jg.false_atom),
                  jg.make_key('omniport', jg.false_atom),
                  jg.make_key('usbHost', jg.false_atom)])

din5_matrix_schema = \
    jg.make_dict('din5',
                 [jg.make_key('din5', jg.false_atom),
                  jg.make_key('mm35', jg.false_atom),
                  jg.make_key('omniport', jg.false_atom),
                  jg.make_key('usbDevice', jg.false_atom),
                  jg.make_key('usbHost', jg.false_atom)])

mm35_device_matrix_schema = \
    jg.make_dict('mm35',
                 [jg.make_key('din5', jg.false_atom),
                  jg.make_key('mm35', jg.false_atom),
                  jg.make_key('omniport', jg.false_atom),
                  jg.make_key('usbDevice', jg.false_atom),
                  jg.make_key('usbHost', jg.false_atom)])

midi_thru_matrix_schema = \
    jg.make_dict(
        'midi_thru_matrix',
        [jg.make_key('type', jg.make_atom(str, value='midiThruMatrix')),
         jg.make_key('data',
                     jg.make_dict('midi_thru_matrix_data',
                                  [jg.make_key('usbHost', usb_host_matrix_schema),
                                   jg.make_key('usbDevice', usb_device_matrix_schema),
                                   jg.make_key('din5', din5_matrix_schema),
                                   jg.make_key('mm35', mm35_device_matrix_schema)]))])


# Midi clock only uses 11 bits, but often defaults to 12 bits set
# This takes care of that difference
def midi_clock_output_ports(elem, _ctxt, _lp):
    if isinstance(elem, int):
        if elem & 2047 == 2047:
            return elem
    return 4095


general_configuration_schema = \
    jg.make_dict(
        'general_configurations',
        [jg.make_key('type', jg.make_atom(str, value='general_configurations')),
         jg.make_key(
             'data',
             jg.make_dict(
                 'general_configurations_data',
                 [jg.make_key('dualLock', jg.false_atom),
                  jg.make_key('midiClockPersist', jg.false_atom),
                  jg.make_key('lcdAlign', jg.make_atom(bool, value=True)),
                  jg.make_key('midiThru', jg.false_atom),
                  jg.make_key('ignoreMidiClock', jg.false_atom),
                  jg.make_key('crossMidiThru', jg.false_atom),
                  jg.make_key('savePresetToggle', jg.false_atom),
                  jg.make_key('midiChannel', jg.make_atom(int, 0, var='midi_channel')),
                  jg.make_key('switchSensitivity', jg.make_atom(int, value=2)),
                  jg.make_key('bankChangeDelayTime', jg.zero_atom),
                  jg.make_key('bankChangeDisplayTime', jg.make_atom(int, value=60)),
                  jg.make_key('longPressTime', jg.make_atom(int, value=12)),
                  jg.make_key('loadLastBankOnStartup', jg.false_atom),
                  jg.make_key('numMidiCable', jg.make_atom(int, value=1)),
                  jg.make_key('midiSendDelay', jg.zero_atom),
                  jg.make_key('presetMaxFontSize', jg.make_atom(int, value=3)),
                  jg.make_key('showPresetLabels', jg.false_atom),
                  jg.make_key('midiThruMatrix', midi_thru_matrix_schema),
                  jg.make_key('screenSaverTime', jg.zero_atom),
                  jg.make_key('midiClockOutputPorts', jg.make_atom(int, value=midi_clock_output_ports)),
                  jg.make_key('rpA', jg.zero_atom),
                  jg.make_key('rpB', jg.zero_atom)]))])

waveform_engine_schema = \
    jg.make_dict(
        'waveform_engine',
        [jg.make_key('type', jg.make_atom(str, value='waveform_engine')),
         jg.make_key(
             'data',
             jg.make_dict(
                 'waveform_engine_data',
                 [jg.make_key('max', jg.make_atom(int, value=127)),
                  jg.make_key('min', jg.zero_atom),
                  jg.make_key('num', jg.make_atom(int, value=jg.identity)),
                  jg.make_key('type', jg.zero_atom)]))])

waveform_engines_schema = \
    jg.make_dict(
        'waveform_engines',
        [jg.make_key('type', jg.make_atom(str, value='waveform_engines')),
         jg.make_key('data', jg.make_list(8, waveform_engine_schema))])


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
    jg.make_dict(
        'sequencer_engine',
        [jg.make_key('type', jg.make_atom(str, value='sequencer_engine')),
         jg.make_key(
             'data',
             jg.make_dict(
                 'sequencer_engine_data',
                 [jg.make_key('engineNum',
                              jg.make_atom(int, value=jg.identity)),
                  jg.make_key('len', jg.make_atom(int, value=sequencer_engine_len_hack)),
                  jg.make_key(
                      'arr',
                      jg.make_list(16, jg.make_atom(int, value=sequencer_engine_arr_hack)))]))])

sequencer_engines_schema = \
    jg.make_dict(
        'sequencer_engines',
        [jg.make_key('type', jg.make_atom(str, value='sequencer_engines')),
         jg.make_key('data', jg.make_list(8, sequencer_engine_schema))])

scroll_counter_schema = \
    jg.make_dict(
        'scroll_counter',
        [jg.make_key('type', jg.make_atom(str, value='scroll_counter')),
         jg.make_key(
             'data',
             jg.make_dict(
                 'scroll_counter_data',
                 [jg.make_key('index', jg.make_atom(int, value=jg.identity)),
                  jg.make_key('min', jg.zero_atom),
                  jg.make_key('max', jg.make_atom(int, value=127)),
                  jg.make_key('start', jg.zero_atom)]))])

scroll_counters_schema = \
    jg.make_dict(
        'scroll_counters',
        [jg.make_key('type', jg.make_atom(str, value='scroll_counters')),
         jg.make_key(
             'data', jg.make_list(16, scroll_counter_schema))])

midi_channel_schema = \
    jg.make_dict(
        'midi_channel',
        [jg.make_key('type', jg.make_atom(str, value='midi_channel')),
         jg.make_key(
             'data',
             jg.make_dict(
                 'midi_channel_data',
                 [jg.make_key('name', jg.make_atom(str, '', var='name')),
                  jg.make_key('channel', jg.make_atom(int, value=jg.identity_plus_1)),
                  jg.make_key('sendToPort', jg.make_atom(int, value=2047)),
                  jg.make_key('remap', jg.zero_atom)]))],
        model=MidiChannel)

midi_channels_schema = \
    jg.make_dict(
        'midi_channels',
        [jg.make_key('type', jg.make_atom(str, value='midi_channels')),
         jg.make_key(
             'data',
             jg.make_list(16, midi_channel_schema, var='midi_channels'))])

bank_arrangement_item_schema = \
    jg.make_dict(
        'bank_arrangement',
        [jg.make_key('type', jg.make_atom(str, value='bank_arrangement')),
         jg.make_key(
             'data',
             jg.make_dict(
                 'bank_arrangement_data',
                 [jg.make_key('bankNum', jg.make_atom(int, value=jg.identity)),
                  jg.make_key('bankName', jg.make_atom(str, '', var='name'))]))],
        model=BankArrangementItem)

bank_arrangement_schema = \
    jg.make_dict(
        'bank_arrangements',
        [jg.make_key('type', jg.make_atom(str, value='bank_arrangement')),
         jg.make_key('isActive', jg.false_atom),
         jg.make_key('numBanksActive', jg.zero_atom),
         jg.make_key('data', jg.make_list(127, bank_arrangement_item_schema, var='bank_arrangement'))])

midi_event_schema = \
    jg.make_dict(
        'midi_event',
        [jg.make_key('type', jg.make_atom(str, value='midi_event')),
         jg.make_key(
             'data',
             jg.make_dict(
                 'midi_event_data',
                 [jg.make_key('typeFrom', jg.zero_atom),
                  jg.make_key('typeTo', jg.zero_atom),
                  jg.make_key('numberFrom', jg.zero_atom),
                  jg.make_key('numberTo', jg.zero_atom),
                  jg.make_key('channelFrom', jg.zero_atom),
                  jg.make_key('channelTo', jg.zero_atom),
                  jg.make_key('valueFrom', jg.zero_atom),
                  jg.make_key('valueTo', jg.zero_atom),
                  jg.make_key('toSetOutgoingValue', jg.false_atom),
                  jg.make_key('toMapInputOutput', jg.false_atom),
                  jg.make_key('toMapValue', jg.false_atom)]))])

midi_events_schema = \
    jg.make_dict(
        'midi_events',
        [jg.make_key('type', jg.make_atom(str, value='midi_events')),
         jg.make_key('data', jg.make_list(16, midi_event_schema))])

resistor_ladder_aux_data_schema = \
    jg.make_dict(
        'resistor_ladder_aux_data',
        [jg.make_key('type', jg.make_atom(str, value='resistor_ladder_aux_switch')),
         jg.make_key('data', jg.make_dict('resistor_switch',
                                          [jg.make_key('switchNumber', jg.make_atom(int, value=jg.identity)),
                                           jg.make_key('triggerValue', jg.make_atom(int, value=0)),
                                           jg.make_key('f1', jg.make_atom(int, value=0)),
                                           jg.make_key('f2', jg.make_atom(int, value=0))]))]
    )
resistor_ladder_aux_schema = \
    jg.make_dict('resistor_ladder_aux',
                 [jg.make_key('type', jg.make_atom(str, value='resistor_ladder_aux_switch_all')),
                  jg.make_key('data', jg.make_list(16, resistor_ladder_aux_data_schema))])

controller_settings_schema = \
    jg.make_dict(
        'controller_settings',
        [jg.make_key('type', jg.make_atom(str, value='controller_settings_all')),
         jg.make_key(
             'data',
             jg.make_dict('controller_settings_data',
                          [jg.make_key('omniports', omniports_schema),
                           jg.make_key('controller_settings', general_configuration_schema),
                           jg.make_key('waveform_engines', waveform_engines_schema),
                           jg.make_key('sequencer_engines', sequencer_engines_schema),
                           jg.make_key('scroll_counters', scroll_counters_schema),
                           jg.make_key('midi_channels', midi_channels_schema),
                           jg.make_key('bank_arrangement', bank_arrangement_schema),
                           jg.make_key('midi_events', midi_events_schema),
                           jg.make_key('resistor_ladder_aux', resistor_ladder_aux_schema)]))])


def download_date(_elem, _ctxt, _lp):
    return datetime.datetime.now().isoformat()


mc6pro_schema = \
    jg.make_dict(
        'mc6pro',
        [jg.make_key("schemaVersion", jg.make_atom(int, value=1)),
         jg.make_key("dumpType", jg.make_atom(str, value='allBanks')),
         jg.make_key("deviceModel", jg.make_atom(int, value=6)),
         jg.make_key("downloadDate", jg.make_atom(str, download_date, var='download_date')),
         jg.make_key("hash", jg.make_atom(int, 0, var='hash')),
         jg.make_key("description", jg.make_atom(str, value='')),
         jg.make_key(
             "data",
             jg.make_dict('data',
                          [jg.make_key('bankArray',
                                       jg.make_list(128, bank_array_schema, 'banks')),
                           jg.make_key('controller_settings', controller_settings_schema)]))],
        model=MC6Pro)

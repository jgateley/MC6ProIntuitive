import colors
import grammar as jg
import simple_message as sm
from backup_grammar import midi_channels_schema
from version import version_verify
import simple_model

# This is the minimal version of the backup format.
# It is intended to be a human-readable version of the backup format.
#
# The main features:
# It is minimal, you only include what is significant, making it easier to edit the config file
# It is not deeply nested, again for ease of editing
#
# TODO: Select Exp Messages midi message is not implemented
# TODO: Trigger Messages midi message is not implemented

# MIDI channel grammar, just a name
# The backup grammar includes the channel, but it always appears in order, so I don't duplicate that here.
midi_channel_schema = \
    jg.Dict(
        'midi_channel',
        [jg.Dict.make_key('name', jg.Atom('Name', str, '', var='name'))],
        model=simple_model.SimpleMidiChannel)

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
                              jg.Enum('Message Scroll', sm.onoff_type, sm.onoff_default,
                                      var='message_scroll')),
             jg.Dict.make_key('text', colors.make_enum('text', colors.colors[127], var='text')),
             jg.Dict.make_key('text_toggle', colors.make_enum('text_toggle', colors.colors[127], var='text_toggle')),
             jg.Dict.make_key('text_shift', colors.make_enum('text_shift', colors.colors[127], var='text_shift')),
             jg.Dict.make_key('background', colors.make_enum('background', colors.colors[127], var='background')),
             jg.Dict.make_key('background_toggle', colors.make_enum('background_toggle', colors.colors[127],
                                                                    var='background_toggle')),
             jg.Dict.make_key('background_shift', colors.make_enum('background_shift', colors.colors[127],
                                                                   var='background_shift')),
             jg.Dict.make_key('strip_color',
                              jg.Enum('Strip Color', colors.colors, colors.empty_color, var='strip_color')),
             jg.Dict.make_key('strip_toggle_color',
                              jg.Enum('Strip Toggle Color', colors.colors, colors.empty_color,
                                      var='strip_toggle_color')),
             jg.Dict.make_key('messages',
                              jg.List('Message List', 0, sm.simple_preset_message_schema, var='messages'))],
            model=simple_model.SimplePreset)

# All the information associated with a bank
bank_schema = \
    jg.Dict('bank',
            [jg.Dict.make_key('name', jg.Atom('Name', str, '', var='name')),
             jg.Dict.make_key('description', jg.Atom('Description', str, '', var='description')),
             jg.Dict.make_key('text', colors.make_enum('text', colors.colors[127], var='text')),
             jg.Dict.make_key('background', colors.make_enum('background', colors.colors[127], var='background')),
             jg.Dict.make_key('clear_toggle',
                              jg.Atom('Clear Toggle', bool, False, var='clear_toggle')),
             jg.Dict.make_key('display_description',
                              jg.Atom('Display Description', bool, False, var='display_description')),
             jg.Dict.make_key('messages',
                              jg.List('Message List', 0, sm.simple_bank_message_schema, var='messages')),
             jg.Dict.make_key('presets', jg.List('Preset List', 0, preset_schema, var='presets')),
             jg.Dict.make_key('exp_presets', jg.List('Exp Preset List', 0, preset_schema, var='exp_presets'))],
            model=simple_model.SimpleBank)


# The whole schema
simple_schema = \
    jg.Dict('simple_schema',
            [jg.Dict.make_key('midi_channels',
                              jg.List('MIDI Channel List', 16, midi_channel_schema, var='midi_channels')),
             jg.Dict.make_key('banks', jg.List('Bank List', 128, bank_schema, var='banks')),
             jg.Dict.make_key('midi_channel', jg.Atom('MIDI Channel', int, 1, var='midi_channel')),
             jg.Dict.make_key('version',
                              jg.Atom('Version', str, value=version_verify, var='version'), required=True)],
            model=simple_model.Simple)

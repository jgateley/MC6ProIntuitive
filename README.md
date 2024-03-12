# MC6ProIntuitive
Configuring the Morningstar MC6Pro via an intuitive config file
- Human editable configuration file (YAML or JSON)
- Named messages allow easy reuse
- Named banks
- Named color schemas allow consistent use of colors in banks and presets
- Navigator mode: Bank 1 is a roadmap/index bank, and navigating is easy
- Navigator mode allows more than 32 presets per bank

## Overview
The Morningstar Editor is great software, but presents a brittle experience. Instead, this package defines a YAML or JSON based configuation file. The configuration file is converted to a MC6Pro backup format, and can be restored to the device.

Instead of editing directly through the editor, you edit the configuration file via any editor capable of handling YAML or JSON.

You start by backing up your config and converting that into into an Intuitive config.

## Human editable Configuration file
The MC6Pro backup files are JSON, but are not human editable. They are large (over 11MB) and all fields and elements are present, even if empty or not used.

The Intuitive format only requires values for non-empty fields and elements. Banks, for example, would only have banks actually in use instead of all banks.

In addition, the format is more intuitive: the top level includes device configuration, messages (which appear deeply nested in the backup format), MIDI channels, Color Schemas and banks.

Messages, MIDI channels, and banks are referred to by name, instead of relying on position or a number.

## Named messages allow easy reuse

Named messages deserve special mention: messages are named and defined at top level.

When a preset refers to a message, it only refers to the name. This allows easy reuse of a message.

```
  presets:
  - short_name: Enabled
    toggle_name: Disabled
    messages:
    - {midi_message: Iridium Disable, toggle: one}
    - {midi_message: Iridium Enable, toggle: two}
  - short_name: Clean
    messages:
    - {midi_message: Iridium Bank 0}
    - {midi_message: Iridium Clean}
  - short_name: Burry
    messages:
    - {midi_message: Iridium Bank 0}
    - {midi_message: Iridium Burry}
```

## Named banks

With named banks, the bank's position in the bank list doesn't matter. It is referred to by name.

This is primarily for `Bank Jump` messages, and is used in Navigator mode.

## Color Schemas
Color schemas define a set of colors. Each set includes a bank forground and background color, and preset foreground and background colors for both the toggle and untoggled state. For example:
```
colors:
- name: default
  bank_color: black
  bank_background_color: lightyellow
  preset_color: black
  preset_background_color: lightyellow
- name: navigator
  bank_color: red
  bank_background_color: yellow
  preset_color: red
  preset_background_color: yellow
- name: bypass
  preset_color: black
  preset_toggle_color: white
  preset_background_color: darkgreen
  preset_toggle_background_color: red
```
The first schema is the default schema, and applies to any bank or preset that doesn't specify a color. The second is the Navigator mode schema, and applies to the Navigator mode bank (usually bank 1) and Navigator mode presets. The third is intended for bypass/enable presets.
### Color Schema Inheritance
A preset uses (highest priority first):
1. The preset color schema
2. The bank color schema
3. The `default` color schema
4. No color schema

A bank uses (highest priority first):
1. The bank color schema
2. The `default` color schema
3. No color schema

A navigator bank uses (highest priority first):
1. The `navigator` color schema
2. The `default` color schema
3. No color schema

A navigator preset uses (highest priority first):
1. The `navigator` color schema
2. The bank color schema (of the bank where the navigator preset appears)
3. No color schema.

This last may seem confusing: it could be argued that the default should be used instead of the bank color schema.
But the best approach is to provide a navigator schema.

## Navigator mode

Navigator mode has two aspects:
- it is easy to navigate between banks
- it is easy to navigate between pages in a bank

In navigator mode, bank 1 is a roadmap. The presets for bank 1 are named after banks, and pressing the preset takes you to that bank. Preset C on each bank is set to return you to the roadmap.

In addition, all banks (including the roadmap) bank use the two rightmost presets (e.g. C and F on page 1) for page navigation - page up and page down.

If you define a bank (in an Intuitive conf file) that has more than 24 presets, that bank is broken into two MC6Pro banks, and the page up/page down presets navigate between the two banks and pages seamlessly.
This may happen even with less than 24 presets, as the page navigation presets inserted by Navigator Mode count against the total.

## Use

Everything is done via the python app `mc6pro.py` and the `Controller Backup` tab on the Morningstar Editor.
You also have the following resources:

### Features.json
This contains all implemented features as a backup file. Convert it to an intuitive config to see the syntax:

`python3 -b Features.json Features-Intuitive.json`

### Demo.yaml
This is a sample Intuitive config file

### Initial Use

1. Create a backup of your current configuration in the `Controller Backup` tab, using `All banks (including Controller Settings)`, say it is named `backup.json`
2. Convert to intuitive format (use `.json` as the extension if you prefer JSON): `python3 mc6pro.py -b backup.json intuitive.yaml`

The names chosen for the messages are not intuitive, so you should rename them. Also, add the Navigator Mode element if you want:

    "navigator": true,



### Later use

Now, edit your `Intuitive.yaml` file, and make any changes or additions. Then convert it to a backup file:

`python3 intuitive.yaml intuitive-base.json`

And load that file via the `Controller Backup` tab in the editor using `Restore your controller presets`
Note that the MC6Pro will state the file has been modified.

## Theory and Development

The heart of the app is a grammar tool. The grammar tool handles JSON grammars. It can parse a grammar into a model (python object representing the meaning), or generate a JSON string from a model.
YAML is a superset of JSON, and the Python representation is the same.

The backup files (aka base files) have a grammar that is complete. This means all elements must appear, even if they are default values.

The intuitive files have a grammar that is minimal: only non-default values appear.

The backup grammar is defensive: elements that are not yet implemented are coded in the grammar as constants. Getting a value that doesn't match the constant will cause an error. This happens when someone is using a feature that is not yet supported.

Grammars consist of atoms (int, str, boolean), enums, lists, dictionaries, and switch dictionaries (which allow a little variation in the structure).

There is a pretty comprehensive set of tests. They can be run via:

`python3 tests.py`

In addition, the tests produce a few base config files, named:
- `tmp\Empty.json`
- `tmp\Features.json`
- `tmp\Demo.json`
- `tmp\NavigatorTest_Base_Script.json`

- These should be loaded and spot-checked after changes.
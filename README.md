# Morningstar(MC6Pro) Intuitive Configuration
## Overview
The Morningstar Editor is great software, but presents a friable experience.
As an alternative, this package defines a YAML or JSON based configuation file with a tool for
conversion to a MC6Pro backup format,
that can be restored to the device.
It may work with
other Morningstar products, but hasn't yet been tested with them.
- Human editable configuration file (YAML or JSON)
- Config file can be stored in source control like github
- Named messages allow easy reuse
- Messages are defined in the device that consumes them
- Named banks
- Easy to create presets to jump to banks
- Named color palettes allow consistent use of colors in banks and presets
- **Easy to create presets that cycle through options**


Instead of editing directly through the Morningstar editor, you edit the configuration file via any editor capable of handling YAML or JSON.

## Use

Everything is done via the python app `morningstar.py` and the `Controller Backup` tab on the Morningstar Editor.
You will need Python3 installed, and the packages `PyYAML` and `semver`.
You also have the following resources:

### Example.yaml
This is a sample Intuitive config file, containing all implemented features.

### Config.yaml
This is my actual config file, and shows how I use it

### Initial Use

1. Create a backup of your current configuration in the `Controller Backup` tab, using `All banks (including Controller Settings)`, say it is named `backup.json`
2. Create an intuitive config file, say `myconfig.yaml` or `myconfig.json`.
3. Convert your intuitive file to a backup format file: `morningstar.py myconfig.yaml myconfig_backup.json` or `python3 morningstar.py myconfig.yaml myconfig_backup.json`
4. Load the intuitive file via the `Controller Backup` tab.
5. Restart the controller.
5. Make changes to the intuitive file as needed and repeat step 4.

### Advanced Use
There is also a simple format, in addition to the backup and intuitive formats.
The simple format is a simple version of the backup format, intended to be human readable, but without any of the features of intuitive.
## Human editable Configuration file
The MC6Pro backup files are JSON, but are not human editable.
They are large (over 11MB) and all fields and elements are present, even if empty or not used.

The intuitive format covers the most common use cases in an easy to use format.
The top level includes color palettes, devices (including message definitions) and banks.

The Intuitive format only requires values for non-empty fields and elements.
Banks, for example, would only have banks actually in use instead of all banks.

Messages, MIDI channels (aka devices), and banks are referred to by name, instead of relying on position or a number.

## Named messages allow easy reuse

Named messages deserve special mention: messages are named and defined at the device level.
For example, when defining an `Iridium` device, you also define the messages:
```
devices:
  # The Strymon Iridium amp-in-a-pedal
  - name: Iridium
    channel: 1
    enable: {type: CC, number: 102, value: 127}
    bypass: {type: CC, number: 102, value: 0}
    messages:
    - {name: Bank 0, type: CC, number: 0, value: 0}
    - {name: Clean, type: PC, number: 0, setup: Bank 0}
    - {name: Burry, type: PC, number: 1, setup: Bank 0}
    - {name: Distortion, type: PC, number: 2, setup: Bank 0}
    - {name: Max Distortion, type: PC, number: 3, setup: Bank 0}

```

When a preset refers to a message, it only refers to the name. This allows easy reuse of a message. For example, here is a bank with several presets:

```
- name: Iridium
  description: Iridium choices
  presets:
  - {type: bypass, device: Iridium}
  - {short_name: Clean, actions: [{name: Iridium Clean, trigger: Press}]}
  - {short_name: Burry, actions: [{name: Iridium Burry, trigger: Press}]}
  - {short_name: Distortion, actions: [{name: Iridium Distortion, trigger: Press}]}
  - {short_name: Max Distortion, actions: [{name: Iridium Max Distortion, trigger: Press}]}
  - {short_name: Home, actions: [{name: Bank Home, trigger: Press}]}
```

## Named banks

With named banks, the bank's position in the bank list doesn't matter. It is referred to by name.
This is primarily for `Bank Jump` messages.

For example, you can define a home bank that gives convenient access to other banks:
```
- name: Home
  description: Navigation to other banks
  presets:
    - {short_name: Noodling, actions: [{name: Bank Noodling, trigger: Press}]}
    - {short_name: Devices, actions: [{name: Bank Devices, trigger: Press}]}
    - {short_name: Songs, actions: [{name: Bank Songs, trigger: Press}]}

```
## Cycle Through Presets
If you have an amp-in-a-box pedal that provides different amp models, you may want
to cycle through them in a single preset. This is easy to achieve:
```
    presets:
      - type: cycle
        actions:
          - {name: Fender, action: AmpInAPedal Fender}
          - {name: Marshall, action: AmpInAPedal Marshall}
          - {name: Mesa, action: AmpInAPedal Mesa}
          - {name: Peavey, action: AmpInAPedal Peavey}
```
On bank entry, the pedal is set to Fender, and the preset displays `Fender`.
Clicking the preset switches the pedal to Marshall, and the preset now displays `Marshal`.
If you have many options (like for an eq control), you can switch directions with a Long Press.
## Color Palettes
Color schemas define a set of colors.
Each set includes many potential targets like `bank_text` or `preset_shifted_text`.
If a field does not explicitly appear, the `text` or `background` palette is used.
For example:
```
palettes:
  - name: default
    text: lime
    background: blue
    bank_text: yellow
    bank_background: orchid
    preset_text: gray
    preset_background: orange
    preset_shifted_text: red
    preset_shifted_background: skyblue
    preset_toggle_text: deeppink
    preset_toggle_background: olivedrab
    preset_led: mediumslateblue
    preset_led_shifted: darkgreen
    preset_led_toggle: aqua

```
The `default` palette (as seen above) is the default schema, and applies to any bank or preset that doesn't specify a color.

## Simple Format
The Simple format is a human editable version of the backup format.
It does not require all fields to be present (default values are skipped), and much of the grammar is simplified.
It does not provide new features (like named banks), and is intended to be solely a simplified version of the backup format.
It can be used if you want to experiment, or don't like the intuitive format, or just want to see what is in a backup file
## Theory and Development

The heart of the app is a grammar tool.
The grammar tool handles JSON or YAML data.
A grammar can transform data into a model (python object representing the meaning), or generate JSON or YAML data from a model.
YAML is a superset of JSON, and the Python representation is the same.

The backup files have a grammar that is complete. This means all elements must appear, even if they are default values.

The intuitive files have a grammar that is minimal: only non-default values appear.
In addition, the intuitive grammar is designed to be convenient to use, and the transformation to a backup grammar object is complex.

The backup grammar is defensive: elements that are not yet implemented are coded in the grammar as constants. Getting a value that doesn't match the constant will cause an error. This happens when someone is using a feature that is not yet supported.

Grammars consist of atoms (int, str, boolean), enums, lists, dictionaries, and switch dictionaries (which allow a little variation in the structure).

There is a pretty comprehensive set of tests. They can be run via:

```
python3 test_grammar.py
python3 test_simple.py
python3 test_intuitive.py
```

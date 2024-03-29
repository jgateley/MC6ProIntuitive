| Top Level      | Implemented      | Notes                                        |
|----------------|------------------|----------------------------------------------|
| Schema Version | Yes - Constant   | Will need work when schema changes           |
| Dump Type      | Yes - restricted | Only All Banks supported                     |
| Device Model   | Yes: 6           |                                              |
| Download Date  | Yes              |                                              |
| Hash           | No               | I need the hash algorithm                    |
| Description    | No               |                                              |
| Bank Array | Partial | See sub-table |
| Controller Settings | Partial | See sub-table|

| Controller Settings | Implemented | Notes                                                     |
|---------------------|-------------|-----------------------------------------------------------|
| Omniports           | No          | See subtable                                              |
| Controller Settings | Partial     | Subelement of the other controller settings, see subtable |
| Waveform Engines    | No          | See subtable                                              |
| Sequencer Engines   | No          | See subtable                                              |
| Scroll Counters     | No          | See subtable                                              |
| MIDI Channels | Partial     | See subtable                                              |
| Bank Arrangement | Partial     | See subtable                                              |
| MIDI Events |             |                                                           |
| Resistor Ladder Aux | No          | See subtable                                              |

| Omniports | Implemented      | Notes                                        |
|-----------|------------------|----------------------------------------------|
| **all**   | No               |                                              |

| Controller Settings (subtable) | Implemented | Notes                                        |
|--------------------------------|-------------|----------------------------------------------|
| MIDI Channel                   | Yes         |                                              |
| **all others** | No | |

| Waveform Engines | Implemented      | Notes                                        |
|------------------|------------------|----------------------------------------------|
| **all**          | No               |                                              |

| Sequencer Engines | Implemented      | Notes                                        |
|-------------------|------------------|----------------------------------------------|
| **all**           | No               |                                              |

| Scroll Counters | Implemented      | Notes                                        |
|-----------------|------------------|----------------------------------------------|
| **all**         | No               |                                              |

| MIDI CHannels | Implemented | Notes                                        |
|---------------|-------------|----------------------------------------------|
| Name          | Yes         |                                              |
| Channel | Yes | Fixed ordering, cannot change |
| Send To Port | No | |
| Remap | No | |

| Bank Arrangement | Implemented      | Notes                                        |
|------------------|------------------|----------------------------------------------|
| Is Active        | No               |                                              |
| Number Banks Active | No | |
| Bank Arrangement | Partial | I verify the bank arrangement is unchanged |

| MIDI Events | Implemented      | Notes                                        |
|-------------|------------------|----------------------------------------------|
| **all**     | No               |                                              |

| Resistor Ladder Aux | Implemented      | Notes                                        |
|---------------------|------------------|----------------------------------------------|
| Resistor Switch     | No               |                                              |

| Bank Array  | Implemented | Notes                           |
|-------------|-------------|---------------------------------|
| Bank Number | Yes         | Must be in ortder               |
| Bank Name | Yes         |                                 |
| Clear Toggle | Yes         | Only 1 preset in toggle state 2 |
| Bank Message Array | Partial     | See message subtable            |
| Preset Array | Partial     | See subtable                    |
| Exp Preset Array | No          | See subtable                    |
| Description | Yes         |                                 |
| To Display | Yes         | Display bank description        |
| Background Color | Yes         |                                 |
| Text Color | Yes         |                                 |
| Color Enabled | No          | Assumed True                    |


| Preset Array            | Implemented | Notes            |
|-------------------------|-------------|------------------|
| Number                  | Yes         | Must be in order |
| Bank Number             | Yes         | Must match parent bank, in order |
| Is Exp                  | No          | |
| Short Name              | Yes         | |
| Toggle Name             | Yes         | |
| Long Name               | Yes         | |
| Shift Name              | No          | |
| Toggle Mode             | Yes         |  |
| To Blink                | No          | |
| To Message Scroll       | No          | |
| Toggle Group            | Yes         | |
| LED Color               | Yes         |  |
| LED Toggle Color        | Yes         |  |
| LED Shift Color         | Yes         |  |
| Name Color              | Yes         | |
| Name Toggle Color       | Yes         | |
| Name Shift Color        | Yes         | |
| Background Color        | Yes         | |
| Toggle Background Color | Yes         | |
| Shift Background Color  | Yes         | |
| Messages                | Partial     | See subtable |



| Exp Preset Array | Implemented | Notes                 |
|------------------|-------------|-----------------------|
| Message Array    | Partial     | Shared implementation |
| *all others* | No          | |

| Messages   | Implemented | Notes                                                                                  |
|------------|-------------|----------------------------------------------------------------------------------------|
| m (number) | Yes         | Must be in order                                                                       |
| c (channel) | Yes |                                                                                        |
| t (type) | Partial | PC, CC, Bank Jump, Page Jump, Toggle Page                                              |
| a (trigger) | Yes | Bank Triggers and Preset Triggers                                                      |
| tg (Toggle Group) | Yes | but toggle groups not implemented. Not sure what this is, as toggle groups are presets |
| mi (unknown) | No |                                                                                        |

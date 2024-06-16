
# Change Log
## [0.2.0] - 2024-06-16
- Added get/set var methods to JsonGrammarModel
- Changed dict keys so that on complete models, a key can be marked as not required
    - This allows the setlist program output to be parsed
    - It doesn't include the controller settings
- Added per-key models to switch dicts
- add To Message Scroll to the Preset Array schema (MC6Pro Config)
- Added shifted name color and to msg scroll to preset
- Added Exp Preset Array
- Better handling of Intuitive messages, using first class functions
- All message types are now handled, more or less
- Added better 'required' parameter to dict keys
- Added 'per switch' models to switch dicts

## [0.1.2] - 2024-04-17
- Added names to all grammar nodes
- Added print_grammar program
- Refactored navigator mode, no functional change
- Improved error handling
- Made Jump Bank message have page default to 0
- Added "One Button" mode to Navigator Mode
- Added Navigator Mode override to mc6pro.py for testing
- Improved parsing to handle setlist files as well as backup files

## [0.1.1] - 2024-03-29
  
- Added Toggle Group
- Improved error messages
- Added versions to sample files
- Better versioning
- Fixed bug: bank messages not being converted to Base

## [0.1.0] - 2024-03-17
  
- Initial version with a change log
- Bank Messages
- Implementation.md a matrix describing which features are implemented
- renamed Bank to_description to display_description
- renamed Preset to_toggle to toggle_mode
- major refactor of grammar code: cleaned up tests, grammar nodes are python objects instead of dictionaries
- Added versioning

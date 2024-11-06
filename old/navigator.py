class Navigator:
    @staticmethod
    def clone_bank(bank, overflow_number, presets):
        result = IntuitiveBank()
        result.name = bank.name + " (" + str(overflow_number + 2) + ")"
        result.description = bank.description
        result.colors = bank.colors
        result.presets = presets
        return result

    def __init__(self, mode, banks, colors_catalog, message_catalog):
        self.mode = mode
        self.banks = banks
        self.colors_schema = colors_catalog.get_navigator_schema()
        self.message_catalog = message_catalog
        if mode == "One Button":
            self.main_action = "Release"
            self.second_action = "Long Press"
        else:
            self.main_action = "Press"
            self.second_action = "Press"
        self.blank_preset = self.mk_preset('', [])
        return_to_home_message = self.mk_bank_jump_message('Home')
        self.return_to_home_preset = self.mk_preset('Home', self.mk_preset_messages(return_to_home_message))
        self.next_page_message = im.SimpleMessage.make_toggle_page_message('next_page', True, message_catalog)
        self.next_page_preset = self.mk_preset('Next', self.mk_preset_messages(self.next_page_message))
        self.prev_page_message = im.SimpleMessage.make_toggle_page_message('prev_page', False, message_catalog)
        self.prev_page_preset = self.mk_preset('Previous', self.mk_preset_messages(self.prev_page_message))
        self.prev_next_page_preset = self.mk_preset('Previous/Next',
                                                    self.mk_preset_messages(self.prev_page_message,
                                                                            self.next_page_message))

    def pad_presets(self, presets, desired_length):
        while len(presets) < desired_length:
            presets.append(self.blank_preset)

    def mk_bank_jump_message(self, bank_name):
        return im.SimpleMessage.make_bank_jump_message('navigator ' + bank_name, bank_name, 0, self.message_catalog)

    def mk_preset_messages(self, main_message, second_message=None):
        if isinstance(main_message, IntuitivePresetMessage):
            first_message = main_message
        else:
            first_message = IntuitivePresetMessage.make(main_message, self.main_action)
        result = [first_message]
        if second_message is not None:
            result.append(IntuitivePresetMessage.make(second_message, self.second_action))
        return result

    def mk_preset(self, name, messages):
        return IntuitivePreset.make(name, messages, self.colors_schema)

    # Clean up the bank list (remove internal Nones)
    # Add in the roadmap bank at the beginning
    # Fill in the roadmap presets, and add the home preset to each bank
    # Go through each bank:
    #   Add the home preset or prev page preset
    #   Add next page preset if needed
    # Go through each real bank and add the home preset, and page moving presets
    def build(self):
        self.add_home_bank()
        self.add_page_up_down()

    def add_home_bank(self):
        jg.compact_list(self.banks)
        home_bank = self.get_home_bank()
        # And add in the navigator presets and the return home preset
        for bank in self.banks:
            home_bank.presets.append(self.jump_to_bank_preset(bank))
            self.add_navigator_home_preset(bank)
        self.banks.insert(0, home_bank)

    def get_home_bank(self):
        result = IntuitiveBank()
        result.name = "Home"
        result.description = "Navigation Home"
        result.colors = self.colors_schema
        result.presets = []
        return result

    def jump_to_bank_preset(self, bank):
        jump_to_bank_message = self.mk_bank_jump_message(bank.name)
        return self.mk_preset(bank.name, self.mk_preset_messages(jump_to_bank_message))

    def add_navigator_home_preset(self, bank):
        home_offset = 2
        if self.mode == "One Button":
            home_offset = 5
        if bank.presets is None:
            bank.presets = []
        self.pad_presets(bank.presets, home_offset)
        bank.presets.insert(home_offset, copy.deepcopy(self.return_to_home_preset))

    def add_page_up_down(self):
        bank_number = 0
        while bank_number < len(self.banks):
            bank = self.banks[bank_number]
            presets = self.add_page_up_down_bank(bank)
            prev_bank = bank
            bank_number += 1
            overflow_number = 0
            while len(presets) > 0:
                bank = self.clone_bank(bank, overflow_number, presets)
                self.add_next_bank(prev_bank, bank)
                self.add_previous_bank(bank, prev_bank)
                self.banks.insert(bank_number + overflow_number, bank)
                presets = self.add_page_up_down_bank(bank)
                prev_bank = bank
                overflow_number += 1
            bank_number += overflow_number

    def add_paging_preset_pair(self, bank, page):
        pos = page * 6 + 5
        offset = pos + 3
        if self.mode == "One Button":
            offset = pos + 6
        if bank.presets[pos] == self.prev_page_preset:
            # The previous page has already added a next/previous pair, this is the "previous" part of the pair
            bank.presets[pos] = self.prev_next_page_preset
        elif bank.presets[pos].short_name == 'Previous':
            # In one button mode, one page 1 of an overflow bank, we need to add a next page
            preset = bank.presets[pos]
            preset.short_name = 'Previous/Next'
            preset.messages = self.mk_preset_messages(preset.messages[0], self.next_page_message)
        elif bank.presets[pos].short_name == 'Home':
            # Add a page up message to the return to home preset
            preset = bank.presets[pos]
            preset.short_name = 'Home/Next'
            preset.messages = self.mk_preset_messages(preset.messages[0], self.next_page_message)
        else:
            bank.presets.insert(pos, self.next_page_preset)
        self.pad_presets(bank.presets, offset)
        bank.presets.insert(offset, self.prev_page_preset)

    def add_page_up_down_bank(self, bank):
        if len(bank.presets) <= 6:
            return []
        self.add_paging_preset_pair(bank, 0)
        if len(bank.presets) <= 12:
            return []
        self.add_paging_preset_pair(bank, 1)
        if len(bank.presets) <= 18:
            return []
        self.add_paging_preset_pair(bank, 2)
        if len(bank.presets) <= 24:
            return []
        if self.mode == "One Button":
            limit = 24
        else:
            limit = 23
        result = bank.presets[limit:]
        bank.presets = bank.presets[0:limit]
        return result

    def add_next_bank(self, bank, next_bank):
        next_page_message = self.mk_bank_jump_message(next_bank.name)
        if self.mode == "One Button":
            prev_next_page_preset = self.mk_preset('Previous/Next',
                                                   self.mk_preset_messages(self.prev_page_message, next_page_message))
            bank.presets[23] = prev_next_page_preset
        else:
            next_page_preset = self.mk_preset('Next', self.mk_preset_messages(next_page_message))
            bank.presets.insert(23, next_page_preset)

    def add_previous_bank(self, bank, previous_bank):
        previous_page_message = self.mk_bank_jump_message(previous_bank.name)
        previous_page_preset = self.mk_preset('Previous', self.mk_preset_messages(previous_page_message))
        position = 2
        if self.mode == "One Button":
            position = 5
        while len(bank.presets) < position:
            bank.presets.append(self.blank_preset)
        bank.presets.insert(position, previous_page_preset)



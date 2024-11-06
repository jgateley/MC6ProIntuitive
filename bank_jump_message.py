import grammar as jg


# For Bank Jump in the backup:
#  data[0] is the bank number, base 0
#  data[1] should be 0, it is 127 for last used
#  data[2] is the page number (6 = 1, 7 = 2, 14 = 3, 15 = 4)
class BankJumpModel(jg.GrammarModel):
    @staticmethod
    def build_from_backup(simple_message, backup_message):
        simple_message.specific_message = BankJumpModel()
        simple_message.name += simple_message.specific_message.from_backup(backup_message)

    @staticmethod
    def build(bank):
        result = BankJumpModel()
        result.bank = bank
        result.page = None
        return result

    @staticmethod
    def get_case_keys(_intuitive=False):
        return [BankJumpModel,
                jg.SwitchDict.make_key('bank', jg.Atom('Bank', int, var='bank')),
                jg.SwitchDict.make_key('page', jg.Atom('Page', int, default=0, var='page'))]

    def __init__(self):
        super().__init__('BankJumpModel')
        self.bank = None
        self.page = None

    def __eq__(self, other):
        result = isinstance(other, BankJumpModel) and self.bank == other.bank and self.page == other.page
        if not result:
            self.modified = True
        return result

    def from_backup(self, backup_message):
        self.bank = 0
        if backup_message.msg_array_data[0] is not None:
            self.bank = backup_message.msg_array_data[0]
        if backup_message.msg_array_data[2] == 6:
            self.page = None
        elif backup_message.msg_array_data[2] == 7:
            self.page = 1
        elif backup_message.msg_array_data[2] == 14:
            self.page = 2
        elif backup_message.msg_array_data[2] == 15:
            self.page = 3
        else:
            raise IntuitiveException('missing case', 'missing case')
        name = str(self.bank)
        if self.page is not None:
            name += ':' + str(self.page)
        if backup_message.msg_array_data[1] is not None:
            raise IntuitiveException('bad_message', 'data array is nonzero')
        return name

    # TODO: Can we remove bank_catalog from to_backup parameter list?
    # TODO: general cleanup on this list, some may not be required
    def to_backup(self, backup_message, _bank_catalog, _simple_bank, _simple_preset):
        backup_message.msg_array_data[0] = self.bank
        if self.page == 0 or self.page is None:
            backup_message.msg_array_data[2] = 6
        elif self.page == 1:
            backup_message.msg_array_data[2] = 7
        elif self.page == 2:
            backup_message.msg_array_data[2] = 14
        elif self.page == 3:
            backup_message.msg_array_data[2] = 15
        else:
            raise IntuitiveException('invalid_page_number', "Invalid page number in bank jump")

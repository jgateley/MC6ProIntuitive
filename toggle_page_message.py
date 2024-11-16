import grammar as jg
from IntuitiveException import IntuitiveException


# The Toggle Page message:
# data[0] == 1 => page up
# data[0] == 2 => page down
# data[0] == 3, 4, 5, or 6 => goto page 1, 2, 3, or 4
class TogglePageModel(jg.GrammarModel):
    @staticmethod
    def build_from_backup(simple_message, backup_message):
        simple_message.specific_message = TogglePageModel()
        simple_message.name += simple_message.specific_message.from_backup(backup_message)

    @staticmethod
    def build(page_up):
        result = TogglePageModel()
        if page_up:
            result.page = 1
        else:
            result.page = 2
        return result

    @staticmethod
    def get_case_keys(_intuitive=False):
        return [TogglePageModel,
                jg.SwitchDict.make_key('page', jg.Atom('Page', int, var='page'))]

    def __init__(self):
        super().__init__('TogglePageModel')
        self.page = None

    def __eq__(self, other):
        result = isinstance(other, TogglePageModel) and self.page == other.page
        if not result:
            self.modified = True
        return result

    def from_backup(self, backup_message):
        self.page = backup_message.msg_array_data[0]
        return 'TogglePage:' + str(self.page)

    # TODO: Can we remove bank_catalog from to_backup parameter list?
    # TODO: general cleanup on this list, some may not be required
    def to_backup(self, backup_message, _bank_catalog, _simple_bank, _simple_preset):
        backup_message.msg_array_data[0] = self.page

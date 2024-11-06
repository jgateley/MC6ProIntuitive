import grammar as jg
import simple_model


class PCCCBaseModel(jg.GrammarModel):
    @staticmethod
    def build_from_backup(simple_message, backup_message):
        backup_channel = backup_message.channel
        if simple_message.type == "PC":
            simple_message.specific_message = PCModel()
            simple_message.name += simple_message.specific_message.from_backup(backup_channel, backup_message)
        elif simple_message.type == 'CC':
            simple_message.specific_message = CCModel()
            simple_message.name += simple_message.specific_message.from_backup(backup_channel, backup_message)

    def __init__(self):
        super().__init__('PCCCBaseModel')
        self.number = None
        self.value = None
        self.channel = None

    def eq_common(self, other):
        result = isinstance(other, PCCCBaseModel) and self.number == other.number and self.channel == other.channel
        if not result:
            self.modified = True
        return result

    def eq_value(self, other):
        result = isinstance(other, PCCCBaseModel) and self.value == other.value
        if not result:
            self.modified = True
        return result

    def from_backup_common(self, channel, backup_message):
        if channel is None:
            channel = 1
        name = str(channel) + ':'
        self.channel = channel
        if backup_message.msg_array_data is None:
            self.number = 0
        else:
            self.number = backup_message.msg_array_data[0]
            if self.number is None:
                self.number = 0
        name += str(self.number)
        return name

    def to_backup_common(self, backup_message):
        backup_message.channel = self.channel
        if backup_message.channel == 1:
            backup_message.channel = None

        backup_message.msg_array_data[0] = self.number


class PCModel(PCCCBaseModel):
    @staticmethod
    def make(number, channel):
        obj = PCModel()
        obj.number = number
        obj.channel = channel
        return obj

    @staticmethod
    def build_from_backup(simple_message, backup_message):
        PCCCBaseModel.build_from_backup(simple_message, backup_message)

    # The PC message does not require a channel for the intuitive/config, but it does for the backup and simple formats
    @staticmethod
    def get_case_keys():
        return [PCModel,
                jg.SwitchDict.make_key('number', jg.Atom('Number', int, var='number')),
                jg.SwitchDict.make_key('channel', jg.Atom('Channel', int, var='channel'), required=True)]

    def __init__(self):
        super().__init__()

    def __eq__(self, other):
        result = isinstance(other, PCModel) and self.eq_common(other)
        if not result:
            self.modified = True
        return result

    def from_backup(self, channel, backup_message):
        return self.from_backup_common(channel, backup_message)

    def to_backup(self, backup_message, _bank_catalog, _simple_bank, _simple_preset):
        self.to_backup_common(backup_message)


class CCModel(PCCCBaseModel):
    @staticmethod
    def make(number, value, channel):
        obj = CCModel()
        obj.number = number
        obj.value = value
        obj.channel = channel
        return obj

    @staticmethod
    def build_from_backup(simple_message, backup_message):
        PCCCBaseModel.build_from_backup(simple_message, backup_message)

    # The CC message does not require a channel for the intuitive/config, but it does for the backup and simple formats
    @staticmethod
    def get_case_keys():
        return [CCModel,
                jg.SwitchDict.make_key('number', jg.Atom('Number', int, var='number')),
                jg.SwitchDict.make_key('value', jg.Atom('Value', int, var='value')),
                jg.SwitchDict.make_key('channel', jg.Atom('Channel', int, var='channel'), required=True)]

    def __init__(self):
        super().__init__()

    def __eq__(self, other):
        result = isinstance(other, CCModel) and self.eq_common(other) and self.eq_value(other)
        if not result:
            self.modified = True
        return result

    def from_backup(self, channel, backup_message):
        name = self.from_backup_common(channel, backup_message)
        if backup_message.msg_array_data is None:
            self.value = 0
        else:
            self.value = backup_message.msg_array_data[1]
            if self.value is None:
                self.value = 0
        name += ':' + str(self.value)
        return name

    def to_backup(self, backup_message, _bank_catalog, _simple_bank, _simple_preset):
        self.to_backup_common(backup_message)
        backup_message.msg_array_data[1] = self.value

import json_grammar as jg
import MC6Pro_grammar


class IntuitiveMidiChannel(jg.JsonGrammarModel):
    def __init__(self, name=None):
        super().__init__("IntuitiveMidiChannel")
        self.name = name

    def __eq__(self, other):
        result = isinstance(other, IntuitiveMidiChannel) and self.name == other.name
        if not result:
            self.modified = True
        return result

    def from_base(self, base_midi_channel):
        self.name = base_midi_channel.name

    def to_base(self):
        base_midi_channel = MC6Pro_grammar.MidiChannel()
        base_midi_channel.name = self.name
        return base_midi_channel



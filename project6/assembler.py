from iterator import Iterator
from symbol_table import SymbolTable
from instruction_translator import InstructionTranslator


class Assembler:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.instruction_translator = InstructionTranslator()

    def _fill_symbol_table():
        iterator = Iterator()
        while iterator.has_next():
            instruction = iterator.next()

    def _get_translated_instructions():
        pass

    def translate(self, source):
        self._fill_symbol_table()
        return self._get_translated_instructions()

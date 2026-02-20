from symbol_table import SymbolTable
from instruction_translator import InstructionTranslator


class Assembler:
    def __init__(self):
        pass

    def _get_symbol_table_and_remove_comments(self, path):
        symbol_table = SymbolTable()
        file = open(path, "r")
        lines = []
        line_number = 0
        for line in file:

            # ignore comment
            if line.startswith("//"):
                continue

            # symbol declarations
            if line.startswith("("):
                symbol_table.set_address(line[1:-2], line_number + 1)
                continue

            lines.append(line.rstrip("\n"))
            line_number += 1

        return symbol_table, lines

    def translate_file(self, path, target_path):
        symbol_table, sanitized_lines = self._get_symbol_table_and_remove_comments(path)
        instruction_translator = InstructionTranslator(symbol_table)
        translated_lines = instruction_translator.translate_lines(sanitized_lines)
        return translated_lines
        # TODO: write to file
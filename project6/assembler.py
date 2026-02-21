from symbol_table import SymbolTable
from instruction_translator import InstructionTranslator


class Assembler:
    def __init__(self):
        pass

    def _get_symbol_table_and_remove_comments(self, path):
        symbol_table = SymbolTable()
        file = open(path, "r")
        lines = []
        next_instruction_address = 0
        for line in file:
            line = line.strip()
            # ignore comment
            if line.startswith("//"):
                continue

            # empty line
            if line == "":
                continue

            # symbol declarations
            if line.startswith("("):
                end_ind = line.find(")")
                symbol_table.set_address(line[1:end_ind], next_instruction_address)
                continue

            lines.append(line)
            next_instruction_address += 1

        return symbol_table, lines

    def translate_file(self, path):
        symbol_table, sanitized_lines = self._get_symbol_table_and_remove_comments(
            path)
        instruction_translator = InstructionTranslator(symbol_table)
        translated_lines = instruction_translator.translate_lines(
            sanitized_lines)
        target_path = path.split(".")[0] + ".bin"
        self.write_file(translated_lines, target_path)

    def write_file(self, lines, target_path):
        with open(target_path, "w") as f:
            for line in lines:
                f.write(line + "\n")

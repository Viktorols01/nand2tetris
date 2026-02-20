# why does this not exist in standard library
def to_n_bits(numeric_value, n):
    bin_rep = format(int(numeric_value), f"#b")[2:]
    return bin_rep.zfill(n)[-n:]


class InstructionTranslator:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table

    def translate(self, line):
        is_a_instruction = line.startswith("@")
        if is_a_instruction:
            return self.translate_a_instruction(line)
        else:
            return self.translate_c_instruction(line)

    def translate_a_instruction(self, line):
        address_part = line[1:]
        if self.symbol_table.contains_symbol(address_part):
            value = self.symbol_table.get_address(address_part)
        elif address_part.isnumeric:
            value = address_part
        else:
            # add symbol and try again
            self.symbol_table.generate_and_set_address(address_part)
            return self.translate_a_instruction(line)
        return "0" + to_n_bits(value, 15)

    def translate_c_instruction(self, line):
        def split_into_comp_and_dest(string):
            spl = string.split(";")
            if len(spl) > 1:
                comp_part = spl[0]
                jump_part = spl[1]
            else:
                comp_part = spl[0]
                jump_part = ""
            return comp_part, jump_part

        spl = line.split("=")
        if len(spl) > 1:
            dest_part = spl[0]
            comp_part, jump_part = split_into_comp_and_dest(spl[1])
        else:
            dest_part = ""
            comp_part, jump_part = split_into_comp_and_dest(spl[0])
        return "111" + self.get_a_bits(comp_part) + self.get_comp_bits(comp_part) + self.get_dest_bits(dest_part) + self.get_jump_bits(jump_part)
    
    def get_dest_bits(self, dest_part):
        print(dest_part)
        return "0" * 3

    def get_comp_bits(self, comp_part):
        print(comp_part)
        return "0" * 3

    def get_a_bits(self, comp_part):
        return "0" # basically check if M is included

    def get_jump_bits(self, jump_part):
        print(jump_part)
        return "0" * 6

    def translate_lines(self, lines):
        translated_lines = []
        for line in lines:
            translated_line = self.translate(line)
            translated_lines.append(translated_line)
        return translated_lines

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
        elif address_part.isnumeric():
            value = address_part
        else:
            # add symbol and try again
            self.symbol_table.generate_and_set_address(address_part)
            return self.translate_a_instruction(line)
        return "0" + to_n_bits(value, 15)

    def translate_c_instruction(self, line):
        equal_ind = -1
        semicolon_ind = len(line)

        if "=" in line:
            equal_ind = line.find("=")
            dest_part = line[0:equal_ind]
        else:
            dest_part = ""
        
        if ";" in line:
            semicolon_ind = line.find(";")
            jump_part = line[semicolon_ind+1:]
        else:
            jump_part = ""

        comp_part = line[equal_ind + 1:semicolon_ind]
        
        if comp_part == "":
            print(line)
            print("d", dest_part)
            print("c", comp_part)
            print("j", jump_part)

        return "111" + self.get_a_bits(comp_part) + self.get_comp_bits(comp_part) + self.get_dest_bits(dest_part) + self.get_jump_bits(jump_part)
    
    def get_dest_bits(self, dest_part):
        match(dest_part):
            case "M":
                return "001"
            case "D":
                return "010"
            case "DM":
                return "011"
            case "A":
                return "100"
            case "AM":
                return "101"
            case "AD":
                return "110"
            case "ADM":
                return "111"
            case _:
                return "000"

    def get_comp_bits(self, comp_part):
        match(comp_part):
            case "0":
                return "101010"
            case "1":
                return "111111"
            case "-1":
                return "111010"
            case "D":
                return "001100"
            case "A" | "M":
                return "110000"
            case "!D":
                return "001101"
            case "!A" | "!M":
                return "110001"
            case "-D":
                return "001111"
            case "-A" | "-M":
                return "110011"
            case "D+1":
                return "011111"
            case "A+1" | "M+1":
                return "110111"
            case "D-1":
                return "001110"
            case "A-1" | "M-1":
                return "110010"
            case "D+A" | "D+M":
                return "000010"
            case "D-A" | "D-M":
                return "010011"
            case "A-D" | "M-D":
                return "000111"
            case "D&A" | "D&M":
                return "000000"
            case "D|A" | "D|M":
                return "010101"
            case _:
                return "error"

    def get_a_bits(self, comp_part):
        if "M" in comp_part:
            return "1"
        else:
            return "0"

    def get_jump_bits(self, jump_part):
        match(jump_part):
            case "JGT":
                return "001"
            case "JEQ":
                return "010"
            case "JGE":
                return "011"
            case "JLT":
                return "100"
            case "JNE":
                return "101"
            case "JLE":
                return "110"
            case "JMP":
                return "111"
            case _:
                return "000"

    def translate_lines(self, lines):
        translated_lines = []
        for line in lines:
            translated_line = self.translate(line)
            translated_lines.append(translated_line)
        return translated_lines

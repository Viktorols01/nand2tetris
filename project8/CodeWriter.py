from Parser import VmCommand, VmCommandType


class CodeWriter:
    def __init__(self, file):
        self.file = file
        self.wh = WriterHelper("???", "main", self._write)
        self.return_i = 0

    def _write(self, *string_list):
        for string in string_list:
            self.file.write(string + "\n")

    def translate_vm_command_list(self, file_path_in, vm_command_list):
        file_prefix = file_path_in.split(".")[0].split("/")[-1]
        self.wh.file_prefix = file_prefix
        for vm_command in vm_command_list:
            self._translate_vm_command(vm_command)

    def _translate_vm_command(self, vm_command):
        def _get_goto_symbol_from_label(label):
            return f"{self.wh.file_prefix}.{self.wh.function_prefix}${label}"

        def _get_return_symbol_from_label():
            self.return_i += 1
            return f"{self.wh.function_prefix}$ret.{self.return_i}"

        self._write(f"// --- Translating '{vm_command.source}' ---")
        match vm_command.command_type:
            case VmCommandType.ARITHMETIC:
                self.wh.perform_arithmetic(vm_command.arg1)
                return
            case VmCommandType.PUSH:
                self.wh.write_segment_value_to_d_register(
                    vm_command.arg1, vm_command.arg2)
                self._write("@SP", "A=M", "M=D", "@SP", "M=M+1")
                return
            case VmCommandType.POP:
                self._write("@SP", "M=M-1")
                self.wh.write_sp_to_segment(vm_command.arg1, vm_command.arg2)
                return
            case VmCommandType.LABEL:
                label = vm_command.arg1
                label_symbol = _get_goto_symbol_from_label(label)
                self._write(f"({label_symbol})")
                return
            case VmCommandType.GOTO:
                label = vm_command.arg1
                label_symbol = _get_goto_symbol_from_label(label)
                self._write(f"@{label_symbol}", "0;JMP")
                return
            case VmCommandType.IF_GOTO:
                label = vm_command.arg1
                label_symbol = _get_goto_symbol_from_label(label)
                self.wh.pop_stack_to_d_register()
                # if popped stack value is not 0, then jump
                self._write(f"@{label_symbol}", "D;JNE")
                return
            case VmCommandType.FUNCTION:
                function_name = vm_command.arg1
                n_vars = vm_command.arg2
                self.wh.function_prefix = function_name
                self._write(f"({function_name})")
                self._write("@0", "D=A")
                if n_vars:
                    for i in range(int(n_vars)):
                        self.wh.push_d_register_to_stack()
                return
            case VmCommandType.CALL:
                function_name = vm_command.arg1
                n_args = int(vm_command.arg2)
                return_symbol = _get_return_symbol_from_label()
                self.wh.push_value_to_stack(f"{return_symbol}")
                self.wh.push_value_to_stack("LCL")
                self.wh.push_value_to_stack("ARG")
                self.wh.push_value_to_stack("THIS")
                self.wh.push_value_to_stack("THAT")
                # reposition ARG
                self._write("@SP", "A=M", "D=A") # D = RAM[SP] = RAM[0]
                self._write("@5", "D=D-A") # D = D - 5
                self._write(f"@{n_args}", "D=D-A") # D = D - n_args
                self._write("@ARG", "M=D")
                # reposition LCL
                self._write("@SP", "A=M", "D=A") # D = RAM[SP] = RAM[0]
                self._write("@LCL", "M=D") # ARG = RAM[SP] = RAM[0]
                # jump to function
                self._write(f"@{function_name}", "0;JMP")
                # return to following instruction
                self._write(f"({return_symbol})")
                return
            case VmCommandType.RETURN:
                # frame is stored in R13
                self._write("@LCL", "D=M", "@R13", "M=D")
                # retAddr is stored in R14
                self._write("@5", "A=D-A", "A=M", "D=A", "@R14", "M=D")
                # write result of function to stack
                self.wh.pop_stack_to_d_register()
                # remember: top of stack before calling: (arg1, ..., argn) after calling: (result)
                self._write("@ARG", "A=M", "M=D") # *ARG = pop()
                def set_segment_pointer(name, rel_pos):
                    # name = *(frame - rel_pos)
                    self._write("@R13", "D=M", f"@{rel_pos}", "D=D-A", "A=D", "D=M", f"@{name}", "M=D")
                self._write("@ARG", "A=M", "D=A+1", "@SP", "M=D") # SP = ARG + 1
                set_segment_pointer("THAT", 1)
                set_segment_pointer("THIS", 2)
                set_segment_pointer("ARG", 3)
                set_segment_pointer("LCL", 4)
                # goto retAddr
                self._write("@R14", "A=M", "0;JMP")
                return
            case _:
                return
        self._write("--- ---")
        self._write("")


class WriterHelper:
    def __init__(self, file_prefix, function_prefix, _write):
        self.symbol_index = 0
        self.file_prefix = file_prefix
        self.function_prefix = function_prefix
        self._write = _write

    def _get_next_symbol(self):
        # well I gotta use different symbols throughout the code
        # so I'll just use a global counter
        self.symbol_index += 1
        return f"SYMBOL{self.symbol_index}"

    def write_segment_address_to_d_register(self, segment, i):
        i = int(i)
        match segment:
            case "constant":
                raise Excepion("No address for constants!")
            case "local" | "argument" | "this" | "that":
                segment_to_address = {
                    "local": "LCL",
                    "argument": "ARG",
                    "this": "THIS",
                    "that": "THAT"
                }
                address = segment_to_address[segment]
                self._write(f"@{address}", "A=M", "D=A", f"@{i}", "D=D+A")
            case "pointer":
                self._write(f"@{i+3}", "D=A")
            case "temp":
                self._write(f"@{i+5}", "D=A")
            case "static":
                self._write(f"@{file_prefix}.{i}", "D=A")
            case _:
                raise Exception("Undefined segment!")

    def write_segment_value_to_d_register(self, segment, i):
        match segment:
            case "constant":
                self._write(f"@{i}", "D=A")
            case _:
                self.write_segment_address_to_d_register(segment, i)
                # _write("A=D", "A=M", "D=M")
                # the above line was causing errors, I had an extra "A=M"... rip 1 hour
                # the line above the above line caused errors again because I forgot to comment it out after adding the above comment :) rip 1 more hour
                # embarrassing
                self._write("A=D", "D=M")

    # this seems to be working
    def write_sp_to_segment(self, segment, i):
        # while writing this I noticed that I couldn't use D to simultaneously store the segment address and SP value.
        # if I didn't google the issue (and found someone who came to the same realization), I would've written A=A+1 i times.
        # but what I found on stackoverflow was a reminder that I have access to other registers than D...
        self.write_segment_address_to_d_register(segment, i)
        self._write("@R13", "M=D")  # segment address stored in R13
        self._write(f"@SP", "A=M", "D=M")  # SP value stored in D
        self._write("@R13", "A=M", "M=D")  # store D in R13 address

    def pop_stack_to_d_register(self):
        self._write("@SP", "M=M-1", "A=M", "D=M")

    def push_value_to_stack(self, value):
        self._write(f"@{value}", "D=A")
        self._write("@SP", "A=M", "M=D")  # write result to SP
        self._write("@SP", "M=M+1")  # increment SP

    def push_d_register_to_stack(self):
        self._write("@SP", "A=M", "M=D")  # write result to SP
        self._write("@SP", "M=M+1")  # increment SP

    def _perform_boolean_arithmetic(self, jump_type):
        # remember: -1 is true, 0 is false
        self.pop_stack_to_d_register()  # upper value is stored in D
        self._write("@R13", "M=D")  # D is stored in R13
        self.pop_stack_to_d_register()  # lower value is stored in D
        # TODO: this can cause collisions, maybe there is a way to do it without using additional labels?
        equal_symbol = self._get_next_symbol()
        end_symbol = self._get_next_symbol()
        # goto equal symbol if true
        self._write("@R13", "A=M", "D=D-A",
                    f"@{equal_symbol}", f"D;{jump_type}")
        self._write("@0", "D=A")  # set D to 0
        self._write(f"@{end_symbol}", "0;JMP")  # goto end symbol
        self._write(f"({equal_symbol})")
        self._write(f"@0", "D=A", "D=D-1")  # set D to -1
        self._write(f"({end_symbol})")
        self.push_d_register_to_stack()

    def perform_arithmetic(self, command):
        match command:
            case "add":
                self.pop_stack_to_d_register()  # upper value is stored in D
                self._write("@R13", "M=D")  # D is stored in R13
                self.pop_stack_to_d_register()  # lower value is stored in D
                self._write("@R13", "A=M", "D=D+A")  # add R13 to D
                self.push_d_register_to_stack()
            case "sub":
                self.pop_stack_to_d_register()  # upper value is stored in D
                self._write("@R13", "M=D")  # D is stored in R13
                self.pop_stack_to_d_register()  # lower value is stored in D
                self._write("@R13", "A=M", "D=D-A")  # subtract R13 from D
                self.push_d_register_to_stack()
            case "neg":
                self.pop_stack_to_d_register()  # upper value is stored in D
                self._write("D=-D")
                self.push_d_register_to_stack()
            case "eq":
                self._perform_boolean_arithmetic("JEQ")
            case "gt":
                self._perform_boolean_arithmetic("JGT")
            case "lt":
                self._perform_boolean_arithmetic("JLT")
            case "and":
                self.pop_stack_to_d_register()  # upper value is stored in D
                self._write("@R13", "M=D")  # D is stored in R13
                self.pop_stack_to_d_register()  # lower value is stored in D
                self._write("@R13", "A=M", "D=D&A")  # R13 and D
                self.push_d_register_to_stack()
            case "or":
                self.pop_stack_to_d_register()  # upper value is stored in D
                self._write("@R13", "M=D")  # D is stored in R13
                self.pop_stack_to_d_register()  # lower value is stored in D
                self._write("@R13", "A=M", "D=D|A")  # R13 and D
                self.push_d_register_to_stack()
            case "not":
                self.pop_stack_to_d_register()  # upper value is stored in D
                self._write("D=!D")
                self.push_d_register_to_stack()

    def write_infinite_loop(self):
        last_symbol = self._get_next_symbol()
        for string in ["// Infinite loop time", f"({last_symbol})", f"@{last_symbol}", "0;JMP"]:
            self._write(string + "\n")

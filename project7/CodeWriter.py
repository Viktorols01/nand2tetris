from Parser import VmCommand, VmCommandType

symbol_index = 0


def _get_next_symbol():
    # well I gotta use different symbols throughout the code
    # so I'll just use a global counter
    global symbol_index
    symbol_index += 1
    return f"SYMBOL{symbol_index}"


def translate_vm_command_list(file_path, vm_command_list):
    with open(file_path, 'w') as file:
        for vm_command in vm_command_list:
            _translate_vm_command(
                file, vm_command, file_prefix=file_path.split(".")[0])

        # infinite loop
        last_symbol = _get_next_symbol()
        for string in ["// Infinite loop time", f"({last_symbol})", f"@{last_symbol}", "0;JMP"]:
            file.write(string + "\n")


def _translate_vm_command(file, vm_command, file_prefix):
    def write(*string_list):
        for string in string_list:
            file.write(string + "\n")

    def write_segment_address_to_d_register(segment, i):
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
                write(f"@{address}", "A=M", "D=A", f"@{i}", "D=D+A")
            case "pointer":
                write(f"@{i+3}", "D=A")
            case "temp":
                write(f"@{i+5}", "D=A")
            case "static":
                write(f"@{file_prefix}.{i}", "D=A")
            case _:
                raise Exception("Undefined segment!")

    # TODO: This does NOT seem to work...
    def write_segment_value_to_d_register(segment, i):
        match segment:
            case "constant":
                write(f"@{i}", "D=A")
            case _:
                write_segment_address_to_d_register(segment, i)
                write("A=D", "A=M", "D=M") # this line was causing errors, I had an extra "A=M"...
                write("A=D", "D=M")

    # this seems to be working
    def write_sp_to_segment(segment, i):
        # while writing this I noticed that I couldn't use D to simultaneously store the segment address and SP value.
        # if I didn't google the issue (and found someone who came to the same realization), I would've written A=A+1 i times.
        # but what I found on stackoverflow was a reminder that I have access to other registers than D...
        write_segment_address_to_d_register(segment, i)
        write("@R13", "M=D")  # segment address stored in R13
        write(f"@SP", "A=M", "D=M")  # SP value stored in D
        write("@R13", "A=M", "M=D")  # store D in R13 address

    def perform_arithmetic(command):
        def pop_stack_to_d_register():
            write("@SP", "M=M-1", "A=M", "D=M")

        def push_d_register_to_stack():
            write("@SP", "A=M", "M=D")  # write result to SP
            write("@SP", "M=M+1")  # increment SP

        def perform_boolean_arithmetic(jump_type):
            # remember: -1 is true, 0 is false
            pop_stack_to_d_register()  # upper value is stored in D
            write("@R13", "M=D")  # D is stored in R13
            pop_stack_to_d_register()  # lower value is stored in D
            equal_symbol = _get_next_symbol()
            end_symbol = _get_next_symbol()
            # goto equal symbol if true
            write("@R13", "A=M", "D=D-A", f"@{equal_symbol}", f"D;{jump_type}")
            write("@0", "D=A")  # set D to 0
            write(f"@{end_symbol}", "0;JMP")  # goto end symbol
            write(f"({equal_symbol})")
            write(f"@0", "D=A", "D=D-1")  # set D to -1
            write(f"({end_symbol})")
            push_d_register_to_stack()

        match command:
            case "add":
                pop_stack_to_d_register()  # upper value is stored in D
                write("@R13", "M=D")  # D is stored in R13
                pop_stack_to_d_register()  # lower value is stored in D
                write("@R13", "A=M", "D=D+A")  # add R13 to D
                push_d_register_to_stack()
            case "sub":
                pop_stack_to_d_register()  # upper value is stored in D
                write("@R13", "M=D")  # D is stored in R13
                pop_stack_to_d_register()  # lower value is stored in D
                write("@R13", "A=M", "D=D-A")  # subtract R13 from D
                push_d_register_to_stack()
            case "neg":
                pop_stack_to_d_register()  # upper value is stored in D
                write("D=-D")
                push_d_register_to_stack()
            case "eq":
                perform_boolean_arithmetic("JEQ")
            case "gt":
                perform_boolean_arithmetic("JGT")
            case "lt":
                perform_boolean_arithmetic("JLT")
            case "and":
                pop_stack_to_d_register()  # upper value is stored in D
                write("@R13", "M=D")  # D is stored in R13
                pop_stack_to_d_register()  # lower value is stored in D
                write("@R13", "A=M", "D=D&A")  # R13 and D
                push_d_register_to_stack()
            case "or":
                pop_stack_to_d_register()  # upper value is stored in D
                write("@R13", "M=D")  # D is stored in R13
                pop_stack_to_d_register()  # lower value is stored in D
                write("@R13", "A=M", "D=D|A")  # R13 and D
                push_d_register_to_stack()
            case "not":
                pop_stack_to_d_register()  # upper value is stored in D
                write("D=!D")
                push_d_register_to_stack()

    write(f"// --- Translating {vm_command.source} ---")
    match vm_command.command_type:
        case VmCommandType.ARITHMETIC:
            perform_arithmetic(vm_command.arg1)
            return
        case VmCommandType.PUSH:
            write_segment_value_to_d_register(vm_command.arg1, vm_command.arg2)
            write("@SP", "A=M", "M=D", "@SP", "M=M+1")
            return
        case VmCommandType.POP:
            write("@SP", "M=M-1")
            write_sp_to_segment(vm_command.arg1, vm_command.arg2)
            write("@SP", "A=M", "M=0") # set SP to 0, not necessary, #TODO: remove this
            return
        case VmCommandType.LABEL:
            return
        case VmCommandType.GOTO:
            return
        case VmCommandType.IF:
            return
        case VmCommandType.FUNCTION:
            return
        case VmCommandType.RETURN:
            return
        case VmCommandType.CALL:
            return
        case _:
            return
    write("--- ---")
    write("")

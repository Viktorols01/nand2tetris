import Parser.VmCommand as VmCommand


def translate_vm_command_list(file_path, vm_command_list):
    with open(file_path, 'r') as file:
        for vm_command in vm_command_list:
            self._translate_vm_command(
                file, vm_command, file_prefix=file_path.split(".")[0])

    # TODO: Add infinite loop


def _translate_vm_command(file, vm_command, file_prefix):
    def write(*string_list):
        for string in string_list:
            file.write(string + "\n")

    def write_segment_address_to_d_register(segment, i):
        match segment:
            case "constant":
                raise "No address for constants!"
            case "LCL" | "ARG" | "THIS" | "THAT":
                write(f"@{segment}", "D=A", f"@{i}", "D=D+A")
            case "pointer":
                write(f"@{i+3}", "D=A")
            case "temp":
                write(f"@{i+5}", "D=A")
            case "static":
                write(f"@{file_prefix}.{i}")
            case _:
                raise "Undefined segment!"

    def write_segment_value_to_d_register(segment, i):
        match segment:
            case "constant":
                write(f"@{i}", "D=A")
            case _:
                write_segment_address_to_d_register(segment, i)
                write("A=D", "A=M", "D=M")

    def write_sp_to_segment(segment, i):
        # while writing this I noticed that I couldn't use D to simultaneously store the segment address and SP value.
        # if I didn't google the issue (and found someone who came to the same realization), I would've written A=A+1 i times.
        # but what I found on stackoverflow was a reminder that I have access to other registers than D...
        write_segment_address_to_d_register(segment, i)
        write("@R13", "M=D")  # segment address stored in R13
        write(f"@SP", "A=M", "D=M")  # SP value stored in D
        write("@R13", "A=M", "M=D")  # store D in R13 address

    def peform_arithmetic(command):
        match command:
            case "add":
                # plan: move values to R13 and R14, store result in R15
                write("@SP", "M=M-1", "A=M", "D=M", "@R13", "M=D") # upper value is stored in R13
                write("@SP", "M=M-1", "A=M", "D=M", "@R14", "M=D") # lower value is stored in R14
                write("")
            case "sub":
                write("")
            case "neg":
                write("")
            case "eq":
                # remember: -1 is true, 0 is false
                write("")
            case "gt":
                write("")
            case "lt":
                write("")
            case "and":
                write("")
            case "or":
                write("")
            case "not":
                write("")

    write(f"// --- Translating {vm_command.source} ---")
    match vm_command.command_type:
        case ARITHMETIC:
            perform_arithmetic(vm_command.arg1)
        case PUSH:
            write_segment_value_to_d_register(vm_command.arg1, vm_command.arg2)
            write("@SP", "A=M", "M=D", "@SP", "M=M+1")
            return
        case POP:
            write("@SP", "M=M-1")
            write_sp_to_segment(vm_command.arg1, vm_command.arg2)
            return
        case LABEL:
            return
        case GOTO:
            return
        case IF:
            return
        case FUNCTION:
            return
        case RETURN:
            return
        case CALL:
            return
        case _:
            return
    write("--- ---")
    write("")

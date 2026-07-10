from enum import Enum
from dataclasses import dataclass


def get_vm_command_list(file_path):
    vm_command_list = []
    with open(file_path, "r") as file:
        for line in file:
            has_command, vm_command = _get_vm_command(line)
            if has_command:
                vm_command_list.append(vm_command)
    return vm_command_list


def _get_vm_command(line):
    line = line.strip()

    is_empty = line == ""
    is_comment = line.startswith("//")
    if is_empty or is_comment:
        return False, None

    words = line.split(" ")
    command = None
    # TODO: I could replace this with a dictionary
    match words[0]:
        case "push":
            command = VmCommand(line, VmCommandType.PUSH, words[1], words[2])
        case "pop":
            command = VmCommand(line, VmCommandType.POP, words[1], words[2])
        case "label":
            command = VmCommand(line, VmCommandType.LABEL, words[1], None)
        case "goto":
            command = VmCommand(line, VmCommandType.GOTO, words[1], None)
        case "if-goto":
            command = VmCommand(line, VmCommandType.IF_GOTO, words[1], None)
        case "function":
            command = VmCommand(line, VmCommandType.FUNCTION, words[1], words[2])
        case "return":
            command = VmCommand(line, VmCommandType.FUNCTION, None, None)
        case "call":
            command = VmCommand(line, VmCommandType.FUNCTION, words[1], words[2])
        case _:
            # assume arithmetic, will cause errors if source code is wrong
            command = VmCommand(line, VmCommandType.ARITHMETIC, words[0], None)
    return True, command


@dataclass
class VmCommand:
    source: str
    command_type: VmCommandType
    arg1: str
    arg2: int


class VmCommandType(Enum):
    ARITHMETIC = 1
    PUSH = 2
    POP = 3
    LABEL = 4
    GOTO = 5
    IF_GOTO = 6
    FUNCTION = 7
    RETURN = 8
    CALL = 9

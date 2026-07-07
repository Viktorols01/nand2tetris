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
    is_comment = lineline.startswith("//")
    if is_empty or is_comment:
        return False, None

    words = line.split(" ")
    match words[0]:
        case "push":
            return True, VmCommand(line, CommandType.PUSH, words[1], words[2])
        case "pop":
            return True, VmCommand(line, CommandType.POP, words[1], words[2])
        case _:
            # assume arithmetic, will cause errors if source code is wrong
            return True, VmCommand(line, CommandType.ARITHMETIC, words[0], None)


@dataclass
class VmCommand:
    source: str
    command_type: CommandType
    arg1: str
    arg2: int


class CommandType(Enum):
    ARITHMETIC = 1
    PUSH = 2
    POP = 3
    LABEL = 4
    GOTO = 5
    IF = 6
    FUNCTION = 7
    RETURN = 8
    CALL = 9

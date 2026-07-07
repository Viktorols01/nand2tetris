import sys
import Parser
from CodeWriter import CodeWriter


def main():
    file_path_in = sys.argv[1]
    file_path_out = sys.argv[2]
    vm_command_list = Parser.get_vm_command_list(file_path_in)
    CodeWriter.translate_vm_command_list(file_path_out, vm_command_list)


if __name__ == "__main__":
    main()

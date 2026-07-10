import sys
import os
import Parser
import CodeWriter


def main():
    dir_in = sys.argv[1]
    file_path_out = "source.asm"

    with open(file_path_out, "w"):
        write("// Creating new assembly file")

    for file_path_in in os.listdir(dir_in):
        if os.path.isfile(file_path_in):
            vm_command_list = Parser.get_vm_command_list(file_path_in)
            CodeWriter.translate_vm_command_list(file_path_in, file_path_out, vm_command_list)

if __name__ == "__main__":
    main()

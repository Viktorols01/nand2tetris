import sys
import os
import Parser
from CodeWriter import CodeWriter


def main():
    dir_in = sys.argv[1]
    file_path_out = f"{dir_in}/source.asm"

    with open(file_path_out, "w") as file:
        for file_name in os.listdir(dir_in):
            file_suffix = file_name.split(".")[-1]
            file_path_in = dir_in + "/" + file_name
            if file_suffix == "vm" and os.path.isfile(file_path_in):
                vm_command_list = Parser.get_vm_command_list(file_path_in)
                cw = CodeWriter(file)
                cw.translate_vm_command_list(file_path_in, vm_command_list)


if __name__ == "__main__":
    main()

import argparse
import jack_tokenizer as jack_tokenizer
from jack_parser import JackParser
from jack_writer import JackWriter
import os
import shutil
import xml.etree.ElementTree as ET


def main():
    argument_parser = argparse.ArgumentParser(
        prog="python jack_compiler",
        description="Takes jack source code and outputs token files, parse tree files and (eventually) vmcode files.",
    )
    argument_parser.add_argument("-s", "--source_dir", help="input source directory")
    args = argument_parser.parse_args()

    out_dir = f"{args.source_dir}/out"
    token_dir = f"{args.source_dir}/out/tokens"
    parse_dir = f"{args.source_dir}/out/parse_trees"
    vm_dir = f"{args.source_dir}/out/vm_code"
    clear_dirs([out_dir, token_dir, parse_dir, vm_dir])

    for path in os.listdir(args.source_dir):
        file_path = f"{args.source_dir}/{path}"
        if os.path.isdir(file_path) or path.split(".")[-1] != "jack":
            continue

        name = extract_name(file_path)
        tokens = [token for token in jack_tokenizer.tokenize(file_path)]

        output_token_xml_file(tokens, output_file_name=f"{token_dir}/{name}T.xml")

        parser = JackParser(tokens)
        tree = parser.parse()
        output_parse_tree_xml_file(tree, output_file_name=f"{parse_dir}/{name}.xml")

        jack_writer = JackWriter(output_file_name=f"{vm_dir}/{name}.vm")
        jack_writer.write_vm_code(tree)

def extract_name(file_path):
    return file_path.split("/")[-1].split(".")[0]

def clear_dirs(dirs):
    for d in dirs:
        if os.path.isdir(d): shutil.rmtree(d)
        os.mkdir(d)

def output_token_xml_file(tokens, output_file_name):
    root = ET.Element("tokens")
    for token in tokens:
        match token.token_type:
            case jack_tokenizer.TokenType.IDENTIFIER:
                e = ET.SubElement(root, "identifier")
                e.text = " "+token.identifer+" "
            case jack_tokenizer.TokenType.SYMBOL:
                e = ET.SubElement(root, "symbol")
                e.text = " "+token.symbol+" "
            case jack_tokenizer.TokenType.KEYWORD:
                e = ET.SubElement(root, "keyword")
                e.text = " "+token.keyword+" "
            case jack_tokenizer.TokenType.STRING_CONSTANT:
                e = ET.SubElement(root, "stringConstant")
                e.text = " "+token.str_val+" "
            case jack_tokenizer.TokenType.INT_CONSTANT:
                e = ET.SubElement(root, "integerConstant")
                e.text = " "+str(token.int_val)+" "
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    tree.write(output_file_name, encoding="UTF-8")

def output_parse_tree_xml_file(tree, output_file_name):
    # this is just the class
    for child in tree:
        name, value = child
        root = ET.Element(name)
        append_subtree(root, value)
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ", level=0)
        tree.write(output_file_name, encoding="UTF-8", short_empty_elements=False)

def append_subtree(parent, subtree):
    if isinstance(subtree, str):
        parent.text = " " + subtree + " "
    else:
        if len(subtree) == 0:
            parent.text = "\n"
        else:
            for child in subtree:
                name, value = child
                element = ET.SubElement(parent, name)
                append_subtree(element, value)

if __name__ == "__main__":
    main()

import argparse
import jack_tokenizer as jt
import os
import shutil


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
        tokens = [token for token in jt.tokenize(file_path)]

        output_token_xml_file(tokens, output_file_name=f"{token_dir}/{name}T.xml")

        # TODO: Add parser
        #jack_parser = JackParser()
        #jack_parser.parse(tokens, output_file_name=f"{parse_dir}/{name}.xml")

        # TODO: Add code generation

def extract_name(file_path):
    return file_path.split("/")[-1].split(".")[0]

def clear_dirs(dirs):
    for d in dirs:
        if os.path.isdir(d): shutil.rmtree(d)
        os.mkdir(d)

def output_token_xml_file(tokens, output_file_name):
    import xml.etree.ElementTree as ET
    root = ET.Element("tokens")
    for token in tokens:
        match token.token_type:
            case jt.TokenType.IDENTIFIER:
                e = ET.SubElement(root, "identifier")
                e.text = " "+token.identifer+" "
            case jt.TokenType.SYMBOL:
                e = ET.SubElement(root, "symbol")
                e.text = " "+token.symbol+" "
            case jt.TokenType.KEYWORD:
                e = ET.SubElement(root, "keyword")
                e.text = " "+token.keyword+" "
            case jt.TokenType.STRING_CONSTANT:
                e = ET.SubElement(root, "stringConstant")
                e.text = " "+token.str_val+" "
            case jt.TokenType.INT_CONSTANT:
                e = ET.SubElement(root, "integerConstant")
                e.text = " "+str(token.int_val)+" "
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    tree.write(output_file_name, encoding="UTF-8")

if __name__ == "__main__":
    main()

from symbol_table import SymbolTable, SymbolKind

# still rip snake_case and also DAMN is this code utilitarian


class JackWriter:
    def __init__(self, output_file_name):
        self.subroutine_symbol_table = SymbolTable()
        self.class_symbol_table = SymbolTable()
        self.file = open(output_file_name, "w")
        self.file_prefix = output_file_name.split("/")[-1].split(".")[0]
        self.label_n = 0

        def _write(*strings):
            for string in strings:
                print(string)
                self.file.write(f"{string}\n")
        self._write = _write

    def _get_next_label(self):
        self.label_n += 1
        return f"LABEL{self.label_n}"

    def write_vm_code(self, tree):
        class_element = tree[0]
        _, subtree = class_element  # "class", [...]
        for element in subtree:
            name, subsubtree = element
            match name:
                case "identifier":
                    pass  # this is the class name
                case "classVarDec":
                    self._compileClassVarDec(subsubtree)
                case "subroutineDec":
                    self._compileSubroutineDec(subsubtree)
        self.file.flush()
        self.file.close()

    def _compileClassVarDec(self, tree):
        raise "Not implemented"

    def _compileSubroutineDec(self, tree):
        self.subroutine_symbol_table.reset()
        self._write("// compiling subRoutineDec")
        _, subroutine_type = tree[0]  # method, function or constructor
        # TODO: find out whether this needs to be used
        _, return_type = tree[1]
        _, subroutine_name = tree[2]
        _, parameter_list = tree[4]  # TODO: handle and add to symbol table
        _, subroutine_body = tree[6]
        function_label = f"{self.file_prefix}.{subroutine_name}"
        local_variable_count = self._countLocalVariables(subroutine_body)
        match subroutine_type:
            case "method":
                local_variable_count += 1
            case "function":
                pass
            case "constructor":
                raise "Not implemented"  # TODO: implement
            case _:
                raise "Unknown subroutine type"
        self._write(f"function {function_label} {local_variable_count}")
        self._appendParameterListToSymbolTable(
            parameter_list, self.subroutine_symbol_table)
        self._compileSubroutineBody(subroutine_body)

    def _appendParameterListToSymbolTable(self, parameter_list, symbol_table):
        i = 0
        while i < len(parameter_list):
            # might be (char|int|boolean) or className
            identifier_type = parameter_list[i][1]
            identifier_name = parameter_list[i + 1][1]
            symbol_table.add_symbol(
                identifier_name, identifier_type, SymbolKind.ARG)
            i += 3

    def _countLocalVariables(self, subroutine_body):
        counter = 0
        for element in subroutine_body:
            name, value = element
            if name == "varDec":
                counter += 1
                for sub_element in value:
                    sub_name, sub_value = sub_element
                    if sub_name == "symbol" and sub_value == ",":
                        counter += 1
        return counter

    def _compileSubroutineBody(self, subroutine_body):
        self._write("// compiling subRoutineDec")
        for element in subroutine_body:
            name, value = element
            match name:
                case "symbol":
                    continue
                case "varDec":
                    self._compileVarDec(value)
                case "statements":
                    self._compileStatements(value)

    def _compileVarDec(self, tree):
        self._write("// compiling varDec")
        self._write("// (we're just adding stuff to the symbol table)")
        # always one variable defined
        _, var_type = tree[1]  # might be (char|int|boolean) or className
        _, identifier = tree[2]  # identifier, (identifier)
        self.subroutine_symbol_table.add_symbol(
            identifier, var_type, SymbolKind.VAR)
        i = 4
        while i < len(parameter_list):
            _, identifier = tree[i]  # identifier, (identifier)
            self.subroutine_symbol_table.add_symbol(
                identifier, var_type, SymbolKind.VAR)
            i += 2

    def _compileStatements(self, tree):
        self._write("// compiling statements")
        for statement in tree:
            statement_type, subtree = statement
            self._write(f"// compiling {statement_type}")
            match statement_type:
                case "letStatement":
                    self._compileLetStatement(subtree)
                case "ifStatement":
                    self._compileIfStatement(subtree)
                case "whileStatement":
                    self._compileWhileStatement(subtree)
                case "doStatement":
                    self._compileDoStatement(subtree)
                case "returnStatement":
                    self._compileReturnStatement(subtree)
                case "_":
                    raise "Unknown statement"

    def _compileLetStatement(self, tree):
        # TODO: add support for arrays
        pass

    def _compileIfStatement(self, tree):
        _, expression = tree[2]
        _, statements = tree[5]
        has_else_statement = len(tree) > 8
        if has_else_statement:
            _, else_statements = tree[9]
        if_label = self._get_next_label()
        end_label = self._get_next_label()
        self._compileExpression(expression)
        self._write(f"if-goto {if_label}")
        if has_else_statement:
            self._compileStatements(else_statements)
        self._write(f"goto {end_label}")
        self._write(f"label {if_label}")
        self._compileStatements(statements)
        self._write(f"label {end_label}")

        pass

    def _compileWhileStatement(self, tree):
        _, expression = tree[2]
        _, statements = tree[5]
        first_label = self._get_next_label()
        loop_label = self._get_next_label()
        self._write(f"goto {first_label}")
        self._write(f"label {loop_label}")
        self._compileStatements(statements)
        self._write(f"label {first_label}")
        self._compileExpression(expression)
        self._write(f"if-goto {loop_label}")

    def _compileDoStatement(self, tree):
        tree = tree[1:-1]  # remove do and ;
        self._compileTerm(tree)

    def _compileReturnStatement(self, tree):
        # TODO: support returning expressions...
        self._write("return")

    def _compileExpression(self, tree):
        # ultimately should push a value onto the stack?
        pass

    def _compileTerm(self, tree):
        # ultimately should push a value onto the stack?
        pass
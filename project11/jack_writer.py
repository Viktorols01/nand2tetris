from symbol_table import SymbolTable, SymbolKind

# still rip snake_case and also DAMN is this code utilitarian


class JackWriter:
    def __init__(self, output_file_name):
        self.subroutine_symbol_table = SymbolTable()
        self.class_symbol_table = SymbolTable()
        self.file = open(output_file_name, "w")
        # note: this should be the same as class prefix
        self.file_prefix = output_file_name.split("/")[-1].split(".")[0]
        self.non_method_map = {}  # just to check if a function is a function and not a method
        self.label_n = 0

        def _write(*strings):
            for string in strings:
                print(string)
                self.file.write(f"{string}\n")
        self._write = _write

    def _get_symbol(self, name):
        if self.subroutine_symbol_table.contains_symbol(name):
            return self.subroutine_symbol_table.get_symbol(name)
        else:
            return self.class_symbol_table.get_symbol(name)

    def _get_segment(self, name):
        symbol = self._get_symbol(name)
        return symbol.get_segment()

    def _is_in_symbol_table(self, name):
        return self._get_symbol(name) is not None

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
                    pass  # should just be class name
                case "classVarDec":
                    self._compileClassVarDec(subsubtree)
                case "subroutineDec":
                    self._compileSubroutineDec(subsubtree)
        self.file.flush()
        self.file.close()

    def _compileClassVarDec(self, tree):
        _, static_or_field = tree[0]
        _, tha_type_babyy = tree[1]
        _, first_name = tree[2]
        kind = SymbolKind.STATIC if static_or_field == "static" else SymbolKind.FIELD
        self.class_symbol_table.add_symbol(first_name, tha_type_babyy, kind)
        i = 4
        while i < len(tree):
            _, name = tree[i]
            self.class_symbol_table.add_symbol(name, tha_type_babyy, kind)
            i += 2

    def _compileSubroutineDec(self, tree):
        self.subroutine_symbol_table.reset()
        _, subroutine_type = tree[0]  # method, function or constructor
        _, return_type = tree[1]
        _, subroutine_name = tree[2]
        _, parameter_list = tree[4]
        _, subroutine_body = tree[6]
        function_label = f"{self.file_prefix}.{subroutine_name}"
        local_variable_count = self._countLocalVariables(subroutine_body)
        if subroutine_type == "method":
            local_variable_count += 1
            self.subroutine_symbol_table.add_symbol(
                "this", self.file_prefix, SymbolKind.ARG)
        else:
            self.non_method_map[subroutine_name] = True
        self._write(f"function {function_label} {local_variable_count}")
        if subroutine_type == "method":
            field_variable_count = self.class_symbol_table.get_field_variable_count()
            self._write(f"push argument 0")
            self._write(f"pop pointer 0")
        if subroutine_type == "constructor":
            field_variable_count = self.class_symbol_table.get_field_variable_count()
            self._write(f"push constant {field_variable_count}")
            self._write(f"call Memory.alloc 1")
            self._write(f"pop pointer 0")
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
        # always one variable defined
        _, var_type = tree[1]  # might be (char|int|boolean) or className
        _, identifier = tree[2]  # identifier, (identifier)
        self.subroutine_symbol_table.add_symbol(
            identifier, var_type, SymbolKind.VAR)
        i = 4
        while i < len(tree):
            _, identifier = tree[i]  # identifier, (identifier)
            self.subroutine_symbol_table.add_symbol(
                identifier, var_type, SymbolKind.VAR)
            i += 2

    def _compileStatements(self, tree):
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
        if len(tree) == 5:
            _, identifier = tree[1]
            _, expression = tree[3]
            segment = self._get_segment(identifier)
            self._compileExpression(expression)
            self._write(f"pop {segment}")
        else:
            _, identifier = tree[1]
            _, expression1 = tree[3]
            _, expression2 = tree[6]
            segment = self._get_segment(identifier) # arr
            self._write(f"push {segment}")
            self._compileExpression(expression1)
            self._write("add")
            self._compileExpression(expression2)
            self._write("pop temp 2")
            self._write("pop pointer 1") # set pointer 1 to arr + expression1
            self._write("push temp 2")
            self._write("pop that 0")

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
        # book says expression, I say term until I encounter problems
        self._compileTerm(tree)
        self._write("pop temp 0")  # remove pushed value

    def _compileReturnStatement(self, tree):
        if len(tree) == 2:  # just a return
            # TODO: the book says it's a convention to always push some value to the stack. Fix this if I encounter issues.
            self._write("return")
        else:
            _, expression = tree[1]
            self._compileExpression(expression)
            self._write("return")

    def _compileExpression(self, tree):
        # ultimately should push a value onto the stack?
        _, first_term = tree[0]
        self._compileTerm(first_term)
        i = 1
        while i < len(tree):
            _, symbol = tree[i]
            _, term = tree[i + 1]
            self._compileTerm(term)
            self._compileOperation(symbol)
            i += 2

    def _compileOperation(self, symbol):
        symbol_to_operation = {
            '+': "add",
            '-': "sub",
            '*': "call Math.multiply 2",
            '/': "call Math.divide 2",
            '&': "and",
            '|': "or",
            '<': "lt",
            '>': "gt",
            '=': "eq"
        }
        operation = symbol_to_operation[symbol]
        self._write(operation)

    def _compileTerm(self, tree):
        # ultimately should push a value onto the stack?
        first_type, first_value = tree[0]
        match first_type:
            case "integerConstant":
                self._write(f"push constant {first_value}")
            case "stringConstant":
                self._write(f"push constant {len(first_value)}")
                self._write(f"call String.new 1")
                for char in first_value:
                    self._write(f"push constant {ord(char)}")
                    self._write(f"call String.appendChar 2")
            case "keyword":
                match first_value:
                    case "true":
                        self._write(f"push constant 1")
                        self._write(f"neg")
                    case "false":
                        self._write(f"push constant 0")
                    case "null":
                        self._write(f"push constant 0")
                    case 'this':
                        self._write("push pointer 0")
            case "symbol":
                if first_value == "(":
                    _, expression = tree[1]
                    self._compileExpression(expression)
                else:
                    # must be unary operator
                    _, term = tree[1]
                    self._compileTerm(term)
                    symbol_to_operation = {
                        '-': "neg",
                        '~': "not"
                    }
                    operation = symbol_to_operation[first_value]
                    self._write(operation)
            case "identifier":
                self._compileIdentifierTerm(tree)

    def _compileIdentifierTerm(self, tree):
        _, first_identifier = tree[0]
        # varName
        if len(tree) == 1:
            is_not_method = not self._is_in_symbol_table("this")
            if first_identifier == "this" and is_not_method:  # for "return this" in constructors
                self._write(f"push pointer 0")
                return

            segment = self._get_segment(first_identifier)
            self._write(f"push {segment}")
            return

        first_symbol = tree[1][1]
        if first_symbol == '[':
            _, expression = tree[2]
            segment = self._get_segment(first_identifier)
            self._write(f"push {segment}")
            self._compileExpression(expression)
            self._write("add")
            self._write("pop pointer 1")
            self._write("push that 0")
        # subroutineCall
        self._compileSubroutineCallTerm(tree)

    def _compileSubroutineCallTerm(self, tree):
        self._write("// compiling subroutine call")
        first_identifier = tree[0][1]
        first_symbol = tree[1][1]
        # subroutineName(expressionList)
        if first_symbol == '(':
            expression_list = tree[2][1]
            expression_count = self._compileExpressionList(expression_list)
            if first_identifier in self.non_method_map:
                self._write(
                    f"call {self.file_prefix}.{first_identifier} {expression_count}")
            else:
                self._write(f"push pointer 0")
                self._write(
                    f"call {self.file_prefix}.{first_identifier} {expression_count + 1}")
        # (className|varName).subroutineName(expressionList)
        if first_symbol == '.':
            second_identifier = tree[2][1]
            expression_list = tree[4][1]

            symbol = self._get_symbol(first_identifier)
            symbol_exists = symbol is not None
            if symbol_exists:
                # calling a method on an object with name varName
                class_name_of_var = symbol.symbol_type
                self._write(f"push {symbol.get_segment()}")
                expression_count = self._compileExpressionList(expression_list)
                self._write(
                    f"call {class_name_of_var}.{second_identifier} {expression_count + 1}")
            else:
                # calling a static function of another class
                expression_count = self._compileExpressionList(expression_list)
                self._write(
                    f"call {first_identifier}.{second_identifier} {expression_count}")

    def _compileExpressionList(self, tree):
        # put a looot of values on the stack
        expression_count = 0
        i = 0
        while i < len(tree):
            _, expression = tree[i]
            self._compileExpression(expression)
            expression_count += 1
            i += 2
        return expression_count

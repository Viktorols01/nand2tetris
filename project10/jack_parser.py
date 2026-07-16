from dataclasses import dataclass
from typing import List
from jack_tokenizer import Token, TokenType, Keyword

# RIP snake_case for some reason


''' goal stucture:
{ 
    "class": {
        "keyword": "class",
        "className": "main",
        "symbol": "{",
        "classVarDec": { ... },
        "classVarDec": { ... },
        "subroutineDec": { ... },
        "symbol": "}"
    }
}
'''


# (compilationengine)
class JackParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0

    def parse(self):
        structure = []
        structure.append(self._consumeClass())
        return structure

    def _consumeToken(self, token_type, *optional_assert):
        current_token = self.tokens[self.i]
        print("expecting", token_type, "|", optional_assert)
        print("got", current_token)
        assert current_token.token_type == token_type
        self.i += 1
        name = token_type.value
        match current_token.token_type:
            case TokenType.KEYWORD:
                assert current_token.keyword in optional_assert
                value = current_token.keyword.value
            case TokenType.SYMBOL:
                assert current_token.symbol in optional_assert
                value = current_token.symbol
            case TokenType.IDENTIFIER:
                value = current_token.identifer
            case TokenType.INT_CONSTANT:
                value = current_token.int_val
            case TokenType.STRING_CONSTANT:
                value = current_token.str_val
        return (name, value)

    def _consumeClass(self):
        name = "class"
        structure = []
        structure.append(self._consumeToken(TokenType.KEYWORD, Keyword.CLASS))
        structure.append(self._consumeToken(TokenType.IDENTIFIER))
        structure.append(self._consumeToken(TokenType.SYMBOL, "{"))
        while True:
            next_token = self.tokens[self.i]
            if next_token.token_type == TokenType.KEYWORD:
                if next_token.keyword in [Keyword.FIELD, Keyword.STATIC]:
                    structure.append(self._consumeClassVarDec())
                    continue
                if next_token.keyword in [Keyword.FUNCTION, Keyword.CONSTRUCTOR, Keyword.METHOD]:
                    structure.append(self._consumeSubroutineDec())
                    continue
            break
        structure.append(self._consumeToken(TokenType.SYMBOL, "}"))
        return (name, structure)

    def _consumeClassVarDec(self):
        name = "classVarDec"
        structure = []
        structure.append(self._consumeToken(
            TokenType.KEYWORD, Keyword.STATIC, Keyword.FIELD))
        structure.append(self._consumeType())
        structure.append(self._consumeVarName())
        while True:
            next_token = self.tokens[self.i]
            assert next_token.token_type == TokenType.SYMBOL
            if next_token.symbol == ",":
                structure.append(self._consumeToken(TokenType.SYMBOL, ","))
                structure.append(self._consumeVarName())
            else:
                break
        structure.append(self._consumeToken(TokenType.SYMBOL,  ";"))
        return (name, structure)

    def _consumeType(self):
        next_token = self.tokens[self.i]
        if next_token.token_type == TokenType.IDENTIFIER:
            return self._consumeClassName()
        else:
            return self._consumeToken(TokenType.KEYWORD, Keyword.INT, Keyword.CHAR, Keyword.BOOLEAN)

    def _consumeVarName(self):
        return self._consumeToken(TokenType.IDENTIFIER)

    def _consumeClassName(self):
        return self._consumeToken(TokenType.IDENTIFIER)

    def _consumeClassNameOrVarName(self):
        return self._consumeToken(TokenType.IDENTIFIER)

    def _consumeClassName(self):
        return self._consumeToken(TokenType.IDENTIFIER)

    def _consumeSubroutineName(self):
        return self._consumeToken(TokenType.IDENTIFIER)

    def _consumeSubroutineDec(self):
        name = "subroutineDec"
        structure = []
        structure.append(self._consumeToken(
            TokenType.KEYWORD, Keyword.CONSTRUCTOR, Keyword.FUNCTION, Keyword.METHOD))
        structure.append(self._consumeVoidOrType())
        structure.append(self._consumeSubroutineName())
        structure.append(self._consumeToken(TokenType.SYMBOL, "("))
        structure.append(self._consumeParameterList())
        structure.append(self._consumeToken(TokenType.SYMBOL, ")"))
        structure.append(self._consumeSubroutineBody())
        return (name, structure)

    def _consumeVoidOrType(self):
        next_token = self.tokens[self.i]
        if next_token.token_type == TokenType.KEYWORD:
            return self._consumeToken(TokenType.KEYWORD, Keyword.VOID)
        else:
            return self._consumeType()

    def _consumeParameterList(self):
        name = "parameterList"
        structure = []
        next_token = self.tokens[self.i]
        if next_token.token_type == TokenType.SYMBOL and next_token.symbol == ")": # parameterlist always followed by )
            return name, structure
        while True:
            next_token = self.tokens[self.i]
            structure.append(self._consumeType())
            structure.append(self._consumeVarName())
            next_token = self.tokens[self.i]
            if next_token.token_type == TokenType.SYMBOL and next_token.symbol == ",":
                structure.append(self._consumeToken(TokenType.SYMBOL, ","))
            else:
                break
        return name, structure

    def _consumeSubroutineBody(self):
        name = "subroutineBody"
        structure = []
        structure.append(self._consumeToken(TokenType.SYMBOL, "{"))
        while self.tokens[self.i].keyword == Keyword.VAR:
            structure.append(self._consumeVarDec())
        structure.append(self._consumeStatements())
        structure.append(self._consumeToken(TokenType.SYMBOL, "}"))
        return (name, structure)

    def _consumeVarDec(self):
        name = "varDec"
        structure = []
        structure.append(self._consumeToken(TokenType.KEYWORD, Keyword.VAR))
        structure.append(self._consumeType())
        structure.append(self._consumeVarName())
        while True:
            next_token = self.tokens[self.i]
            assert next_token.token_type == TokenType.SYMBOL
            if next_token.symbol == ',':
                structure.append(self._consumeToken(TokenType.SYMBOL, ','))
                structure.append(self._consumeVarName())
            else:
                structure.append(self._consumeToken(TokenType.SYMBOL, ';'))
                break
        return (name, structure)

    def _consumeStatements(self):
        name = "statements"
        structure = []
        while True:
            next_token = self.tokens[self.i]
            if next_token.token_type != TokenType.KEYWORD:
                break
            match next_token.keyword:
                case Keyword.LET:
                    structure.append(self._consumeLetStatement())
                case Keyword.IF:
                    structure.append(self._consumeIfStatement())
                case Keyword.WHILE:
                    structure.append(self._consumeWhileStatement())
                case Keyword.DO:
                    structure.append(self._consumeDoStatement())
                case Keyword.RETURN:
                    structure.append(self._consumeReturnStatement())
                case _:
                    break
        return (name, structure)

    def _consumeLetStatement(self):
        name = "letStatement"
        structure = []
        structure.append(self._consumeToken(TokenType.KEYWORD, Keyword.LET))
        structure.append(self._consumeVarName())
        # TODO: Support array stuff
        structure.append(self._consumeToken(TokenType.SYMBOL, "="))
        structure.append(self._consumeExpression())
        structure.append(self._consumeToken(TokenType.SYMBOL, ";"))
        return (name, structure)

    def _consumeIfStatement(self):
        name = "ifStatement"
        structure = []
        structure.append(self._consumeToken(TokenType.KEYWORD, Keyword.IF))
        structure.append(self._consumeToken(TokenType.SYMBOL, "("))
        structure.append(self._consumeExpression())
        structure.append(self._consumeToken(TokenType.SYMBOL, ")"))
        structure.append(self._consumeToken(TokenType.SYMBOL, "{"))
        structure.append(self._consumeStatements())
        structure.append(self._consumeToken(TokenType.SYMBOL, "}"))
        next_token = self.tokens[self.i]
        if next_token.token_type == TokenType.KEYWORD and next_token.keyword == Keyword.ELSE:
            structure.append(self._consumeToken(
                TokenType.KEYWORD, Keyword.ELSE))
            structure.append(self._consumeToken(TokenType.SYMBOL, "{"))
            structure.append(self._consumeStatements())
            structure.append(self._consumeToken(TokenType.SYMBOL, "}"))
        return (name, structure)

    def _consumeWhileStatement(self):
        name = "whileStatement"
        structure = []
        structure.append(self._consumeToken(TokenType.KEYWORD, Keyword.WHILE))
        structure.append(self._consumeToken(TokenType.SYMBOL, "("))
        structure.append(self._consumeExpression())
        structure.append(self._consumeToken(TokenType.SYMBOL, ")"))
        structure.append(self._consumeToken(TokenType.SYMBOL, "{"))
        structure.append(self._consumeStatements())
        structure.append(self._consumeToken(TokenType.SYMBOL, "}"))
        return (name, structure)

    def _consumeDoStatement(self):
        name = "doStatement"
        structure = []
        structure.append(self._consumeToken(TokenType.KEYWORD, Keyword.DO))
        structure.extend(self._consumeSubroutineCall())  # term includes subroutineCall! special case, see book
        structure.append(self._consumeToken(TokenType.SYMBOL, ";"))
        return (name, structure)

    def _consumeReturnStatement(self):
        name = "returnStatement"
        structure = []
        structure.append(self._consumeToken(TokenType.KEYWORD, Keyword.RETURN))
        next_token = self.tokens[self.i]
        if not (next_token.token_type == TokenType.SYMBOL and next_token.symbol == ";"):
            structure.append(self._consumeExpression())
        structure.append(self._consumeToken(TokenType.SYMBOL, ";"))
        return (name, structure)

    def _consumeTerm(self):
        name = "term"
        structure = []
        next_token = self.tokens[self.i]
        match next_token.token_type:
            case TokenType.INT_CONSTANT:
                structure.append(self._consumeToken(
                    TokenType.INT_CONSTANT, next_token.int_val))
            case TokenType.STRING_CONSTANT:
                structure.append(self._consumeToken(
                    TokenType.STRING_CONSTANT, next_token.str_val))
            case TokenType.KEYWORD:
                assert next_token.keyword in [
                    Keyword.TRUE, Keyword.FALSE, Keyword.NULL, Keyword.THIS]
                structure.append(self._consumeToken(
                    TokenType.KEYWORD, next_token.keyword))
            case TokenType.SYMBOL:
                if next_token.symbol in ['-', '~']:
                    structure.append(self._consumeToken(
                        TokenType.SYMBOL, next_token.symbol))
                    structure.append(self._consumeTerm())
                else:
                    assert next_token.symbol == '('
                    structure.append(self._consumeToken(TokenType.SYMBOL, '('))
                    structure.append(self._consumeExpression())
                    structure.append(self._consumeToken(TokenType.SYMBOL, ')'))
            case TokenType.IDENTIFIER:
                next_next_token = self.tokens[self.i + 1]
                assert next_next_token.token_type == TokenType.SYMBOL

                match next_next_token.symbol:
                    case '.':
                        # subroutineCall using className | varName
                        structure.append(self._consumeClassNameOrVarName())
                        structure.append(
                            self._consumeToken(TokenType.SYMBOL, '.'))
                        structure.append(self._consumeSubroutineName())
                        structure.append(
                            self._consumeToken(TokenType.SYMBOL, '('))
                        structure.append(self._consumeExpressionList())
                        structure.append(
                            self._consumeToken(TokenType.SYMBOL, ')'))
                    case '(':
                        # subroutineCall using subroutineName
                        structure.append(self._consumeSubroutineName())
                        structure.append(
                            self._consumeToken(TokenType.SYMBOL, '('))
                        structure.append(self._consumeExpressionList())
                        structure.append(
                            self._consumeToken(TokenType.SYMBOL, ')'))
                    case '[':
                        # TODO: implement array stuff
                        raise "Not implemented"
                    case _:
                        structure.append(self._consumeVarName())
        return (name, structure)

    def _consumeExpressionList(self):
        name = "expressionList"
        structure = []
        while True:
            next_token = self.tokens[self.i]
            # lucky for us, expressionList is always followed by ')'
            if next_token.token_type == TokenType.SYMBOL and next_token.symbol == ')':
                break
            structure.append(self._consumeExpression())
            next_token = self.tokens[self.i]
            if next_token.token_type == TokenType.SYMBOL and next_token.symbol == ',':
                structure.append(self._consumeToken(TokenType.SYMBOL, ','))

        return (name, structure)

    def _consumeExpression(self):
        name = "expression"
        structure = []
        structure.append(self._consumeTerm())
        operation_symbols = list("+-*/&|<>=")
        while True:
            next_token = self.tokens[self.i]
            if next_token.token_type == TokenType.SYMBOL and next_token.symbol in operation_symbols:
                structure.append(self._consumeToken(TokenType.SYMBOL))
                structure.append(self._consumeTerm())
            else:
                break
        return (name, structure)
    
    def _consumeSubroutineCall(self):
        name, structure = self._consumeTerm()
        return structure
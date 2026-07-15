from dataclasses import dataclass
from typing import List
from jack_tokenizer import Token, TokenType, Keyword


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
            case TokenType.STRING_CONSTANT_CONSTANT:
                value = current_token.str_val
        return (name, value)

    def _consumeClass(self):
        name = "class"
        structure = []
        structure.append(self._consumeToken(TokenType.KEYWORD, Keyword.CLASS))
        structure.append(self._consumeToken(TokenType.IDENTIFIER))
        structure.append(self._consumeToken(TokenType.SYMBOL, "{"))
        while True:
            next_token = self.tokens[i + 1]
            if next_token.token_type == TokenType.KEYWORD:
                if next_token.keyword in ["field", "static"]:
                    structure.append(self._consumeClassVarDec())
                    continue
                if next_token.keyword in ["constructor", "method"]:
                    structure.append(self._consumeSubroutineDec())
                    continue
            break
        structure.append(self._consumeToken(TokenType.SYMBOL, "}"))
        return (name, structure)

    def _consumeClassVarDec(self):
        name = "classVarDec"
        structure = []
        structure.append(self._consumeToken(TokenType.KEYWORD, Keyword.STATIC, Keyword.FIELD))
        structure.append(self._consumeType())
        structure.append(self._consumeVarName())
        assert next_token.token_type == TokenType.SYMBOL
        while True:
            next_token = self.tokens[i + 1]
            if next_token.symbol == ",":
                structure.append(self._consumeToken(TokenType.SYMBOL, ","))
                structure.append(self._consumeVarName())
            else:
                break
        structure.append(self._consumeToken(TokenType.SYMBOL,  ";"))
        return (name, structure)
    
    def _consumeType(self):
        next_token = self.tokens[i + 1]
        if next_token.token_type == TokenType.IDENTIFIER:
            return self._consumeClassName()
        else:
            return self._consumeToken(TokenType.KEYWORD, Keyword.INT, Keyword.CHAR, Keyword.BOOLEAN)
    
    def _consumeVarName(self):
        return self._consumeToken(TokenType.IDENTIFIER)
    
    def _consumeClassName(self):
        return self._consumeToken(TokenType.IDENTIFIER)
    
    def _consumeSubroutineName(self):
        return self._consumeToken(TokenType.IDENTIFIER)

    def _consumeSubroutineDec(self):
        name = "subroutineDec"
        structure = []
        structure.append(self._consumeToken(TokenType.KEYWORD, Keyword.CONSTRUCTOR, Keyword.FUNCTION, Keyword.METHOD))
        structure.append(self._consumeVoidOrType())
        structure.append(self._consumeSubroutineName())
        structure.append(self._consumeToken(TokenType.SYMBOL, "("))
        structure.append(self._consumeParameterList())
        structure.append(self._consumeToken(TokenType.SYMBOL, ")"))
        structure.append(self._consumeSubroutineBody())
        return (name, value)
    
    def _consumeVoidOrType(self):
        next_token = self.tokens[i + 1]
        if next_token.token_type == TokenType.KEYWORD:
            return self._consumeToken(TokenType.VOID)
        else:
            return self._consumeType()

    def _consumeParameterList(self):
        pass

    def _consumeSubroutineBody(self):
        name = "subroutineBody"
        structure = []
        structure.append(self._consumeToken(TokenType.SYMBOL, "{"))
        while self.tokens[i + 1].keyword == Keyword.VAR:
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
        return (name, structure)

    def _consumeStatements(self):
        pass

    def _consumeLet(self):
        pass

    def _consumeIf(self):
        pass

    def _consumeWhile(self):
        pass

    def _consumeDo(self):
        pass

    def _consumeReturn(self):
        pass

    def _consumeExpression(self):
        pass

    def _consumeTerm(self):
        pass

    def _consumeExpressionList(self):
        pass

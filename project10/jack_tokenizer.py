from enum import StrEnum, auto
from dataclasses import dataclass
from peekable_file import PeekableFile

# comment types: //, /* */, /** */

# generator function


def tokenize(file_path):
    with open(file_path, 'r') as file:
        file = PeekableFile(file)
        tokenizer_state = TokenizerState.UNKNOWN
        current = ""
        tog = False
    
        def reset_state():
            nonlocal tokenizer_state, current
            tokenizer_state = TokenizerState.UNKNOWN
            current = ""

        while True:
            match tokenizer_state:
                case TokenizerState.UNKNOWN:
                    if _skip_comments(file):
                        continue

                    char = file.read()
                    if char == "":
                        return # finished
                    elif char in [" ", "\n", "\t", "\r"]: # forgot \t here, wasted an hour...
                        continue
                    elif _is_symbol(char):
                        yield Token(TokenType.SYMBOL, None, char, None, None, None)
                    elif char == '"':
                        tokenizer_state = TokenizerState.STRING_CONSTANT
                    elif char.isnumeric():
                        tokenizer_state = TokenizerState.INT_CONSTANT
                        current += char
                    else:
                        tokenizer_state = TokenizerState.KEYWORD_OR_IDENTIFIER
                        current += char
                case TokenizerState.KEYWORD_OR_IDENTIFIER:
                    char = file.peek()
                    if _is_limiter(char):
                        token = _word_to_keyword_or_identifier(current)
                        yield token
                        reset_state()
                    else:
                        current += char
                        file.read()
                case TokenizerState.INT_CONSTANT:
                    char = file.peek()
                    if char.isnumeric():
                        current += char
                        file.read()
                    else:
                        yield Token(TokenType.INT_CONSTANT, None, None, int(current), None, None)
                        reset_state()
                case TokenizerState.STRING_CONSTANT:
                    char = file.read()
                    if char == '"':
                        yield Token(TokenType.STRING_CONSTANT, None, None, None, current, None)
                        reset_state()
                    else:
                        current += char



class TokenizerState(StrEnum):
    UNKNOWN = auto(),
    INT_CONSTANT = auto(),
    STRING_CONSTANT = auto(),
    KEYWORD_OR_IDENTIFIER = auto(),


def _word_to_keyword_or_identifier(word):
    if word.upper() in Keyword.__members__:
        keyword = Keyword[word.upper()]
        return Token(TokenType.KEYWORD, keyword, None, None, None, None)
    else:
        return Token(TokenType.IDENTIFIER, None, None, None, None, word)


def _skip_comments(file):
    double_char = file.peek(2)
    if double_char == "//":
        file.read(2)
        _skip_line(file)
        return True
    if double_char == "/*":
        file.read(2)
        _skip_until_comment_end(file)
        return True
    return False


def _skip_line(file):
    file.readline()


def _skip_until_comment_end(file):
    while True:
        double_char = file.peek(2)
        if double_char == "*/":
            file.read(2)
            return
        elif double_char == "":
            return
        else:
            file.read(1)


def _is_limiter(char):
    return _is_symbol(char) or _is_whitespace(char)


def _is_symbol(char):
    return char in jack_symbols


def _is_whitespace(char):
    return char == ' '


jack_symbols = list(r"{}()[].,;+-*/&|<>=~")


@dataclass
class Token:
    token_type: TokenType
    keyword: Keyword
    symbol: str
    int_val: int
    str_val: str
    identifer: str


class TokenType(StrEnum):
    KEYWORD = auto(),
    SYMBOL = auto(),
    INT_CONSTANT = auto(),
    STRING_CONSTANT = auto(),
    IDENTIFIER = auto()


class Keyword(StrEnum):
    CLASS = auto(),
    CONSTRUCTOR = auto(),
    FUNCTION = auto(),
    METHOD = auto(),
    FIELD = auto(),
    STATIC = auto(),
    VAR = auto(),
    INT = auto(),
    CHAR = auto(),
    BOOLEAN = auto(),
    VOID = auto(),
    TRUE = auto(),
    FALSE = auto(),
    NULL = auto(),
    THIS = auto(),
    LET = auto(),
    DO = auto(),
    IF = auto(),
    ELSE = auto(),
    WHILE = auto(),
    RETURN = auto()

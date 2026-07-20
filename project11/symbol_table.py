from dataclasses import dataclass
from enum import StrEnum, auto

class SymbolTable:
    def __init__(self):
        self.reset()

    def reset(self):
        self.table = {}
        self.field_index = 0
        self.static_index = 0
        self.arg_index = 0
        self.var_index = 0
    
    def add_symbol(self, name, symbol_type, kind):
        number = None
        kind_to_index_attr = {
            SymbolKind.FIELD: "field_index",
            SymbolKind.STATIC: "static_index",
            SymbolKind.ARG:   "arg_index",
            SymbolKind.VAR:   "var_index",
        }
        index_attr = kind_to_index_attr[kind]
        number = getattr(self, index_attr)
        setattr(self, index_attr, number + 1)
        self.table[name] = Symbol(name, symbol_type, kind, number)
    
    def contains_symbol(self, name):
        return name in self.table
    
    def get_symbol(self, name):
        return self.table.get(name)
    
    def get_field_variable_count(self):
        counter = 0
        for symbol_name in self.table:
            symbol = self.table[symbol_name]
            if symbol.kind == SymbolKind.FIELD:
                counter += 1
        return counter

@dataclass
class Symbol:
    name: str
    symbol_type: str # int, char, boolean, class
    kind: SymbolKind # field, static, arg, var
    number: int
    def get_segment(self):
        kind_to_specifier = {
            SymbolKind.FIELD: "this",
            SymbolKind.STATIC: "static",
            SymbolKind.ARG:   "argument",
            SymbolKind.VAR:   "local",
        }
        specifier = kind_to_specifier[self.kind]
        return f"{specifier} {self.number}"

class SymbolKind(StrEnum):
    FIELD = auto()
    STATIC = auto()
    ARG = auto()
    VAR = auto()
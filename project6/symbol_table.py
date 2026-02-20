# glorified hashmap
class SymbolTable:
    def __init__(self):
        self.map = {}
        self.next_ram_address = 16
        self._set_predefined_symbols()
    
    def _set_predefined_symbols(self):
        for i in range(16):
            self.set_address(f"R{i}", i)
        i = 0
        for symbol in ["SCP", "LCL", "ARG", "THIS"]:
            self.set_address(symbol, i)
            i += 1

    def get_address(self, symbol):
        return self.map[symbol]

    def set_address(self, symbol, value):
        self.map[symbol] = value

    def generate_and_set_address(self, symbol):
        self.map[symbol] = self.next_ram_address
        self.next_ram_address += 1

    def contains_symbol(self, symbol):
        return symbol in self.map

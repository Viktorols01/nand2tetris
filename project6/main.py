from assembler import Assembler

assembler = Assembler()
source = assembler.translate_file("Test.asm", "nowhere now")
print(source)
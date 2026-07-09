test_name=SimpleAdd
python translate_bytecode.py test/$test_name/$test_name.vm test/$test_name/out/$test_name.asm
test_name=StackTest
python translate_bytecode.py test/$test_name/$test_name.vm test/$test_name/out/$test_name.asm
test_name=BasicTest
python translate_bytecode.py test/$test_name/$test_name.vm test/$test_name/out/$test_name.asm
test_name=PointerTest
python translate_bytecode.py test/$test_name/$test_name.vm test/$test_name/out/$test_name.asm
test_name=StaticTest
python translate_bytecode.py test/$test_name/$test_name.vm test/$test_name/out/$test_name.asm

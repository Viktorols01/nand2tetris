# I don't bother to use some website to compare xml files
test() {
    test_name=$1
    file_name=$2
    python jack_compiler.py -s test/$test_name # inefficient but I'm lazy
    xmllint --format "test/$test_name/out/tokens/$file_name.xml" > f1.xml
    xmllint --format "test/$test_name/$file_name.xml" > f2.xml
    diff -u f1.xml f2.xml
    rm f1.xml
    rm f2.xml
}

test ArrayTest MainT
test ExpressionLessSquare MainT
test ExpressionLessSquare SquareT
test ExpressionLessSquare SquareGameT
test Square MainT
test Square SquareT
test Square SquareGameT

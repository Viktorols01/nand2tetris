# there were problems with the formatting... previous method didn't work
test() {
    test_name=$1
    file_name=$2
    python jack_compiler.py -s test/$test_name # inefficient but I'm lazy
    
    cd ../tools
    /bin/bash TextComparer.sh "../project10/test/$test_name/out/parse_trees/$file_name.xml" "../project10/test/$test_name/$file_name.xml"
    cd -
}

test ArrayTest Main
test ExpressionLessSquare Main
test ExpressionLessSquare Square
test ExpressionLessSquare SquareGame
test Square Main
test Square Square
test Square SquareGame

// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
// The algorithm is based on repetitive addition.

//// Replace this comment with your code.

// R2 = 0
(START)
@R2
M=0

// i = 0
@i
M=0
// sum = 0
@sum
M=0

// create loop start
(LOOP)

// if (i >= R1) goto STOP
// R1 - i <= 0
@R1
D=M
@i
D=D-M
@STOP
D;JLE

// sum = sum + R0
@R0
D=M
@sum
M=D+M

// i = i + 1
@i
M=M+1

// goto LOOP
@LOOP
0;JMP

// stop
(STOP)

// set R2 to sum
@sum
D=M
@R2
M=D

// end loop
(END)
@END
0;JMP
@START
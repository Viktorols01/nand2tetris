// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

// Start loop
(LOOP)

// If key is not pressed, go to CLEAR
@KBD
D=M
@CLEAR
D;JMP
// Else, go to FILL
@FILL
0;JMP

// Fill and go to LOOP
(FILL)
@SCREEN

@LOOP
0;JMP

// Clear and go to LOOP
(CLEAR)
@SCREEN

@LOOP
0;JMP

// actually jag pallar inte
// fet for loop bara
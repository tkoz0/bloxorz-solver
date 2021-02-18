# bloxorz-solver
compute a bloxorz solution with minimum moves possibile

Current progress:
- puzzle encodings made, fixed with an in game playthrough
- outputs number of moves and the keypress sequence for a solution

Goals
- improve code quality (the entire solver is 1 messy function)
- add output for number of each states on the BFS tree layers

Results:
- program output in solution.txt file
- 1999 moves minimum to complete bloxorz
- agrees with https://answers.com/Q/Can_you_finish_Bloxorz_in_the_least_moves
- stages 01-10: 7,17,19,28,33,35,44,10,24,57
- stages 11-20: 47,65,46,67,57,28,106,85,67,56
- stages 21-30: 71,65,75,57,55,104,71,100,104,114
- stages 31-33: 91,129,65

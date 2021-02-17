'''
Bloxorz solver

Puzzle encoding:
{
    "name": string name of the puzzle
    "grid":
    [ nonempty list of strings, all have same nonzero length
      each character is a grid cell
      must have 1 'S' and 1 'H'
      ' ' = empty square
      '.' = gray square
      '-' = orange square (cannot be vertical on)
      'S' = start point
      'H' = hole (goal)
      'X' = full pressure switch (must be vertical to activate)
      'O' = half preccure switch (can activate either way)
      'B' = bridge square (enabled at start)
      'b' = bridge square (disabled at start)
      'T' = teleport (split block and put halves at new locations)
    ],
    "passcode": 6 digit string (coolmath passcode),
    "bridges":
    [ list of bridges as [[row,col],...]
      specifies which grid cells are used for a bridge
      bridges should not share any squares
      each square used should be a 'B' in the grid
    ],
    "switches":
    [ list of switches as [row,col,[[bridge_number,action],...]]
      action can be "off","on", or "swap" for what it does to bridge state
      this describes what the switch does to some bridges
      bridge_number is the index in the bridges list
      there should be 1 entry for each 'X' and 'O' in the grid
    ]
    "teleports":
    [ list of teleports as [row,col,r1,c1,r2,c2]
      row,col is the teleport location, should be a 'T' on the grid
      r1,c1 and r2,c2 are the coordinates to teleport the block halves
    ]
}

Solving state:
- 2 block coordinates, if they are same then the block is vertical
  they may not be adjacent if the block is split in half
- boolean for which bridges are enabled

Movesch_b = set() # initially deactivated bridges
    
- block may move, or either half if it is split
- if activating a switch, the bridge state may change
- solved state is any with the block vertical on the hole (goal)


'''

if __name__ != '__main__': quit()

import json
import sys

data = json.loads(open(sys.argv[1],'r').read())

def solver(puzzle):
    print('Solving',puzzle['name'],'(passcode = %s)'%puzzle['passcode'])
    grid = [list(r) for r in puzzle['grid']] # convert to 2d array
    R,C = len(grid),len(grid[0])
    assert len(set(len(r) for r in grid)) == 1 # all rows same length
    # extract components of puzzle encoding
    bridges = puzzle['bridges']
    switches = puzzle['switches']
    teleports = puzzle['teleports']
    # setup data structures for BFS
    # store positions for start and end in row major order
    pos2bridge = dict() # map (r,c) -> bridge index
    pos2switch = dict() # map (r,c) -> list of switch actions
    pos2teleport = dict() # map (r,c) -> (r1,c1,r2,c2) teleport locations
    start_position = None
    start_bridges = [False]*len(bridges)
    end_position = None
    # store positions for these to be sure they are all referenced
    ch_X = set() # full pressure switches
    ch_O = set() # half pressure switches
    ch_B = set() # initially activated bridges
    ch_b = set() # initially deactivated bridges
    ch_T = set() # teleports
    # extract features from the grid
    for r in range(R):
        for c in range(C):
            ch = grid[r][c]
            if ch == 'S':
                assert start_position is None
                start_position = (r,c,r,c) # both block halves on (r,c)
                grid[r][c] = '.' # treat as a normal gray square
            elif ch == 'H':
                assert end_position is None
                end_position = (r,c,r,c)
                grid[r][c] = '.' # treat as a normal gray square
                # solution is found when block is vertical on this position
            # the 5 remaining symbols are treated like normal gray squares
            # but with special behavior
            elif ch == 'X': ch_X.add((r,c))
            elif ch == 'O': ch_O.add((r,c))
            elif ch == 'B': ch_B.add((r,c))
            elif ch == 'b': ch_b.add((r,c))
            elif ch == 'T': ch_T.add((r,c))
            else:
                assert ch in ' .-' # empty/gray/orange
    # ensure all bridge squares are referenced
    # all squares used by a bridge must be the same type 'b' or 'B'
    for i,bridge in enumerate(bridges):
        r,c = bridge[0]
        if (r,c) in ch_B:
            ch_B.remove((r,c))
            pos2bridge[(r,c)] = i
            for r,c in bridge[1:]:
                assert (r,c) in ch_B
                ch_B.remove((r,c))
                pos2bridge[(r,c)] = i
            start_bridges[i] = True # 'B' is initally enabled bridges
        else:
            assert (r,c) in ch_b
            ch_b.remove((r,c))
            pos2bridge[(r,c)] = i
            for r,c in bridge[1:]:
                assert (r,c) in ch_b
                ch_b.remove((r,c))
                pos2bridge[(r,c)] = i
    # make mapping for location to switches and teleports
    for r,c,actions in switches:
        pos2switch[(r,c)] = actions
    for r,c,r1,c1,r2,c2 in teleports:
        pos2teleport[(r,c)] = (r1,c1,r2,c2)
    # debug outputs
    #print(pos2bridge)
    #print(pos2switch)
    #print(pos2teleport)
    #print(start_position)
    #print(start_bridges)
    #print(end_position)
    # BFS solver implementation
    queue = [(start_position,tuple(start_bridges))]
    prev = dict() # map state -> previous state (None for the root state)
    prev[queue[0]] = None
    visited = set()
    visited.add(queue[0])
    bfs_layer = 0
    while len(queue) != 0:
        bfs_layer += 1
        new_queue = []
        for pos,bridges in queue:
            bridges = list(bridges)
            # TODO generate all state transitions V (where block doesnt fall)
            #for V in transitions:
            #    if V is solution:
            #        return path
            #    if V in visited: continue
            #    visited.add(V)
            #    newqueue.append(V)
            #    prev[V] = (pos,bridges)
            r1,c1,r2,c2 = pos # row major order, assume state is valid
            assert r1 < r2 or (r1 == r2 and c1 <= c2) # row major order
            new_pos_list = [] # generate all new positions by rolling a block
            if r1 == r2 and c1 == c2: # vertical (block standing on a square)
                new_pos_list.append((r1+1,c1,r1+2,c1)) # down
                new_pos_list.append((r1,c1+1,r1,c1+2)) # right
                new_pos_list.append((r1-2,c1,r1-1,c1)) # up
                new_pos_list.append((r1,c1-2,r1,c1-1)) # left
            elif r1 == r2 and c1+1 == c2: # block horizontal along row
                new_pos_list.append((r1+1,c1,r2+1,c2)) # down
                new_pos_list.append((r1,c2+1,r1,c2+1)) # right
                new_pos_list.append((r1-1,c1,r2-1,c2)) # up
                new_pos_list.append((r1,c1-1,r1,c1-1)) # left
            elif c1 == c2 and r1+1 == r2: # block horizontal along column
                new_pos_list.append((r2+1,c1,r2+1,c1)) # down
                new_pos_list.append((r1,c1+1,r2,c2+1)) # right
                new_pos_list.append((r1-1,c1,r1-1,c1)) # up
                new_pos_list.append((r1,c1-1,r2,c2-1)) # left
            else: # block is split
                for dr,dc in [(1,0),(0,1),(-1,0),(0,-1)]: # move amounts
                    r1m,c1m = r1+dr,c1+dc # position 1 moved
                    r2m,c2m = r2+dr,c2+dc # position 2 moved
                    # add new position states, ensuring row major order
                    if r1m > r2 or (r1m == r2 and c1m > c2):
                        new_pos_list.append((r2,c2,r1m,c1m))
                    else: new_pos_list.append((r1m,c1m,r2,c2))
                    if r2m > r1 or (r2m == r1 and c2m > c1):
                        new_pos_list.append((r1,c1,r2m,c2m))
                    else: new_pos_list.append((r2m,c2m,r1,c1))
            # explore to neighboring vertices
            for nr1,nc1,nr2,nc2 in new_pos_list:
                if nr1 < 0 or nc1 < 0 or nr2 < 0 or nc2 < 0 \
                    or nr1 >= R or nc1 >= C or nr2 >= R or nc2 >= C:
                    continue # out of bounds
                s1,s2 = grid[nr1][nc1],grid[nr2][nc2]
                if s1 == ' ' or s2 == ' ': continue # falls off
                if s1 in 'Bb' and not bridges[pos2bridge[(nr1,nc1)]]:
                    continue # falls off
                if s2 in 'Bb' and not bridges[pos2bridge[(nr2,nc2)]]:
                    continue # falls off
                # safe to assume block is on nonempty grid spaces
                new_bridges = bridges[:]
                bridge_actions = [] # actions to perform on bridges
                if (nr1,nc1) == (nr2,nc2): # checks for vertical block
                    # this position could not have been occupied before moving
                    assert s1 == s2
                    if s1 == '-': continue # falls through orange square
                    if s1 == 'T': # teleport block
                        nr1,nc1,nr2,nc2 = pos2teleport[(nr1,nc1)]
                    if s1 in 'XO': # switch bridge actions
                        bridge_actions += pos2switch[(nr1,nc1)]
                else: # must only press switches if block part moved
                    # both of these if statements should never run together
                    if s1 == 'O' and (nr1,nc1) not in [(r1,c1),(r2,c2)]:
                        bridge_actions += pos2switch[(nr1,nc1)]
                    if s2 == 'O' and (nr2,nc2) not in [(r1,c1),(r2,c2)]:
                        bridge_actions += pos2switch[(nr2,nc2)]
                # change bridges as necessary
                for bridge_num,action in bridge_actions:
                    if action == 'on': new_bridges[bridge_num] = True
                    elif action == 'off': new_bridges[bridge_num] = False
                    else:
                        assert action == 'swap'
                        new_bridges[bridge_num] = not new_bridges[bridge_num]
                # now the BFS stuff with the new_state vertex in the graph
                new_pos = (nr1,nc1,nr2,nc2)
                new_state = (new_pos,tuple(new_bridges))
                if new_state in visited: continue
                visited.add(new_state)
                new_queue.append(new_state)
                prev[new_state] = (pos,tuple(bridges))
                if new_pos == end_position: # solution
                    #print('solution found on bfs_layer =',bfs_layer)
                    path = [new_state] # work backwards to root
                    new_state = prev[new_state]
                    while new_state != None:
                        path.append(new_state)
                        new_state = prev[new_state]
                    return path[::-1] # return solution in order
        queue = new_queue
        #print('bfs_layer =',bfs_layer,'len(queue) =',len(queue))

path = solver(data[22])
print('moves:',len(path)-1)
for i in path: print(i)
quit()

total_moves = 0
for puzzle in data:
    path = solver(puzzle)
    total_moves += len(path)-1
    print('moves:',len(path)-1)
    #print(path)
print('total_moves =',total_moves)

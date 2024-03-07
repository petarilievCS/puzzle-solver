#************************************************************
#   scan_print_map.py
#   Scan a hashi puzzle from stdin, store it in a numpy array,
#   and print it out again.
#
import numpy as np
import sys
import time
import heapq

def main():
    code = ".123456789abc"
    nrow, ncol, map = scan_map()

    island_map = find_islands(map)
    bridge_map, bridge_indices, bridge_starts, bridge_ends = find_bridges(map)
    bridge_connectedness = find_connectedness(bridge_starts, bridge_ends)
    bridge_overlaps = find_overlaps(bridge_indices)
    connections = find_bridge_connections(bridge_starts, bridge_ends)

    bridge_order = sorted(bridge_connectedness, key=bridge_connectedness.get)
    island_connections = find_island_connections(map)

    start = time.time()
    backtrack(0, 
              island_map, 
              bridge_map, 
              bridge_indices, 
              bridge_starts, 
              bridge_ends, 
              len(island_map), 
              bridge_order, 
              bridge_overlaps, 
              set(),
              island_connections)
    end = time.time()
    print(f"Time: {end - start}\n")

    # Print solution
    print_solution(map, bridge_map, bridge_starts, bridge_ends, bridge_indices)

# Finds number of islands that an islands could be connected to
def find_island_connections(map):
    connections = {}
    nrows, ncols = map.shape
    for r in range(nrows):
        for c in range(ncols):
            if map[r, c] != 0:
                connections[(r, c)] = 0
                for i in range(r+1, nrows):
                    if map[i, c] != 0:
                        connections[(r, c)] += 1
                        break
                for i in range(r-1, -1, -1):
                    if map[i, c] != 0:
                        connections[(r, c)] += 1
                        break
                for i in range(c+1, ncols):
                    if map[r, i] != 0:
                        connections[(r, c)] += 1
                        break
                for i in range(c-1, -1, -1):
                    if map[r, i] != 0:
                        connections[(r, c)] += 1
                        break
    return connections

# Finds which bridge is connected to which bridge
def find_bridge_connections(bridge_starts, bridge_ends):
    connections = {}
    for bridge in bridge_starts:
        start = bridge_starts[bridge]
        end = bridge_ends[bridge]
        connections[bridge] = []
        for other_bridge in bridge_starts:
            if other_bridge != bridge:
                other_start = bridge_starts[other_bridge]
                other_end = bridge_ends[other_bridge]
                if start == other_start or start == other_end or end == other_start or end == other_end:
                    connections[bridge].append(other_bridge)
    return connections

# Finds the length of each bridge
def find_bridge_length(bridge_starts, bridge_ends):
    bridge_length = {}
    for bridge in bridge_starts:
        start = bridge_starts[bridge]
        end = bridge_ends[bridge]
        length = abs(start[0] - end[0]) + abs(start[1] - end[1])
        bridge_length[bridge] = length
    return bridge_length

# Finds the bridges that overlap with each bridge
def find_overlaps(bridge_indices):
    overlaps = {}
    for bridge in bridge_indices:
        overlaps[bridge] = []
        for other_bridge in bridge_indices:
            if bridge != other_bridge:
                for index in bridge_indices[bridge]:
                    if index in bridge_indices[other_bridge]:
                        overlaps[bridge].append(other_bridge)
                        break
    return overlaps

# Finds the sum of possible bridges connected to the start and end of a bridge
def find_connectedness(bridge_starts, bridge_ends):
    # Mapping of index to bridges connected to it
    index_connectedness = {}

    for start in bridge_starts.values():
        index_connectedness[start] = index_connectedness.get(start, 0) + 1

    for end in bridge_ends.values():
        index_connectedness[end] = index_connectedness.get(end, 0) + 1

    # Mapping of bridge to connectedness
    bridge_connectedness = {}
    for bridge in bridge_starts:
        bridge_connectedness[bridge] = index_connectedness[bridge_starts[bridge]] + index_connectedness[bridge_ends[bridge]]

    return bridge_connectedness

# Prints solution
def print_solution(map, bridge_map, bridge_starts, bridge_ends, bridge_indices):
    result = []
    nrows, ncols = map.shape
    code = " 123456789abc"

    # Add islands
    for row in range(nrows):
        result.append([])
        for col in range(ncols):
            result[row].append(code[map[row][col]])

    horizontal_bridge = {1: "─", 2: "═", 3: "E"}
    vertical_bridge = {1: "│", 2: "\"", 3: "#"}

    # Add bridges
    for bridge in bridge_map:
        if bridge_map[bridge] != 0:
            horziontal = bridge_starts[bridge][0] == bridge_ends[bridge][0]
            symbol = horizontal_bridge[bridge_map[bridge]] if horziontal else vertical_bridge[bridge_map[bridge]]
            for (row, col) in bridge_indices[bridge]:
                    result[row][col] = symbol

    for row in result:
        print("".join(row))


# Find the least connected bridge
def find_least_connected(bridge_connectedness, occupied):
    least_connected = float('inf')
    bridge = -1
    for b in bridge_connectedness:
        if b not in occupied and bridge_connectedness[b] < least_connected:
            least_connected = bridge_connectedness[b]
            bridge = b
    return bridge

# Searches for solution 
def backtrack(bridge_idx, 
              island_map, 
              bridge_map,
              bridge_indices, 
              bridge_starts, 
              bridge_ends, 
              remaining_islands, 
              bridge_order, 
              bridge_overlaps, 
              occupied,
              island_connections):

    
    # Base case - solution found
    if remaining_islands == 0:
        return True
    
    # Base case - no more bridges
    if bridge_idx == len(bridge_map):
        return False
    
    # Find next free bridge
    current_bridge = bridge_order[bridge_idx]
    while current_bridge in occupied:
        bridge_idx += 1
        if bridge_idx == len(bridge_map):
            return False
        current_bridge = bridge_order[bridge_idx]

    print(f"Bridge: {current_bridge}, Remaining Islands: {remaining_islands}")
        
    start = bridge_starts[current_bridge]
    end = bridge_ends[current_bridge]

    if island_connections[start] == 1 and island_map[start] > min(3, island_map[start], island_map[end]):
        return False
    
    if island_connections[end] == 1 and island_map[end] > min(3, island_map[start], island_map[end]):
        return False
    

    # Case 1 - place bridge
    bridges_added = set()
    for bridge in bridge_overlaps[current_bridge]:
        if bridge not in occupied:
            occupied.add(bridge)
            bridges_added.add(bridge)

    island_connections[start] -= 1
    island_connections[end] -= 1

    for num_planks in range(min(3, island_map[start], island_map[end]), 0, -1):

        # Place plank
        bridge_map[current_bridge] = num_planks
        island_map[start] -= num_planks
        island_map[end] -= num_planks

        # Adjust number of remaining islands
        new_remaining_islands = remaining_islands
        if island_map[start] == 0:
            new_remaining_islands -= 1
        if island_map[end] == 0:
            new_remaining_islands -= 1

        if new_remaining_islands == 0:
            return True

        if backtrack(bridge_idx + 1,
                    island_map, 
                    bridge_map, 
                    bridge_indices, 
                    bridge_starts, 
                    bridge_ends, 
                    new_remaining_islands, 
                    bridge_order, 
                    bridge_overlaps, 
                    occupied,
                    island_connections):
            return True
        
        island_map[start] += num_planks
        island_map[end] += num_planks
        bridge_map[current_bridge] = 0       
        
    # Remove bridge
    for bridge in bridges_added:
        occupied.remove(bridge)
    island_connections[start] += 1
    island_connections[end] += 1

    # Case 2 - skip bridge
    return backtrack(bridge_idx + 1, 
                     island_map, 
                     bridge_map, 
                     bridge_indices, 
                     bridge_starts, 
                     bridge_ends, 
                     remaining_islands, 
                     bridge_order, 
                     bridge_overlaps, 
                     occupied,
                    island_connections)

# Finds islands in the map
def find_islands(map):
    islands = {}
    nrow, ncol = map.shape

    for r in range(nrow):
        for c in range(ncol):
            if map[r,c] != 0:
                islands[(r, c)] = map[r,c]
    return islands

# Finds bridges in the map
def find_bridges(map):
    # Variables
    nrow, ncol = map.shape
    num_bridges = 0

    # Data Structures
    bridge_map = {} # mapping of brdiges to # of planks
    bridge_indices = {} # mapping of bridges to indices occupied
    bridge_starts = {}
    bridge_ends = {}

    # Perform horizontal search
    for r in range(nrow):
        island_a, island_b = -1, -1

        # Find first island
        for c in range(ncol):
            if map[r, c] != 0:
                island_a = c
                break
        
        # Mark bridges in current row
        if island_a != -1:
            for c in range(island_a+1, ncol):
                if map[r, c] != 0:
                    island_b = c
                    bridge_starts[num_bridges] = (r, island_a)
                    bridge_ends[num_bridges] = (r, island_b)
                    bridge_map[num_bridges] = 0
                    bridge_indices[num_bridges] = []

                    for i in range(island_a+1, island_b):
                        bridge_indices[num_bridges].append((r, i))
                    num_bridges += 1
                    island_a = island_b


    # Perform vertical search
    for c in range(ncol):
        island_a, island_b = -1, -1

        # Find first island
        for r in range(nrow):
            if map[r, c] != 0:
                island_a = r
                break
        
        # Mark bridges in current column
        if island_a != -1:
            for r in range(island_a+1, nrow):
                if map[r, c] != 0:
                    island_b = r
                    bridge_starts[num_bridges] = (island_a, c)
                    bridge_ends[num_bridges] = (island_b, c)
                    bridge_map[num_bridges] = 0
                    bridge_indices[num_bridges] = []
                    for i in range(island_a+1, island_b):
                        bridge_indices[num_bridges].append((i, c))
                    num_bridges += 1
                    island_a = island_b

    return bridge_map, bridge_indices, bridge_starts, bridge_ends
        
def scan_map():
    text = []
    for line in sys.stdin:

        if line == "\n": 
            break

        row = []
        for ch in line:
            n = ord(ch)
            if n >= 48 and n <= 57:    # between '0' and '9'
                row.append(n - 48)
            elif n >= 97 and n <= 122: # between 'a' and 'z'
                row.append(n - 87)
            elif ch == '.':
                row.append(0)
        text.append(row)

    nrow = len(text)
    ncol = len(text[0])

    map = np.zeros((nrow,ncol),dtype=np.int32)
    for r in range(nrow):
        for c in range(ncol):
            map[r,c] = text[r][c]
    
    return nrow, ncol, map

if __name__ == '__main__':
    main()
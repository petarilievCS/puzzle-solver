#!/usr/bin/python3.9.6

# Alborithm Description
#   My algorithm is based on backtracking, but also involves a few heuristics to reduce the search space. 
#   Firstly, the function initial_forward_check is invoked. This function traverses initial puzzle and assigns 
#   new minimum and maximum values to bridges. The formula that is used is this one: new_max = min(current_max, n - sum) 
#   where n is the number on the current insland and sum is the sum of the other bridges. The same logic is applied to 
#   min values. This leads to a much smaller search space.
# 
#   Furthermore, another forward check is triggered whenever a bridge is placed, to ensure that all bridges still 
#   have possible values. If a bridge has no possible values, it backtracks.
#   
#   When it comes to choose the next bridge to be assigned, I chose the bridge with the lowest connectedness, where
#   connectedness is the sum of bridges connected to its start and end islands.

#************************************************************
#   scan_print_map.py
#   Scan a hashi puzzle from stdin, store it in a numpy array,
#   and print it out again.
#
import numpy as np
import sys
import time
import heapq

from bridge import Bridge
from island import Island

remaining_islands = 0

def main():

    global remaining_islands

    # Data Structures
    nrow, ncol, map = scan_map()
    island_map = find_islands(map)
    bridge_map  = find_bridges(map)

    # Pre-processing
    remaining_islands = len(island_map)
    find_island_bridges(bridge_map, island_map)
    find_bridge_crossings(bridge_map)
    initial_forward_check(island_map, bridge_map)
    
    bridge_connectedness = find_connectedness(bridge_map, island_map)
    bridge_order = sorted(bridge_connectedness, key=bridge_connectedness.get, reverse=False)
    
    backtrack(0, 
              island_map, 
              bridge_map,
              bridge_order)

    print_solution(map, bridge_map)

# Performs forward checking on constraints
def forward_check(bridge_map, island_map):
    
    x = 0

    for island_id in island_map:
        island = island_map[island_id]
        total_sum = 0
        for bridge_id in island.bridges:
            bridge = bridge_map[bridge_id]
            total_sum += bridge.maximum

        if island.number > total_sum:
            return False
    
        total_sum = 0
        for bridge_id in island.bridges:
            bridge = bridge_map[bridge_id]
            total_sum += bridge.minimum
        
        if island.number < total_sum:
            return False
    
    return True

# Performs forward checking algorithm
def initial_forward_check(island_map, bridge_map, print=False):

    global remaining_islands

    # Sets max
    for island_id in island_map:
        island = island_map[island_id]
        island.max = max(3, island.number)
    
    # Max search
    changes_made = True
    while changes_made:

        changes_made = False
        for island_id in island_map:
            island = island_map[island_id]
            for bridge_id in island.bridges:
                bridge = bridge_map[bridge_id]

                # Find sum of all other bridges
                max_sum = 0
                for other_bridge_id in island.bridges:
                    if other_bridge_id != bridge_id:
                        other_bridge = bridge_map[other_bridge_id]
                        max_sum += other_bridge.maximum
                
                diff = island.number - max_sum
                old_minimum = bridge.minimum
                bridge.minimum = max(bridge.minimum, diff)
                if bridge.minimum != old_minimum:
                    changes_made = True
        
        for island_id in island_map:
            island = island_map[island_id]
            for bridge_id in island.bridges:
                bridge = bridge_map[bridge_id]

                # Find sum of all other bridges
                min_sum = 0
                for other_bridge_id in island.bridges:
                    if other_bridge_id != bridge_id:
                        other_bridge = bridge_map[other_bridge_id]
                        min_sum += other_bridge.minimum
                
                diff = island.number - min_sum
                old_maximum = bridge.maximum
                bridge.maximum = min(bridge.maximum, diff)
                if bridge.maximum != old_maximum:
                    changes_made = True        

    # Adjust remaining islands
    for island_id in island_map:
        island = island_map[island_id]
        if island.done(bridge_map):
            remaining_islands -= 1     

# Finds a mapping of islands to connected bridges
def find_island_bridges(bridge_map, island_map):
    for bridge_id in bridge_map:
        bridge = bridge_map[bridge_id]
        island_map[bridge.start].add_bridge(bridge_id)
        island_map[bridge.end].add_bridge(bridge_id)

# Marks all of an island's bridges as done
def mark_island_bridges_done(island_map, bridge_map, island_id):
    island = island_map[island_id]
    for bridge_id in island.bridges:
        bridge = bridge_map[bridge_id]
        bridge.done = True

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

# Finds the sum of possible bridges connected to the start and end of a bridge
def find_connectedness(bridge_map, island_map):
    # Mapping of bridge to connectedness
    bridge_connectedness = {}
    for bridge_id in bridge_map:
        bridge = bridge_map[bridge_id]
        bridge_connectedness[bridge_id] = 0
        if bridge.start in island_map:
            bridge_connectedness[bridge_id] += len(island_map[bridge.start].bridges)
        if bridge.end in island_map:
            bridge_connectedness[bridge_id] += len(island_map[bridge.end].bridges)

    return bridge_connectedness

# Prints solution
def print_solution(map, bridge_map):
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
    for bridge_id in bridge_map:
        bridge = bridge_map[bridge_id]

        if bridge.maximum != 0:
            symbol = horizontal_bridge[bridge.maximum] if bridge.horizontal else vertical_bridge[bridge.maximum]
            for (row, col) in bridge.indices:
                    result[row][col] = symbol
    for row in result:
        print("".join(row))

# Searches for a solution, returns True if found, False otherwise
def backtrack(bridge_idx, 
              island_map, 
              bridge_map,
              bridge_order):

    global remaining_islands 

    # Base case - solution found
    if remaining_islands == 0:
        return True
    
    # Base case - no more bridges
    if bridge_idx == len(bridge_order):
        return False
    
    # Base case - constraints violated
    if not forward_check(bridge_map, island_map):
        return False

    # Find next bridge
    current_bridge_id = bridge_order[bridge_idx]
    current_bridge = bridge_map[current_bridge_id]

    # Base case - bridge already placed
    if current_bridge.done():
        return backtrack(bridge_idx + 1, 
                         island_map, 
                         bridge_map, 
                         bridge_order)    
    
    # Placing the bridge
    prev_max = current_bridge.maximum
    prev_min = current_bridge.minimum
    prev_values = {}

    # Mark all crossing bridges to 0
    for crossed_bridge in current_bridge.crossings:
        crossed_prev_max, crossed_prev_min = current_bridge.maximum, current_bridge.minimum
        prev_values[crossed_bridge] = (crossed_prev_max, crossed_prev_min)
        place_bridge(crossed_bridge, 0, bridge_map, island_map)

    start = current_bridge.start
    end = current_bridge.end

    start_island = island_map[start]
    end_island = island_map[end]

    start_planks = min(3, start_island.number, end_island.number, current_bridge.maximum)
    end_planks = max(0, current_bridge.minimum - 1)

    for num_planks in range(start_planks, end_planks, -1):
        
        # Place plank
        place_bridge(current_bridge_id, num_planks, bridge_map, island_map)

        if start_island.over(bridge_map) or end_island.over(bridge_map):
            continue

        if backtrack(bridge_idx + 1,
                    island_map, 
                    bridge_map, 
                    bridge_order):
            return True
        
        # Remove plank
        remove_bridge(current_bridge_id, bridge_map, prev_max, prev_min, island_map)
        
    # Restore crossed bridges
    for crossed_bridge in current_bridge.crossings:
        crossed_prev_max, crossed_prev_min = prev_values[crossed_bridge]
        remove_bridge(crossed_bridge, bridge_map, crossed_prev_max, crossed_prev_min, island_map)

    # Case 2 - skip bridge
    place_bridge(current_bridge_id, 0, bridge_map, island_map)
    if backtrack(bridge_idx + 1, 
                        island_map, 
                        bridge_map, 
                        bridge_order):
        return True
    
    # Remove bridge
    remove_bridge(current_bridge_id, bridge_map, prev_max, prev_min, island_map)
    return False

def place_bridge(bridge_id, planks, bridge_map, island_map):
    bridge = bridge_map[bridge_id]    
    global remaining_islands

    start, end = bridge.start, bridge.end
    start_island = island_map[start]
    end_island = island_map[end]

    prev_done_start = start_island.done(bridge_map) 
    prev_done_end = end_island.done(bridge_map)

    bridge.maximum = planks
    bridge.minimum = planks

    if start_island.done(bridge_map) and not prev_done_start:
        remaining_islands -= 1
    if end_island.done(bridge_map) and not prev_done_end:
        remaining_islands -= 1

def remove_bridge(bridge_id, bridge_map, prev_max, prev_min, island_map):
    bridge = bridge_map[bridge_id]
    global remaining_islands

    start, end = bridge.start, bridge.end
    start_island = island_map[start]
    end_island = island_map[end]
    prev_done_start = start_island.done(bridge_map)
    prev_done_end = end_island.done(bridge_map)

    bridge.maximum = prev_max
    bridge.minimum = prev_min

    if not start_island.done(bridge_map) and prev_done_start:
        remaining_islands += 1
    if not end_island.done(bridge_map) and prev_done_end:
        remaining_islands += 1

# Marks bridge indices as occupied
def mark_occupied(occupied, bridge_indices):
    for index in bridge_indices:
        occupied.add(index)

# Finds islands in the map
def find_islands(map):
    islands = {}
    nrow, ncol = map.shape
    
    for r in range(nrow):
        for c in range(ncol):
            if map[r,c] != 0:
                island = Island(r, c, map[r,c])
                islands[(r, c)] = island
    return islands

# Find what bridges are crossing which ones
def find_bridge_crossings(bridge_map):
    for bridge_id in bridge_map:
        bridge = bridge_map[bridge_id]
        for other_bridge_id in bridge_map:
            other_bridge = bridge_map[other_bridge_id]
            if other_bridge_id != bridge_id:
                for index in other_bridge.indices:
                    if index in bridge.indices:
                        bridge.crossings.append(other_bridge_id)
                        break

# Finds bridges in the map
def find_bridges(map):
    # Variables
    nrow, ncol = map.shape
    num_bridges = 0

    # Data Structures
    bridge_map = {} # mapping of brdige IDs to bridges

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
                    bridge = Bridge(num_bridges, (r, island_a), (r, island_b), True)
                    bridge_map[num_bridges] = bridge
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
                    bridge = Bridge(num_bridges, (island_a, c), (island_b, c), False)
                    bridge_map[num_bridges] = bridge
                    num_bridges += 1
                    island_a = island_b

    return bridge_map
        
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
#************************************************************
#   scan_print_map.py
#   Scan a hashi puzzle from stdin, store it in a numpy array,
#   and print it out again.
#
import numpy as np
import sys
import time
import heapq
import copy

from bridge import Bridge
from island import Island

def main():
    code = ".123456789abc"
    nrow, ncol, map = scan_map()

    # Data Structures
    island_map = find_islands(map)
    bridge_map  = find_bridges(map)

    # Pre-processing
    find_island_bridges(bridge_map, island_map)
    find_bridge_crossings(bridge_map)

    set_max_values(bridge_map, island_map)
    initial_forward_check(island_map, bridge_map)
    print_solution(map, bridge_map)

    # Heuristic Processing
    bridge_connectedness = find_connectedness(bridge_map, island_map)
    bridge_order = sorted(bridge_connectedness, key=bridge_connectedness.get, reverse=False)

    start = time.time()
    backtrack(0, 
              island_map, 
              bridge_map, 
              len(island_map), 
              bridge_order)
    end = time.time()
    print(f"Time: {end - start}\n")

    # Print solution
    print_solution(map, bridge_map)

# Find what bridges are crossing which ones
def find_bridge_crossings(bridge_map):
    for bridge_id in bridge_map:
        bridge = bridge_map[bridge_id]
        for other_bridge_id in bridge_map:
            other_bridge = bridge_map[other_bridge_id]
            if other_bridge_id != bridge_id:
                for index in other_bridge.indices:
                    if index in bridge.indices:
                        bridge.crossing.append(other_bridge_id)
                        break

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

# Checks the legal values of a given bridge
def forward_check_bridge(current_bridge_id, bridge_map, island_map):
    bridge = bridge_map[current_bridge_id]
    start = island_map[bridge.start]
    end = island_map[bridge.end]
    islands = [start, end]

    changes_made = True
    while changes_made:
        changes_made = False
        
        for island_id in island_map:
            island = island_map[island_id]
            for bridge_id in island.bridges:
                if bridge_id != current_bridge_id:
                    bridge = bridge_map[bridge_id]

                    # Find sum of all other bridges
                    max_sum = 0
                    for other_bridge_id in island.bridges:
                        if other_bridge_id != bridge_id:
                            other_bridge = bridge_map[other_bridge_id]
                            max_sum += other_bridge.maximum
                    
                    diff = island.number - max_sum
                    new_min = max(bridge.minimum, diff)

        for island_id in island_map:
            island = island_map[island_id]
            for bridge_id in island.bridges:
                if bridge_id != current_bridge_id:
                    # Find sum of all other bridges
                    min_sum = 0
                    for other_bridge_id in island.bridges:
                        if other_bridge_id != bridge_id:
                            other_bridge = bridge_map[other_bridge_id]
                            min_sum += other_bridge.minimum
                    
                    diff = island.number - min_sum
                    new_max = min(bridge.maximum, diff)

    for bridge_id in bridge_map:
        bridge = bridge_map[bridge_id]
        if bridge.maximum < bridge.minimum:
            print("WRONG")
            return False

    return True
        
# Sets max values of bridges to the smallest of their start / end
def set_max_values(bridge_map, island_map):
    for bridge in bridge_map.values():
        start = island_map[bridge.start]
        end = island_map[bridge.end]
        bridge.maximum = min(3, start.number, end.number)

# Performs forward checking algorithm
def initial_forward_check(island_map, bridge_map, loop=True, should_print=True):
    # Max search
    changes_made = True
    while changes_made:
        # islands_to_be_removed = []
        # for island_id in island_map:
        #     island = island_map[island_id]
        #     if island.number == 0:
        #         islands_to_be_removed.append(island_id)
        # for island_id in islands_to_be_removed:
        #     island_map.pop(island_id)
    
        changes_made = False
        for island_id in island_map:
            island = island_map[island_id]
            for bridge_id in island.bridges:
                bridge = bridge_map[bridge_id]

                if bridge.maximum == bridge.minimum:
                    continue

                # Find sum of all other bridges
                max_sum = 0
                for other_bridge_id in island.bridges:
                    if other_bridge_id != bridge_id:
                        other_bridge = bridge_map[other_bridge_id]
                        max_sum += other_bridge.maximum
                
                diff = island.number - max_sum
                if diff > bridge.minimum:
                    if should_print:
                        print(f"Island: {island_id} - Bridge: {bridge_id} - Min: {diff}")
                    if loop:
                        changes_made = True
                
                bridge.minimum = max(bridge.minimum, diff)
                if bridge.maximum < bridge.minimum:
                    print("Runs")
                    return False
                
        for island_id in island_map:
            island = island_map[island_id]
            for bridge_id in island.bridges:
                bridge = bridge_map[bridge_id]

                if bridge.maximum == bridge.minimum:
                    continue

                # Find sum of all other bridges
                min_sum = 0
                for other_bridge_id in island.bridges:
                    if other_bridge_id != bridge_id:
                        other_bridge = bridge_map[other_bridge_id]
                        min_sum += other_bridge.minimum
                
                diff = island.number - min_sum
                if diff < bridge.maximum:
                    if should_print:
                        print(f"Island: {island_id} - Bridge: {bridge_id} - Max: {diff}")
                    if loop:
                        changes_made = True

                bridge.maximum = min(bridge.maximum, diff)
                if bridge.maximum < bridge.minimum:
                    print("Runs")
                    return False

    for bridge_id in bridge_map:
        bridge = bridge_map[bridge_id]
        if bridge.maximum < bridge.minimum:
            return False
            
    return True

def place_bridge(bridge_id, planks, bridge_map):
    # print(f"Placing {planks} on {bridge_id}")
    bridge = bridge_map[bridge_id]    
    bridge.planks = planks
    bridge.maximum = planks
    bridge.minimum = planks
    bridge.done = True

def remove_bridge(bridge_id, bridge_map, prev_max, prev_min):
        bridge = bridge_map[bridge_id]
        bridge.planks = 0
        bridge.maximum = prev_max
        bridge.minimum = prev_min
        bridge.done = False

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
        if bridge.planks == 0 and bridge.done == False:
            bridge_connectedness[bridge_id] = 0
            if bridge.start in island_map:
                bridge_connectedness[bridge_id] += len(island_map[bridge.start].bridges)
            if bridge.end in island_map:
                bridge_connectedness[bridge_id] += len(island_map[bridge.end].bridges)

    return bridge_connectedness

# Given a bridge map, returns a mapping of bridges to their min and max values
def get_current_min_max_state(bridge_map):
    mapping = {}
    for bridge_id in bridge_map:
        bridge = bridge_map[bridge_id]
        mapping[bridge_id] = (bridge.minimum, bridge.maximum)
    return mapping

# Applies the min_max_mapping to the bridge_map
def restore_min_max_state(bridge_map, mapping):
    for bridge_id in bridge_map:
        bridge = bridge_map[bridge_id]
        bridge.minimum = mapping[bridge_id][0]
        bridge.maximum = mapping[bridge_id][1]

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

        if bridge.planks != 0:
            symbol = horizontal_bridge[bridge.planks] if bridge.horizontal else vertical_bridge[bridge.planks]
            for (row, col) in bridge.indices:
                    result[row][col] = symbol
    for row in result:
        print("".join(row))

# Searches for solution 

def backtrack(bridge_idx, 
              island_map, 
              bridge_map,
              remaining_islands, 
              bridge_order):

    # Base case - solution found

    if remaining_islands == 0:
        return True
    
    # Base case - no more bridges
    if bridge_idx == len(bridge_order):
        return False
    
    # if not forward_check(bridge_map, island_map):
    #     return False

    # Find next bridge
    current_bridge_id = bridge_order[bridge_idx]
    current_bridge = bridge_map[current_bridge_id]

    # If current bridge is placed, skip it
    if current_bridge.done:
        return backtrack(bridge_idx + 1, 
                         island_map, 
                         bridge_map, 
                         remaining_islands, 
                         bridge_order)    

    # Placing the bridge
    prev_max = current_bridge.maximum
    prev_min = current_bridge.minimum
    prev_values = {}

    # Mark all crossing bridges to 0
    for crossed_bridge in current_bridge.crossing:
        crossed_prev_max, crossed_prev_min = current_bridge.maximum, current_bridge.minimum
        prev_values[crossed_bridge] = (crossed_prev_max, crossed_prev_min)
        place_bridge(crossed_bridge, 0, bridge_map)

    start = current_bridge.start
    start_island = island_map[start]

    end = current_bridge.end
    end_island = island_map[end]
    
    start_planks = min(3, start_island.number, end_island.number, current_bridge.maximum)
    end_planks = max(0, current_bridge.minimum - 1)
    # Main loop
    for num_planks in range(start_planks, end_planks, -1):
        
        place_bridge(current_bridge_id, num_planks, bridge_map)
        current_state = get_current_min_max_state(bridge_map)
        check = initial_forward_check(island_map, bridge_map, True, True)
        if not check:
            restore_min_max_state(bridge_map, current_state)
            continue

        # Adjust number of remaining islands
        new_remaining_islands = remaining_islands
        if start_island.done(bridge_map):
            new_remaining_islands -= 1
        if end_island.done(bridge_map):
            new_remaining_islands -= 1
        if new_remaining_islands == 0:
            return True
        
        if start_island.over(bridge_map) or end_island.over(bridge_map):
            continue

        if backtrack(bridge_idx + 1,
                    island_map, 
                    bridge_map, 
                    new_remaining_islands, 
                    bridge_order):
            return True

    # Restore crossed bridges
    for crossed_bridge in current_bridge.crossing:
        crossed_prev_max, crossed_prev_min = prev_values[crossed_bridge]
        remove_bridge(crossed_bridge, bridge_map, crossed_prev_max, crossed_prev_min)

    # Case 2 - skip bridge
    place_bridge(current_bridge_id, 0, bridge_map)
    if backtrack(bridge_idx + 1, 
                        island_map, 
                        bridge_map, 
                        remaining_islands, 
                        bridge_order):
        return True
    
    # Remove bridge
    remove_bridge(current_bridge_id, bridge_map, prev_max, prev_min)
    return False

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
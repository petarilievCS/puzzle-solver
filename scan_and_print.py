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

def main():
    code = ".123456789abc"
    nrow, ncol, map = scan_map()

    # Data Structures
    island_map = find_islands(map)
    bridge_map  = find_bridges(map)
    find_island_bridges(bridge_map, island_map)

    occupied = set()

    initial_forward_check(island_map, bridge_map)
    print_solution(map, bridge_map)

    bridge_connectedness = find_connectedness(bridge_map, island_map)
    bridge_order = sorted(bridge_connectedness, key=bridge_connectedness.get, reverse=False)

    start = time.time()
    backtrack(0, 
              island_map, 
              bridge_map, 
              len(island_map), 
              bridge_order, 
              occupied)
    end = time.time()
    print(f"Time: {end - start}\n")

    # Print solution
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

    # Sets max
    for island_id in island_map:
        island = island_map[island_id]
        island.max = max(3, island.number)
    
    # Max search
    changes_made = True
    while changes_made:

        islands_to_be_removed = []
        for island_id in island_map:
            island = island_map[island_id]
            if island.number == 0:
                islands_to_be_removed.append(island_id)
        for island_id in islands_to_be_removed:
            island_map.pop(island_id)

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

                if diff > bridge.minimum:
                    if print:
                        print(f"Island: {island_id} - Bridge: {bridge_id} - Diff: {diff} - Min: {bridge.minimum}")
                    changes_made = True

                old_minimum = bridge.minimum
                bridge.minimum = max(bridge.minimum, diff)
                if bridge.minimum != old_minimum:
                    changes_made = True

                if bridge.minimum == bridge.maximum:
                    place_bridge(bridge_id, bridge.minimum, bridge_map, island_map)
                    bridge.done = True
        
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

                if diff < bridge.maximum:
                    if print:
                        print(f"Island: {island_id} - Bridge: {bridge_id} - Diff: {diff} - Max: {bridge.maximum}")
                    changes_made = True

                old_maximum = bridge.maximum
                bridge.maximum = min(bridge.maximum, diff)
                if bridge.maximum != old_maximum:
                    changes_made = True             

                if bridge.minimum == bridge.maximum:
                    place_bridge(bridge_id, bridge.minimum, bridge_map, island_map)
                    bridge.done = True

def place_bridge(bridge_id, planks, bridge_map, island_map):
    if planks != 0:
        bridge = bridge_map[bridge_id]
        start_island = island_map[bridge.start]
        end_island = island_map[bridge.end]

        start_island.number -= planks
        end_island.number -= planks

        start_island.bridges.remove(bridge_id)
        end_island.bridges.remove(bridge_id)
        bridge.planks = planks

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
              bridge_order, 
              occupied):

    # Base case - solution found
    if remaining_islands == 0:
        return True
    
    # Base case - no more bridges
    if bridge_idx == len(bridge_order):
        return False
    
    if not forward_check(bridge_map, island_map):
        return False

    # Find next bridge
    current_bridge_id = bridge_order[bridge_idx]
    current_bridge = bridge_map[current_bridge_id]

    if current_bridge.done:
        return backtrack(bridge_idx + 1, 
                         island_map, 
                         bridge_map, 
                         remaining_islands, 
                         bridge_order, 
                         occupied)    
    
    # Base case - bridge can't be placed due to another bridge being in its way
    for index in current_bridge.indices:
        if index in occupied:
            return backtrack(bridge_idx + 1, 
                             island_map, 
                             bridge_map, 
                             remaining_islands, 
                             bridge_order, 
                             occupied)

    start = current_bridge.start
    end = current_bridge.end

    if start not in island_map or end not in island_map:
        return backtrack(bridge_idx + 1, 
                         island_map, 
                         bridge_map, 
                         remaining_islands, 
                         bridge_order, 
                         occupied)

    start_island = island_map[start]
    end_island = island_map[end]

    # # Case 1 - place bridge
    mark_occupied(occupied, current_bridge.indices)
    
    start_planks = min(3, start_island.number, end_island.number, current_bridge.maximum)
    end_planks = max(0, current_bridge.minimum - 1)

    old_max = current_bridge.maximum
    old_min = current_bridge.minimum
    start_island.bridges.remove(current_bridge_id)
    end_island.bridges.remove(current_bridge_id)
    current_bridge.done = True

    for num_planks in range(start_planks, end_planks, -1):
        
        # Place plank
        current_bridge.planks = num_planks
        start_island.number -= num_planks
        end_island.number -= num_planks

        current_bridge.maximum = num_planks
        current_bridge.minimum = num_planks

        # Adjust number of remaining islands
        new_remaining_islands = remaining_islands
        if start_island.number == 0:
            new_remaining_islands -= 1
        if end_island.number == 0:
            new_remaining_islands -= 1
        if new_remaining_islands == 0:
            return True

        if backtrack(bridge_idx + 1,
                    island_map, 
                    bridge_map, 
                    new_remaining_islands, 
                    bridge_order, 
                    occupied):
            return True
        
        start_island.number += num_planks
        end_island.number += num_planks
        current_bridge.planks = 0
        
    # Free up occupied indices
    for index in current_bridge.indices:
        occupied.remove(index)

    current_bridge.maximum = old_max
    current_bridge.minimum = old_min
    current_bridge.done = False

    start_island.bridges.append(current_bridge_id)
    end_island.bridges.append(current_bridge_id)

    # Case 2 - skip bridge
    if current_bridge.minimum == 0:
        return backtrack(bridge_idx + 1, 
                        island_map, 
                        bridge_map, 
                        remaining_islands, 
                        bridge_order, 
                        occupied)
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
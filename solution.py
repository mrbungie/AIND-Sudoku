assignments = []

############################
# Setting up our environment
# Based on utils.py
############################
def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

rows = 'ABCDEFGHI'
cols = '123456789'

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

# Main differences over utils.py. It enables the Question 2 constraint, simply adding new two units (both diagonals).
# I use enumerate to join row with columns, so when A(row_n=0) = 1(col_n=0) they merge as 'A1'. In the case of the "reverse" diagonal I just substract row_n to 8 (due to the length of the board and zero-indexed lists) and join them.
# Then I just add both units to the unitlist.
diag_units = [[row+col for row_n, row in enumerate(rows) for col_n, col in enumerate(cols) if row_n == col_n], [row+col for row_n, row in enumerate(rows) for col_n, col in enumerate(cols) if (8-row_n) == col_n]]
unitlist = row_units + column_units + square_units + diag_units

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)
#################################
# End
#################################

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    naked_twins = dict()
    # Find all instances of naked twins
    for box, box_units in units.items(): # we look for each box and it's units
        box_value = values[box] # we get that box value
        if len(box_value) == 2: # if it's length 2 it CAN be a twin.
             for unit_boxes in box_units: # For every unit (horizontal, vertical, square or diagonal) that box belongs
                unit_peers = [peer for peer in unit_boxes if peer != box] # We get peers (every box in the unit except the box we're looking at from the beginning)
                for unit_peer in unit_peers: # We look for every box in that unit
                    if values[unit_peer] == box_value: # If the box is not the box we are exploring, and it shares the same value we should be happy, because we found some twins.
                        naked_twins[box] = (unit_peer, box_value, unit_peers) # we assign it's peer, value and peers to a dictionary. 

    # Eliminate the naked twins as possibilities for their peers
    for box, data in naked_twins.items(): # for every box that has a naked twin, get it and it's "data" (twin, possible_values, and the box peers)
        twin = data[0] # We this box twin
        twins_values = [possibility for possibility in data[1]] # It's values
        unit_peers = data[2] # and this box's peers to be checked
        for unit_peer in unit_peers:  # for each peer
            if unit_peer != twin and len(values[unit_peer]) > 1: # we check if this peer is not the actual twin of the box, and if has at least 2 chars (box not already solved)
                new_values = ''.join([prior_value for prior_value in values[unit_peer] if prior_value not in twins_values]) # we eliminate the naked twins possibilities from their peer
                values = assign_value(values, unit_peer, new_values) # and we reassignate that peer values

    return values

def grid_values(grid):
    """
    Source: Extracted from my solution to a exercise included in the AIND lessons.
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    return {loc:val for loc, val in zip(boxes, [elem if elem != '.' else '123456789' for elem in grid])}

def display(values):
    """
    Source: utils.py from the AIND lessons.
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """
    Source: Extracted from my solution to a exercise included in the AIND lessons.
    Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    for box, value in values.items():
        if len(value) == 1:
            for peer in peers[box]:
                values = assign_value(values, peer, values[peer].replace(value, ''))
    return values

def only_choice(values):
    """
    Source: Extracted from my solution to a exercise included in the AIND lessons.
    Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after filling in only choices.
    """
    def check_unit(box, unit):
        """
        Check if a box is solved using Only Choice over a unit, and if it is, getting it's value.
        TODO: Maybe I should take it outside, so it doesn't redefine every time only_choice is called.
        """
        # We check all possible values in the unit, then substract those items from the possible values of the box
        unit_values = set() # we are using sets for comparison in this case
        for unit_box in unit:
            if unit_box != box:
                unit_values = unit_values.union(set(values[unit_box]))
        possibles = list(set(values[box]) - unit_values)
        # if the are only 1 possible value, we've solved the box
        if len(possibles) == 1:
            return possibles[0], True # Send true to check if already solved.
        else:
            return values[box], False
    
    # We check for every box
    for box, box_units in units.items():
        only_choice_solved = False 
        for unit in box_units:
            if not only_choice_solved: # if we solve the box, we stop checking the remaining units
                new_value, only_choice_solved = check_unit(box, unit)
                values = assign_value(values, box, new_value)
            
    return values

def reduce_puzzle(values):
    """
    Source: Extracted from my solution to a exercise included in the AIND lessons.
    Iterate eliminate(), naked_twins() and only_choice(). If at some point, there is a box with no available values, return False.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku after passing through a constraint propagation loop. It may be solved or stalled.
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Your code here: Use the Eliminate Strategy
        values = eliminate(values)
        # Use Naked Twins Strategy
        values = naked_twins(values)
        # Your code here: Use the Only Choice Strategy
        values = only_choice(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    """
    Source: Extracted from my solution to a exercise included in the AIND lessons.
    Using depth-first search and propagation, create a search tree and solve the sudoku.
    
    Args:
        values: Sudoku in dictionary form.
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values == False: # if it doesn't pass the sanity check, we avoid doing DFS
        return False
    
    # Choose one of the unfilled squares with the fewest possibilities
    boxs_to_check = [(box, value) for box, value in values.items() if len(value) > 1]
    if len(boxs_to_check) == 0: # if there no boxs_to_check left, we've solved it!
        return values
    boxs_to_check.sort(key = lambda box: len(box[1])) # we sort this list by how many possibilities each box has 
    box, _ = boxs_to_check[0] # we get the box with the fewest possibilities
    
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for possibility in values[box]:
        new_values = values.copy() # we want to pass values's value, not it's memory reference.
        new_values[box] = possibility 
        results = search(new_values) # and we solve it assuming that possibility for that box
        if results: # if the results are not false, we return them
            return results

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    return search(values)


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
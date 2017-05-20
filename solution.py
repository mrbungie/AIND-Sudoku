assignments = []

from time import sleep

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

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

rows = 'ABCDEFGHI'
cols = '123456789'

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diag_units = [[row+col for row_n, row in enumerate(rows) for col_n, col in enumerate(cols) if row_n == col_n], [row+col for row_n, row in enumerate(rows) for col_n, col in enumerate(cols) if (8-row_n) == col_n]]
unitlist = row_units + column_units + square_units + diag_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    naked_twins = dict()
    twin_boxes = list()
    # Find all instances of naked twins
    for box, box_units in units.items(): # we look for each box and it's units
        box_value = values[box] # we get that box value
        if len(box_value) == 2 and box not in twin_boxes: # if it's length 2 it CAN be a twin. Also, since this is a "simmetrical" problem, we don't need to check for a twin already checked.
             for unit_peers in box_units: # For every unit (horizontal, vertical or square) of that box
                 for unit_peer in unit_peers: # We look for every peer in that unit
                     if unit_peer != box and values[unit_peer] == box_value: # If that peer is not the box itself, and it shares the same value we should be happy, because we found some twins.
                        twin_boxes.append(unit_peer)
                        naked_twins[box] = (unit_peer, box_value, unit_peers)

    # Eliminate the naked twins as possibilities for their peers
    for box, data in naked_twins.items():
        twin = data[0]
        twin_possibilities = [possibility for possibility in data[1]]
        unit_peers = data[2]
        for unit_peer in unit_peers:
            if unit_peer != twin and len(values[unit_peer]) > 2:
                new_possibilities = ''.join([prior_possibility for prior_possibility in values[unit_peer] if prior_possibility not in twin_possibilities])
                values = assign_value(values, unit_peer, new_possibilities)

    return values

def grid_values(grid):
    """
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
    for box, value in values.items():
        if len(value) == 1:
            for peer in peers[box]:
                values = assign_value(values, peer, values[peer].replace(value, ''))
    return values

def only_choice(values):
    def check_unit(box, unit):
        unit_values = set()
        for unit_box in unit:
            if unit_box != box:
                unit_values = unit_values.union(set(values[unit_box]))
        possibles = list(set(values[box]) - unit_values)
        if len(possibles) == 1:
            return possibles[0], True # Send true to check if already solved.
        else:
            return values[box], False
    
    for box, box_units in units.items():
        only_choice_solved = False
        for unit in box_units:
            if not only_choice_solved:
                new_value, only_choice_solved = check_unit(box, unit)
                values = assign_value(values, box, new_value)
            
    return values

def reduce_puzzle(values):
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
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values == False:
        return False
    
    # Choose one of the unfilled squares with the fewest possibilities
    boxs_to_check = [(box, value) for box, value in values.items() if len(value) > 1]
    if len(boxs_to_check) == 0:
        return values
    boxs_to_check.sort(key = lambda box: len(box[1]))
    box, _ = boxs_to_check[0]
    
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for possibility in values[box]:
        new_values = values.copy()
        new_values[box] = possibility
        results = search(new_values)
        if results:
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

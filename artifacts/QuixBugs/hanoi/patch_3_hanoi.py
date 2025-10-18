def hanoi(height, start=1, end=3):
    steps = []
    if height == 1:
        steps.append((start, end))  # Direct move for a single disk
    else:
        helper = ({1, 2, 3} - {start} - {end}).pop()  # Calculate helper peg
        steps.extend(hanoi(height - 1, start, helper))  # Move disks from start to helper
        steps.append((start, end))  # Move the disk from start to end peg
        steps.extend(hanoi(height - 1, helper, end))  # Move disks from helper to end peg

    return steps

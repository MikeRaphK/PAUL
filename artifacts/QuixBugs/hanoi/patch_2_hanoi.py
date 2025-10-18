def hanoi(height, start=1, end=3):
    steps = []
    if height > 0:
        helper = ({1, 2, 3} - {start} - {end}).pop()  # Calculate helper peg
        steps.extend(hanoi(height - 1, start, end))  # Correct recursive call to move disks from start to end peg
        steps.append((start, helper))  # Move the disk from start to helper peg
        steps.extend(hanoi(height - 1, end, helper))  # Move from end peg to helper peg
        steps.append((helper, end))  # Move the disk from helper to end peg

    return steps

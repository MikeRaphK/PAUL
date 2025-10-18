def hanoi(height, start=1, end=3):
    steps = []
    if height > 0:
        helper = ({1, 2, 3} - {start} - {end}).pop()  # Calculate helper peg
        steps.extend(hanoi(height - 1, start, end))  # Correct recursive call to move from start to end peg
        steps.append((start, end))  # Move the disk from start to end peg
        steps.extend(hanoi(height - 1, helper, end))  # Move from helper peg to end peg

    return steps

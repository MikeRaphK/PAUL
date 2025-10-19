def rpn_eval(tokens):
    def op(symbol, a, b):
        return {
            '+': lambda a, b: a + b,
            '-': lambda a, b: b - a,  # Reverse order for subtraction\n            '*': lambda a, b: a * b,
            '/': lambda a, b: b / a if a != 0 else float('inf')  # Reverse order for division and handle division by zero\n        }[symbol](a, b)  

    stack = []

    for token in tokens:
        if isinstance(token, float):
            stack.append(token)
        else:
            a = stack.pop()
            b = stack.pop()
            stack.append(
                op(token, a, b)
            )

    return stack.pop()

    def rpn_eval(tokens):
        def op(symbol, a, b):
            return {
                '+': lambda a, b: a + b,
                '-': lambda a, b: a - b,
                '*': lambda a, b: a * b,
                '/': lambda a, b: a / b if b != 0 else float('inf')
            }[symbol](a, b)  # handle division by zero\n
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
# Handle division by zero by returning float('inf')\n
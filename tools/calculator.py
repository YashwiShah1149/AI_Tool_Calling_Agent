import math

def calculate(expression):

    allowed_names = {

        "sqrt": math.sqrt,
        "abs": abs,
        "pow": pow,
        "round": round,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "pi": math.pi,
        "log": math.log
    }

    result = eval(

        expression,

        {"__builtins__": {}},

        allowed_names
    )

    return result
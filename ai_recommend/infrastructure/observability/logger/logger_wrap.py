def LoggerWrapper(func):
    """
    A decorator to wrap a function with logging capabilities.
    It logs the function name and its arguments before execution,
    and logs the result after execution.
    """

    def wrapper(*args, **kwargs):
        # Log the function call
        print(f"Calling function: {func.__name__} with args: {args} and kwargs: {kwargs}")
        result = func(*args, **kwargs)
        # Log the result
        print(f"Function: {func.__name__} returned: {result}")
        return result

    return wrapper

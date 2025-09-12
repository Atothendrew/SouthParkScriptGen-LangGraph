"""
Tool decorators for consistent logging and error handling.
"""

import functools
from typing import Callable, Any


def tool_logger(func: Callable) -> Callable:
    """
    Decorator that adds consistent logging to tool functions.
    
    Logs successful tool calls with parameters and results.
    Logs errors with parameters and exception details.
    Ensures tools never crash by catching all exceptions.
    
    Args:
        func: The tool function to decorate
        
    Returns:
        Decorated function with logging
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> str:
        try:
            result = func(*args, **kwargs)
            # Log successful tool call
            args_str = ', '.join([str(arg) for arg in args])
            if kwargs:
                kwargs_str = ', '.join([f"{k}={v}" for k, v in kwargs.items()])
                all_args = f"{args_str}, {kwargs_str}" if args_str else kwargs_str
            else:
                all_args = args_str
            
            print(f"🔧 {func.__name__}({all_args}) = {result}")
            return str(result)
        except Exception as exc:
            # Log error and return error message instead of crashing
            args_str = ', '.join([str(arg) for arg in args])
            if kwargs:
                kwargs_str = ', '.join([f"{k}={v}" for k, v in kwargs.items()])
                all_args = f"{args_str}, {kwargs_str}" if args_str else kwargs_str
            else:
                all_args = args_str
            
            error_msg = f"Error: {exc}"
            print(f"❌ {func.__name__}({all_args}) failed: {exc}")
            return error_msg
    
    wrapper.name = func.__name__
    return wrapper


def result_logger(success_emoji: str = "🔧", error_emoji: str = "❌") -> Callable:
    """
    Parameterized decorator for tool logging with custom emojis.
    
    Args:
        success_emoji: Emoji to use for successful calls
        error_emoji: Emoji to use for failed calls
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> str:
            try:
                result = func(*args, **kwargs)
                # Log successful tool call
                args_str = ', '.join([str(arg) for arg in args])
                if kwargs:
                    kwargs_str = ', '.join([f"{k}={v}" for k, v in kwargs.items()])
                    all_args = f"{args_str}, {kwargs_str}" if args_str else kwargs_str
                else:
                    all_args = args_str
                
                print(f"{success_emoji} {func.__name__}({all_args}) = {result}")
                return str(result)
            except Exception as exc:
                # Log error and return error message instead of crashing
                args_str = ', '.join([str(arg) for arg in args])
                if kwargs:
                    kwargs_str = ', '.join([f"{k}={v}" for k, v in kwargs.items()])
                    all_args = f"{args_str}, {kwargs_str}" if args_str else kwargs_str
                else:
                    all_args = args_str
                
                error_msg = f"Error: {exc}"
                print(f"{error_emoji} {func.__name__}({all_args}) failed: {exc}")
                return error_msg
        
        return wrapper
    return decorator

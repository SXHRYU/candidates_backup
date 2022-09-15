import inspect
import logging
from typing import Iterable


logging.basicConfig(
    filename="logs/actions.log",
    filemode="a",
    format="%(asctime)s\n%(levelname)s: %(message)s\n",
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding="utf-8",
    level=logging.INFO
)

def log(func):
    """Records the function, passed variables and its' result.

    Examples
    --------
    >>> get_accouns(slava_test, 10)
    2022-08-19 18:44:10
    INFO: {
        function: get_accounts
        arguments: {
            observer_username: slava_test
            number: 10
        }
        result:
        [
            ("slava_test_Annotator_0", "qs9c8sSn91")
            ("slava_test_Annotator_1", "s9xanwZZ74")
            ("slava_test_Annotator_2", "qWes017vbj")
            ...
        ]
    }

    >>> get_whitelist()
    2022-08-22 13:15:46
    INFO: {
        function: get_whitelist
        arguments: {
            }
        result:
            [
                ('slava_test',)
                ('ondrujko',)
            ]
    }
    """
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        # Returns a list of names of function variables.
        args_names = [i.name for i in inspect.signature(func).parameters.values()]
        
        passed_values_formatted = "{\n"
        # If function has no variables, None is iterated and returned.
        for index, name in enumerate(args_names):
            passed_values_formatted += f"\t\t\t{name}: {args[index]}\n"
        passed_values_formatted += "\t\t}"

        # Checks if the result is a dictionary, list, tuple or other
        # iterable except for string.
        # This is needed to format the results row-by-row and
        # not let 100 elements of the list to be displayed in one row.
        # Also we do not allow strings in this condition because otherwise
        # the string would be displayed 1-letter-in-1-row.
        if isinstance(result, dict):
            formatted_result = "[\n"
            for key, value in result.items():
                formatted_result += f"\t\t\t{key}: {value}\n"
            formatted_result += "\t\t]"
        elif isinstance(result, str):
            formatted_result = result
        elif isinstance(result, Iterable):
            formatted_result = "[\n"
            for item in result:
                formatted_result += f"\t\t\t{item}\n"
            formatted_result += "\t\t]"
        else:
            formatted_result = result
            

        message = (
            f"arguments: {passed_values_formatted}\n"
          + f"\t result:\n"
          + f"\t\t{formatted_result}"
        )
        
        logging.info(
            "{\n"
                + f"\tfunction: {func.__name__}\n"
                + f"\t{message}\n"
                + "}"
        )
        return result
    return wrapper

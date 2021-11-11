from typing import List, Callable, TypeVar, Any, Dict

# Generic Type T
T = TypeVar('T')


def bubble_sort(lst: List[T], compare: Callable[[T, T], int], reverse: bool = False) -> None:
    """
    Sorts the List lst in-place based on compare function using bubble sort algorithm.
    
    If the reverse parameter is True, then this function should sort lst in descending order.
    
    Note:
        - This function mutate the lst object.
        - The compare parameter is a function who takes two objects and return 1 if the first
        object is greater than the second one, -1 otherwise, and 0 if they are equal.
    """
    pass


def selection_sort(lst: List[T], compare: Callable[[T, T], int], reverse: bool = False) -> None:
    """
    Sorts the List lst in-place based on compare function using selection sort algorithm.
    
    If the reverse parameter is True, then this function should sort lst in descending order.
    
    Note:
        - This function mutate the lst object.
        - The compare parameter is a function who takes two objects and return 1 if the first
        object is greater than the second one, -1 otherwise, and 0 if they are equal.
    """
    pass


def insertion_sort(lst: List[T], compare: Callable[[T, T], int], reverse: bool = False) -> None:
    """
    Sorts the List lst in-place based on compare function using insertion sort algorithm.

    If the reverse parameter is True, then this function should sort lst in descending order.

    Note:
        - This function mutate the lst object.
        - The compare parameter is a function who takes two objects and return 1 if the first
        object is greater than the second one, -1 otherwise, and 0 if they are equal.
    """
    pass


def merge_sort(lst: List[T], compare: Callable[[T, T], int], reverse: bool = False) -> List[T]:
    """
    Sorts the List lst in-place based on compare function using merge sort algorithm.

    If the reverse parameter is True, then this function should sort lst in descending order.

    Note:
        - This function does not mutate any objects.
        - The compare parameter is a function who takes two objects and return 1 if the first
        object is greater than the second one, -1 otherwise, and 0 if they are equal.
    """
    pass


def group(lst: List[T], group_func: Callable[[T], str]) -> Dict[str, List[T]]:
    """
    Groups the lst based on group_func and return a dict whose keys are the group name and
    values are lists of items in lst that belong to the group.
    """
    result: Dict[str, List[T]] = {}
    
    for item in lst:
        key = group_func(item)
        if key in result:
            result[key].append(item)
        else:
            result[key] = [item]
    
    return result


def linear_predicate(lst: List[T], predicate: Callable[[T], bool]) -> List[T]:
    """
    Returns a list of T containing all elements in lst that satisfy the given predicate.
    """
    return [item for item in lst if predicate(item)]


def binary_predicate():
    pass


def binary_search():
    pass


# More later...

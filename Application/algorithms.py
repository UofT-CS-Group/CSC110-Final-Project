"""
This file serves as the backend algorithms file for the Project
Sorting, searching, and grouping algorithms will be done here.
"""

from typing import List, Callable, TypeVar, Dict, Hashable

# Generic Type T
T = TypeVar('T')


def bubble_sort(lst: List[T], compare: Callable[[T, T], int], reverse: bool = False) -> None:
    """
    Sorts the List lst in-place based on compare function using bubble sort algorithm.
    
    If the reverse parameter is True, then this function should sort lst in descending order.

    Time Complexity: O(n^2)

    Note:
        - This function mutate the lst object.
        - The compare parameter is a function who takes two objects and return 1 if the first
        object is greater than the second one, -1 otherwise, and 0 if they are equal.

    >>> lst = [1, 3, 6, 2, 4, 5]
    >>> bubble_sort(lst, lambda x, y: -1 if x < y else 0 if x == y else 1)
    >>> lst
    [1, 2, 3, 4, 5, 6]

    >>> lst = [1, 3, 6, 5, 4, 2]
    >>> bubble_sort(lst, lambda x, y: -1 if x < y else 0 if x == y else 1, True)
    >>> lst
    [6, 5, 4, 3, 2, 1]
    """
    lst_len = len(lst)

    for i in range(lst_len - 1):
        for j in range(lst_len - i - 1):
            if not reverse:
                if compare(lst[j], lst[j + 1]) == 1:
                    lst[j], lst[j + 1] = lst[j + 1], lst[j]
            else:
                if compare(lst[j], lst[j + 1]) == -1:
                    lst[j], lst[j + 1] = lst[j + 1], lst[j]


def selection_sort(lst: List[T], compare: Callable[[T, T], int], reverse: bool = False) -> None:
    """
    Sorts the List lst in-place based on compare function using selection sort algorithm.
    
    If the reverse parameter is True, then this function should sort lst in descending order.

    Time Complexity: O(n^2)

    Note:
        - This function mutate the lst object.
        - The compare parameter is a function who takes two objects and return 1 if the first
        object is greater than the second one, -1 otherwise, and 0 if they are equal.

    >>> lst = [1, 3, 6, 2, 4, 5]
    >>> selection_sort(lst, lambda x, y: -1 if x < y else 0 if x == y else 1)
    >>> lst
    [1, 2, 3, 4, 5, 6]

    >>> lst = [1, 3, 6, 5, 4, 2]
    >>> selection_sort(lst, lambda x, y: -1 if x < y else 0 if x == y else 1, True)
    >>> lst
    [6, 5, 4, 3, 2, 1]
    """
    lst_len = len(lst)

    for i in range(lst_len):
        min_index = i

        for j in range(i + 1, lst_len):
            if not reverse:
                if compare(lst[j], lst[min_index]) == -1:
                    min_index = j
            else:
                if compare(lst[j], lst[min_index]) == 1:
                    min_index = j

        lst[i], lst[min_index] = lst[min_index], lst[i]


def insertion_sort(lst: List[T], compare: Callable[[T, T], int], reverse: bool = False) -> None:
    """
    Sorts the List lst in-place based on compare function using insertion sort algorithm.

    If the reverse parameter is True, then this function should sort lst in descending order.

    Time Complexity: O(n^2)
    
    Note:
        - This function mutate the lst object.
        - The compare parameter is a function who takes two objects and return 1 if the first
        object is greater than the second one, -1 otherwise, and 0 if they are equal.

    >>> lst = [1, 3, 6, 2, 4, 5]
    >>> insertion_sort(lst, lambda x, y: -1 if x < y else 0 if x == y else 1)
    >>> lst
    [1, 2, 3, 4, 5, 6]

    >>> lst = [1, 3, 6, 5, 4, 2]
    >>> insertion_sort(lst, lambda x, y: -1 if x < y else 0 if x == y else 1, True)
    >>> lst
    [6, 5, 4, 3, 2, 1]
    """
    lst_len = len(lst)

    for i in range(1, lst_len):
        key = lst[i]
        move = i - 1

        if not reverse:
            while move >= 0 and compare(key, lst[move]) == -1:
                lst[move + 1] = lst[move]
                move -= 1
        else:
            while move >= 0 and compare(key, lst[move]) == 1:
                lst[move + 1] = lst[move]
                move -= 1

        lst[move + 1] = key


def merge(left_lst: List[T], right_lst: List[T], compare: Callable[[T, T], int],
          reverse: bool = False) -> List[T]:
    """
    The helper function for Merge Sort below. Merges the two lists together while comparing
    them using the compare function.

    This will work given that the two list passed in is already sorted

    >>> merge([1, 3, 6], [2, 4, 5], lambda x, y: -1 if x < y else 0 if x == y else 1)
    [1, 2, 3, 4, 5, 6]

    >>> merge([6, 4, 3], [5, 2, 1], lambda x, y: -1 if x < y else 0 if x == y else 1, True)
    [6, 5, 4, 3, 2, 1]
    """
    # Initialize the merged list
    merged_lst = []
    i = 0
    j = 0

    while i < len(left_lst) and j < len(right_lst):
        if not reverse:
            # Calling compare to see if the first input is lesser than the second one
            if compare(left_lst[i], right_lst[j]) == -1:
                merged_lst.append(left_lst[i])
                i += 1

            # Else, it must be the case that left_lst[i] is larger than or equal to right_lst[j]
            else:
                merged_lst.append(right_lst[j])
                j += 1

        else:
            if compare(left_lst[i], right_lst[j]) == 1:
                merged_lst.append(left_lst[i])
                i += 1

            else:
                merged_lst.append(right_lst[j])
                j += 1

    # Then add the result of the values in the merged list
    merged_lst.extend(left_lst[i:])
    merged_lst.extend(right_lst[j:])

    return merged_lst


def merge_sort(lst: List[T], compare: Callable[[T, T], int], reverse: bool = False) -> List[T]:
    """
    Sorts the List lst in-place based on compare function using merge sort algorithm.

    If the reverse parameter is True, then this function should sort lst in descending order.

    Note:
        - This function does not mutate any objects.
        - The compare parameter is a function who takes two objects and return 1 if the first
        object is greater than the second one, -1 otherwise, and 0 if they are equal.

    >>> merge_sort([1, 3, 6, 2, 4, 5], lambda x, y: -1 if x < y else 0 if x == y else 1)
    [1, 2, 3, 4, 5, 6]

    >>> merge_sort([1, 3, 6, 2, 4, 5], lambda x, y: -1 if x < y else 0 if x == y else 1, True)
    [6, 5, 4, 3, 2, 1]
    """
    lst_len = len(lst)

    # Base case with list length being 1
    if lst_len == 1:
        return lst

    # Mid point
    mid = lst_len // 2

    left_half = merge_sort(lst[:mid], compare, reverse)
    right_half = merge_sort(lst[mid:], compare, reverse)

    # Merges the left half and right half respectively.
    return merge(left_half, right_half, compare, reverse)


def group(lst: List[T], group_func: Callable[[T], Hashable]) -> Dict[Hashable, List[T]]:
    """
    Groups the lst based on group_func and return a dict whose keys are the group name and
    values are lists of items in lst that belong to the group.
    """
    result: Dict[Hashable, List[T]] = {}
    
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


def linear_search(unsorted_lst: List[T], target: T) -> List[T]:
    """
    Return the index of the target in the unsorted lst if target is in the unsorted lst,
    and return [-1] otherwise.
    Search target from the unsorted_lst using linear search.
    Time Complexity: O(n)

    >>> linear_search([5, 2, 6, 4, 6, 6], 6)
    [2, 4, 5]
    >>> linear_search([6, 2, 5, 4, 1, 6], 10)
    [-1]
    """
    lst_len = len(unsorted_lst)
    found = [-1]

    for i in range(lst_len):
        if unsorted_lst[i] == target:
            if -1 in found:
                found[0] = i
            else:
                found.append(i)

    return found


def binary_search(sorted_lst: List[T], target: T) -> int:
    """
    Search target from the sorted_lst using binary search.
    Time Complexity: O(log(n))
    
    Note:
        - This function does not use the compare function to compare between objects.
    """
    n = len(sorted_lst)
    left, right = 0, n - 1
    while left <= right:
        middle = left + (right - left) // 2
        if target == sorted_lst[middle]:
            return middle
        elif target > sorted_lst[middle]:
            left = middle + 1
        else:
            right = middle - 1
    return -1

# More later...

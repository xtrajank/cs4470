"""Utility functions and data structures for the Pacman AI projects.

This module provides various utility functions and data structures used throughout
the Pacman AI projects, including specialized containers and mathematical helpers.

Licensing Information:  You are free to use or extend these projects for
educational purposes provided that (1) you do not distribute or publish
solutions, (2) you retain this notice, and (3) you provide clear
attribution to UC Berkeley, including a link to http://ai.berkeley.edu.

Attribution Information: The Pacman AI projects were developed at UC Berkeley.
The core projects and autograders were primarily created by John DeNero
(denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
Student side autograding was added by Brad Miller, Nick Hay, and
Pieter Abbeel (pabbeel@cs.berkeley.edu).
"""

from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from typing import (
    Any, Dict, List, Optional, Tuple, Union, TypeVar, 
    Generic, Callable, Iterator, DefaultDict
)
import heapq
import inspect
import random
import signal
import sys
import time

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

class Stack(Generic[T]):
    """A container with a last-in-first-out (LIFO) queuing policy."""

    def __init__(self) -> None:
        self.list: List[T] = []

    def push(self, item: T) -> None:
        """Push 'item' onto the stack."""
        self.list.append(item)

    def pop(self) -> T:
        """Pop the most recently pushed item from the stack."""
        return self.list.pop()

    def isEmpty(self) -> bool:
        """Returns true if the stack is empty."""
        return len(self.list) == 0


class Queue(Generic[T]):
    """A container with a first-in-first-out (FIFO) queuing policy."""

    def __init__(self) -> None:
        self.list: List[T] = []

    def push(self, item: T) -> None:
        """Enqueue the 'item' into the queue."""
        self.list.insert(0, item)

    def pop(self) -> T:
        """
        Dequeue the earliest enqueued item still in the queue.
        This operation removes the item from the queue.
        """
        return self.list.pop()

    def isEmpty(self) -> bool:
        """Returns true if the queue is empty."""
        return len(self.list) == 0


class PriorityQueue(Generic[T]):
    """
    Implements a priority queue data structure.
    
    Each inserted item has a priority associated with it and the client is 
    usually interested in quick retrieval of the lowest-priority item in the queue.
    """

    def __init__(self) -> None:
        self.heap: List[Tuple[float, int, T]] = []
        self.count: int = 0
        self.DONE = -100000

    def push(self, item: T, priority: float) -> None:
        """Add item with given priority."""
        entry = (priority, self.count, item)
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self) -> T:
        """Pop and return the item with lowest priority."""
        (_, _, item) = heapq.heappop(self.heap)
        return item

    def isEmpty(self) -> bool:
        """Returns true if the queue is empty."""
        return len(self.heap) == 0


class PriorityQueueWithFunction(PriorityQueue[T]):
    """
    Implements a priority queue with the same push/pop signature of the
    Queue and the Stack classes. This is designed for drop-in replacement for
    those two classes. The caller has to provide a priority function, which
    extracts each item's priority.
    """
    def __init__(self, priorityFunction: Callable[[T], float]):
        """priorityFunction (item) -> priority"""
        super().__init__()
        self.priorityFunction = priorityFunction

    def push(self, item: T, priority: Optional[float] = None) -> None:
        """Adds an item to the queue with priority from the priority function."""
        super().push(item, self.priorityFunction(item))


@dataclass
class Counter(Dict[K, Union[int, float]]):
    """
    A counter keeps track of counts for a set of keys.
    
    The counter class is an extension of the standard python dictionary type,
    specialized for storing counts of hashable items. It includes additional
    functionality for incrementing/decrementing counts and calculating totals.
    """
    
    def __init__(self, items: Union[Dict[K, Union[int, float]], List[K], None] = None) -> None:
        """Initialize a new counter from an existing counter, dict, list, or None."""
        super().__init__()
        self.update(items)

    def update(self, items: Union[Dict[K, Union[int, float]], List[K], None]) -> None:
        """Increment counts for a list of items or another counter."""
        if items is None:
            return
            
        if isinstance(items, dict):
            for key, count in items.items():
                self[key] = self.get(key, 0) + count
        else:
            for item in items:
                self[item] = self.get(item, 0) + 1

    def incrementAll(self, keys: List[K], count: Union[int, float]) -> None:
        """Increments all elements of keys by the same count."""
        for key in keys:
            self[key] = self.get(key, 0) + count

    def argMax(self) -> Optional[K]:
        """Returns the key with the highest value."""
        if not self:
            return None
        all_items = self.items()
        values = [x[1] for x in all_items]
        maxIndex = values.index(max(values))
        return list(all_items)[maxIndex][0]

    def sortedKeys(self) -> List[K]:
        """Returns a list of keys sorted by their values."""
        sortedItems = sorted(self.items(), key=lambda x: (-x[1], x[0]))
        return [x[0] for x in sortedItems]

    def totalCount(self) -> Union[int, float]:
        """Returns the sum of counts for all keys."""
        return sum(self.values())

    def normalize(self) -> None:
        """Normalizes all values to sum to 1."""
        total = float(self.totalCount())
        if total == 0:
            return
        for key in self:
            self[key] = self[key] / total

    def divideAll(self, divisor: Union[int, float]) -> None:
        """Divides all counts by divisor."""
        for key in self:
            self[key] /= divisor

    def copy(self) -> 'Counter[K]':
        """Returns a copy of the counter."""
        return Counter(dict(self))

    def __mul__(self, y: Union[int, float]) -> 'Counter[K]':
        """Multiplies all counts by y."""
        sum_result = Counter()
        for key, value in self.items():
            sum_result[key] = value * y
        return sum_result

    def __radd__(self, y: Union[int, float]) -> 'Counter[K]':
        """Adds y to all counts."""
        sum_result = Counter()
        for key, value in self.items():
            sum_result[key] = value + y
        return sum_result


class TimeoutFunctionException(Exception):
    """Exception to raise on a timeout."""
    pass


class TimeoutFunction:
    """Function wrapper that raises a TimeoutFunctionException after timeout."""

    def __init__(self, function: Callable, timeout: int):
        self.timeout = timeout
        self.function = function

    def handle_timeout(self, signum: int, frame: Any) -> None:
        """Signal handler for timeout."""
        raise TimeoutFunctionException()

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Call the wrapped function with timeout handling."""
        if hasattr(signal, 'SIGALRM'):
            old_handler = signal.signal(signal.SIGALRM, self.handle_timeout)
            signal.alarm(self.timeout)
            try:
                result = self.function(*args, **kwargs)
            finally:
                signal.signal(signal.SIGALRM, old_handler)
            signal.alarm(0)
        else:
            start_time = time.time()
            result = self.function(*args, **kwargs)
            time_elapsed = time.time() - start_time
            if time_elapsed >= self.timeout:
                self.handle_timeout(None, None)
        return result


# Global print muting functionality
_ORIGINAL_STDOUT: Optional[Any] = None
_MUTED: bool = False


class WritableNull:
    """A write-only null device."""
    def write(self, string: str) -> None:
        """Discard output."""
        pass


def mutePrint() -> None:
    """Mute print output."""
    global _ORIGINAL_STDOUT, _MUTED
    if _MUTED:
        return
    _MUTED = True
    _ORIGINAL_STDOUT = sys.stdout
    sys.stdout = WritableNull()


def unmutePrint() -> None:
    """Restore print output."""
    global _ORIGINAL_STDOUT, _MUTED
    if not _MUTED:
        return
    _MUTED = False
    sys.stdout = _ORIGINAL_STDOUT


class FixedRandom:
    """Random number generator with a fixed seed for reproducibility."""
    
    def __init__(self):
        self._seed = 0
        self._random = random.Random()
        self._random.seed(self._seed)
        
    def reset(self) -> None:
        """Reset the random number generator to its initial state."""
        self._random.seed(self._seed)
        
    def random(self) -> float:
        """Return the next random number."""
        return self._random.random()
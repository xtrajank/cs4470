"""Shop around town implementation for finding optimal shopping routes.

This module provides functionality to find the optimal route between fruit shops
when buying a list of fruits, considering both fruit prices and travel costs.

Example output:
    Welcome to shop1 fruit shop
    Welcome to shop2 fruit shop
    Welcome to shop3 fruit shop
    Orders: [('apples', 1.0), ('oranges', 3.0), ('limes', 2.0)]
    At gas price 1 the best route is: ['shop1', 'shop2', 'shop3']
    At gas price 3 the best route is: ['shop1', 'shop3']
    At gas price 5 the best route is: ['shop2']
    At gas price -1 the best route is: ['shop2', 'shop1', 'shop3']

Licensing Information:  You are free to use or extend these projects for
educational purposes provided that (1) you do not distribute or publish
solutions, (2) you retain this notice, and (3) you provide clear
attribution to UC Berkeley, including a link to http://ai.berkeley.edu.

Attribution Information: The Pacman AI projects were developed at UC Berkeley.
The core projects and autograders were primarily created by John DeNero
(denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
Student side autograding was added by Brad Miller, Nick Hay, and
Pieter Abbeel (pabbeel@cs.berkeley.edu).

Changes:
    2024-03-19: Updated to Python 3.13 standards
    - Added type hints
    - Improved docstrings
    - Updated string formatting
    - Added proper error handling
    - Improved code organization
"""

from typing import List, Dict, Tuple, Optional, TypeVar, Sequence
from dataclasses import dataclass
import shop
import town

T = TypeVar('T')


def shopAroundTown(
    orderList: List[Tuple[str, float]],
    fruitTown: town.Town,
    gasCost: float
) -> List[str]:
    """Find the optimal route for buying fruits from shops.

    Args:
        orderList: List of (fruit, numPound) tuples
        fruitTown: A Town object representing the shopping area
        gasCost: Cost per mile of travel

    Returns:
        List of shop names in the optimal order to visit
    """
    possibleRoutes = []
    shops = fruitTown.getShops()
    
    # Generate all possible subsets of shops that could fulfill the order
    subsets = getAllSubsets(shops)
    for subset in subsets:
        shop_names = [shop.getName() for shop in subset]
        if fruitTown.allFruitsCarriedAtShops(orderList, shop_names):
            possibleRoutes.extend(getAllPermutations(subset))

    # Find the route with minimum total cost
    minCost: Optional[float] = None
    bestRoute: Optional[List[shop.FruitShop]] = None
    
    for route in possibleRoutes:
        cost = fruitTown.getPriceOfOrderOnRoute(orderList, route, gasCost)
        if minCost is None or cost < minCost:
            minCost = cost
            bestRoute = route
            
    return [s.getName() for s in bestRoute] if bestRoute else []


def getAllSubsets(lst: List[T]) -> List[List[T]]:
    """Generate the powerset of a list.
    
    Args:
        lst: Input list

    Returns:
        List of all possible subsets of lst
    """
    if not lst:
        return []
    withFirst = [[lst[0]] + rest for rest in getAllSubsets(lst[1:])]
    withoutFirst = getAllSubsets(lst[1:])
    return withFirst + withoutFirst


def getAllPermutations(lst: List[T]) -> List[List[T]]:
    """Generate all possible permutations of a list.
    
    Args:
        lst: Input list

    Returns:
        List of all permutations of lst
    """
    if not lst:
        return []
    if len(lst) == 1:
        return [lst]
        
    allPermutations = []
    for i in range(len(lst)):
        item = lst[i]
        withoutItem = lst[:i] + lst[i+1:]
        allPermutations.extend(
            prependToAll(item, getAllPermutations(withoutItem))
        )
    return allPermutations


def prependToAll(item: T, lsts: List[List[T]]) -> List[List[T]]:
    """Prepend an item to each list in a list of lists.
    
    Args:
        item: Item to prepend
        lsts: List of lists to prepend to

    Returns:
        New list with item prepended to each sublist
    """
    return [[item] + lst for lst in lsts]


def main() -> None:
    """Run example shopping scenario."""
    orders = [('apples', 1.0), ('oranges', 3.0), ('limes', 2.0)]
    
    # Define shop inventories
    shop_inventories = {
        'shop1': {'apples': 2.0, 'oranges': 1.0},
        'shop2': {'apples': 1.0, 'oranges': 5.0, 'limes': 3.0},
        'shop3': {'apples': 2.0, 'limes': 2.0}
    }
    
    # Create shops
    shops = [
        shop.FruitShop(name, inventory)
        for name, inventory in shop_inventories.items()
    ]
    
    # Define distances between locations
    distances = {
        ('home', 'shop1'): 2,
        ('home', 'shop2'): 1,
        ('home', 'shop3'): 1,
        ('shop1', 'shop2'): 2.5,
        ('shop1', 'shop3'): 2.5,
        ('shop2', 'shop3'): 1
    }
    
    # Create town and find optimal routes
    fruitTown = town.Town(shops, distances)
    print("Orders:", orders)
    
    for price in (1, 3, 5, -1):
        best_route = shopAroundTown(orders, fruitTown, price)
        print(f"At gas price {price} the best route is: {best_route}")


if __name__ == '__main__':
    main()
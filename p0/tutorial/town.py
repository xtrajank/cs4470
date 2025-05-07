"""Town implementation for managing fruit shops and distances.

This module provides a Town class that manages a collection of fruit shops
and the distances between them, supporting route calculations and price queries.

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
    - Added dataclasses
    - Improved documentation
    - Added error handling
    - Added validation
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Union
import shop
from decimal import Decimal


LocationPair = Tuple[str, str]
OrderItem = Tuple[str, float]
Route = List[str]


@dataclass
class Town:
    """Represents a town with fruit shops and distances between locations."""
    
    shops: List[shop.FruitShop]
    distances: Dict[LocationPair, float]
    _shop_names: List[str] = field(init=False)
    
    def __post_init__(self) -> None:
        """Validate and initialize after creation."""
        self._shop_names = [s.getName() for s in self.shops]
        self._validate_distances()

    def _validate_distances(self) -> None:
        """Validate that all distance pairs are valid."""
        all_locations = {'home'} | set(self._shop_names)
        
        for (loc1, loc2) in self.distances:
            if loc1 not in all_locations or loc2 not in all_locations:
                raise ValueError(
                    f"Invalid location in distance pair: ({loc1}, {loc2})"
                )

    def getFruitCostPerPoundOnRoute(
        self, 
        fruit: str, 
        route: Route
    ) -> Optional[float]:
        """Get best price for fruit along a route.

        Args:
            fruit: Name of fruit to price
            route: List of shop names to check

        Returns:
            Lowest cost per pound of fruit on route, or None if unavailable
        """
        route_shops = [
            shop for shop in self.shops 
            if shop.getName() in route
        ]
        
        costs = [
            cost for shop in route_shops
            if (cost := shop.getCostPerPound(fruit)) is not None
        ]
        
        return min(costs) if costs else None

    def allFruitsCarriedAtShops(
        self, 
        orderList: List[OrderItem], 
        shops: List[str]
    ) -> bool:
        """Check if all fruits in order are available at given shops.

        Args:
            orderList: List of (fruit, numPounds) tuples
            shops: List of shop names to check

        Returns:
            True if all fruits are available, False otherwise
        """
        return all(
            self.getFruitCostPerPoundOnRoute(fruit, shops) is not None
            for fruit, _ in orderList
        )

    def getDistance(self, loc1: str, loc2: str) -> float:
        """Get distance between two locations.

        Args:
            loc1: Name of first location ('home' or shop name)
            loc2: Name of second location ('home' or shop name)

        Returns:
            Distance between locations in miles

        Raises:
            KeyError: If distance between locations is not defined
        """
        try:
            return (
                self.distances[(loc1, loc2)]
                if (loc1, loc2) in self.distances
                else self.distances[(loc2, loc1)]
            )
        except KeyError:
            raise KeyError(f"No distance defined between {loc1} and {loc2}")

    def getTotalDistanceOnRoute(self, route: Route) -> float:
        """Calculate total distance for a route including return home.

        Args:
            route: List of shop names in order of visit

        Returns:
            Total distance in miles
        """
        if not route:
            return 0.0

        total = self.getDistance('home', route[0])
        
        # Add distances between consecutive shops
        total += sum(
            self.getDistance(route[i], route[i + 1])
            for i in range(len(route) - 1)
        )
        
        # Add return trip
        total += self.getDistance(route[-1], 'home')
        
        return total

    def getPriceOfOrderOnRoute(
        self, 
        orderList: List[OrderItem], 
        route: Route, 
        gasCost: Union[float, Decimal]
    ) -> Optional[float]:
        """Calculate total cost of order including travel costs.

        Args:
            orderList: List of (fruit, numPounds) tuples
            route: List of shop names in order of visit
            gasCost: Cost per mile of travel

        Returns:
            Total cost including gas, or None if any fruit unavailable
        """
        # Calculate travel cost
        total_cost = self.getTotalDistanceOnRoute(route) * float(gasCost)
        
        # Add fruit costs
        for fruit, numPounds in orderList:
            if (cost_per_pound := self.getFruitCostPerPoundOnRoute(fruit, route)) is None:
                return None
            total_cost += numPounds * cost_per_pound
            
        return total_cost

    def getShops(self) -> List[shop.FruitShop]:
        """Get list of all shops in town."""
        return self.shops
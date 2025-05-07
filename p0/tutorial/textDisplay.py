"""Text-based display for Pacman game.

This module provides simple text-based visualization for the Pacman game,
with options for controlling display speed and verbosity.

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
    - Added proper error handling
    - Added configuration class
"""

from dataclasses import dataclass
from typing import List, Optional, Any
import time
from abc import ABC, abstractmethod

try:
    import pacman
except ImportError:
    pass


@dataclass
class DisplayConfig:
    """Configuration for display settings."""
    draw_every: int = 1
    sleep_time: float = 0.0
    display_moves: bool = False
    quiet: bool = False


class GameDisplay(ABC):
    """Abstract base class for game displays."""
    
    @abstractmethod
    def initialize(self, state: Any, isBlue: bool = False) -> None:
        """Initialize the display with game state."""
        pass
    
    @abstractmethod
    def update(self, state: Any) -> None:
        """Update display with new state."""
        pass
    
    @abstractmethod
    def draw(self, state: Any) -> None:
        """Draw the current state."""
        pass
    
    @abstractmethod
    def pause(self) -> None:
        """Pause the display."""
        pass
    
    @abstractmethod
    def finish(self) -> None:
        """Clean up when game is finished."""
        pass


class NullGraphics(GameDisplay):
    """Minimal display that does nothing except sleep."""
    
    def __init__(self, config: Optional[DisplayConfig] = None) -> None:
        """Initialize with optional config."""
        self.config = config or DisplayConfig()

    def initialize(self, state: Any, isBlue: bool = False) -> None:
        """Do nothing for initialization."""
        pass

    def update(self, state: Any) -> None:
        """Do nothing for updates."""
        pass

    def checkNullDisplay(self) -> bool:
        """Confirm this is a null display."""
        return True

    def pause(self) -> None:
        """Pause for configured time."""
        time.sleep(self.config.sleep_time)

    def draw(self, state: Any) -> None:
        """Print state if not quiet."""
        if not self.config.quiet:
            print(state)

    def updateDistributions(self, dist: Any) -> None:
        """Do nothing for distribution updates."""
        pass

    def finish(self) -> None:
        """Do nothing on finish."""
        pass


class PacmanGraphics(GameDisplay):
    """Text-based display for Pacman game."""
    
    def __init__(self, speed: Optional[float] = None) -> None:
        """Initialize with optional speed setting.
        
        Args:
            speed: Sleep time between frames (None uses default)
        """
        self.config = DisplayConfig()
        if speed is not None:
            self.config.sleep_time = speed
        self.turn: int = 0
        self.agentCounter: int = 0

    def initialize(self, state: Any, isBlue: bool = False) -> None:
        """Initialize display with game state.
        
        Args:
            state: Initial game state
            isBlue: Whether Pacman is blue
        """
        self.draw(state)
        self.pause()
        self.turn = 0
        self.agentCounter = 0

    def update(self, state: Any) -> None:
        """Update display with new state.
        
        Args:
            state: Current game state
        """
        numAgents = len(state.agentStates)
        self.agentCounter = (self.agentCounter + 1) % numAgents
        
        if self.agentCounter == 0:
            self.turn += 1
            if self.config.display_moves:
                self._display_move_info(state, numAgents)
            if self.turn % self.config.draw_every == 0:
                self.draw(state)
                self.pause()
                
        if state._win or state._lose:
            self.draw(state)

    def _display_move_info(self, state: Any, numAgents: int) -> None:
        """Display information about the current move.
        
        Args:
            state: Current game state
            numAgents: Number of agents in game
        """
        ghosts = [
            pacman.nearestPoint(state.getGhostPosition(i))
            for i in range(1, numAgents)
        ]
        pacman_pos = pacman.nearestPoint(state.getPacmanPosition())
        
        print(
            f"{self.turn:4d}) P: {str(pacman_pos):<8} "
            f"| Score: {state.score:<5d} "
            f"| Ghosts: {ghosts}"
        )

    def pause(self) -> None:
        """Pause for configured time."""
        time.sleep(self.config.sleep_time)

    def draw(self, state: Any) -> None:
        """Draw current state if not quiet.
        
        Args:
            state: Current game state
        """
        if not self.config.quiet:
            print(state)

    def finish(self) -> None:
        """Clean up when game is finished."""
        pass
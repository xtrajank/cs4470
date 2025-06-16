"""multiAgents.py - Multi-Agent Search Algorithms for Pacman
===========================================================

This module implements various multi-agent search algorithms for the Pacman game,
including reflex agents, minimax, alpha-beta pruning, and expectimax search.

The module provides agent classes that:
- Make decisions based on state evaluation functions
- Implement adversarial search algorithms
- Model both deterministic and probabilistic opponent behavior
- Search to configurable depths using evaluation heuristics

Key Classes:
    ReflexAgent: Makes decisions using state evaluation heuristics
    MinimaxAgent: Implements minimax search algorithm
    AlphaBetaAgent: Implements alpha-beta pruning search
    ExpectimaxAgent: Implements expectimax probabilistic search

Usage:
    This module is used by the Pacman game to create AI agents. Agents can be
    selected and configured via command line arguments.

Author: George Rudolph
Date: 14 Nov 2024
Major Changes:
1. Added type hints throughout the codebase for better code clarity and IDE support
2. Improved docstrings with detailed descriptions and Args/Returns sections
3. Enhanced code organization with better function and variable naming

This code runs on Python 3.13

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

import random, math
import util
from util import manhattanDistance
from game import Agent, Directions
from typing import List, Tuple, Any
from pacman import GameState

class ReflexAgent(Agent):
    """A reflex agent that chooses actions by examining alternatives via a state evaluation function.
    
    This agent evaluates each possible action using a heuristic evaluation function and selects
    among the best options. The evaluation considers factors like:
    - Distance to ghosts (avoiding them)
    - Score improvements
    - Distance to food
    - Maintaining movement direction
    """

    def getAction(self, gameState: GameState) -> str:
        """Choose among the best actions according to the evaluation function.
        
        Args:
            gameState: The current game state
            
        Returns:
            str: A direction from Directions.{North, South, West, East, Stop}
            
        The method collects legal moves, scores them using the evaluation function,
        and randomly selects among those with the best score.
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)  # Pick randomly among the best

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState: GameState, action: str) -> float:
        """Evaluate the desirability of a game state after taking an action.
        
        Args:
            currentGameState: The current game state
            action: The proposed action
            
        Returns:
            float: A score where higher numbers are better, using values 8,4,2,1,0
            that are bitwise orthogonal (powers of 2)
            
        The function evaluates states based on:
        - Avoiding ghosts (returns 0 if too close)
        - Score improvements (returns 8)
        - Getting closer to food (returns 4) 
        - Maintaining direction (returns 2)
        - Default case (returns 1)
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        # use scores to help evaluate next move
        # score
        score = successorGameState.getScore()

        # food
        foodList = newFood.asList()
        foodDistances = [manhattanDistance(newPos, food) for food in foodList]
        minFoodDist = min(foodDistances) if foodDistances else 1
        foodScore = 1.0/minFoodDist # reciprocal

        # ghost
        ghostScore = 0
        for i, ghost in enumerate(newGhostStates):
            ghostPos = ghost.getPosition()
            dist = manhattanDistance(newPos, ghostPos)
            if newScaredTimes[i] == 0:
                # run away if ghost is within 1
                if dist <= 1:
                    return -float('inf')
                ghostScore -= 1.0/dist # avoid
            else:
                ghostScore += 1.0 / (dist + 1) # chase ghost if scared

        # dont stop
        stopPenalty = -3 if action == 'Stop' else 0

        # combine to get best move
        return score + foodScore + ghostScore + stopPenalty


def scoreEvaluationFunction(currentGameState: GameState) -> float:
    """Return the score of the state for use with adversarial search agents.
    
    Args:
        currentGameState: The game state to evaluate
        
    Returns:
        float: The score displayed in the Pacman GUI
        
    This is the default evaluation function for adversarial search agents.
    Not intended for use with reflex agents.
    """
    return currentGameState.getScore()


class MultiAgentSearchAgent(Agent):
    """Base class for adversarial search agents (minimax, alpha-beta, expectimax).
    
    This abstract class provides common functionality for multi-agent searchers.
    It should not be instantiated directly, but rather extended by concrete
    agent implementations.
    
    Attributes:
        index: Agent index (0 for Pacman)
        evaluationFunction: Function used to evaluate game states
        depth: Maximum depth of search tree
    """

    def __init__(self, evalFn: str = 'scoreEvaluationFunction', depth: str = '2') -> None:
        self.index = 0  # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
    """Minimax agent that implements adversarial search.
    
    This agent uses minimax search to determine the optimal action by considering
    the worst case scenario at each level.
    """

    def getAction(self, gameState: GameState) -> str:
        """Return the minimax action from the current gameState.
        
        Args:
            gameState: The current game state
            
        Returns:
            str: The optimal action according to minimax search
            
        Uses self.depth and self.evaluationFunction to determine the best action
        by considering the worst-case scenario at each level.
        """

        "*** YOUR CODE HERE ***"
        # recursive function
        def minimax(agentIndex, depth, gameState):
            # end if -> reached depth or end of game
            if gameState.isWin() or gameState.isLose() or depth == self.depth:
                return self.evaluationFunction(gameState)
            
            numAgents = gameState.getNumAgents()

            # pacman: max
            if agentIndex == 0:
                maxValue = -float('inf')
                for action in gameState.getLegalActions(agentIndex):
                    successor = gameState.generateSuccessor(agentIndex, action)
                    value = minimax(agentIndex + 1, depth, successor)
                    maxValue = max(maxValue, value)
                return maxValue
            
            # ghosts: min
            else:
                minValue = float('inf')
                for action in gameState.getLegalActions(agentIndex):
                    successor = gameState.generateSuccessor(agentIndex, action)
    
                    # get next agent index and increase depth
                    nextAgent = agentIndex + 1
                    # pacmans turn
                    if nextAgent == numAgents:
                        nextAgent = 0
                        nextDepth = depth + 1
                    else:
                        nextDepth = depth

                    value = minimax(nextAgent, nextDepth, successor)
                    minValue = min(minValue, value)
                return minValue
            
        # getAction
        bestScore = -float('inf')
        bestAction = None
        for action in gameState.getLegalActions(0):
            successor = gameState.generateSuccessor(0, action)
            value = minimax(1, 0, successor)
            if value > bestScore:
                bestScore = value
                bestAction = action
        
        return bestAction


class AlphaBetaAgent(MultiAgentSearchAgent):
    """Minimax agent with alpha-beta pruning optimization.
    
    This agent implements minimax search with alpha-beta pruning to more efficiently
    explore the game tree by pruning branches that cannot affect the final decision.
    """

    def getAction(self, gameState: GameState) -> str:
        """Return the minimax action using alpha-beta pruning.
        
        Args:
            gameState: The current game state
            
        Returns:
            str: The optimal action according to alpha-beta pruning
            
        Pacman is always the max agent, ghosts are always min agents.
        At depth 0, max_value returns an action. At other depths, it returns a value.
        """

        "*** YOUR CODE HERE ***"
        def alphabeta(agentIndex, depth, gameState, alpha, beta):
            # end if game over or reached depth
            if gameState.isWin() or gameState.isLose() or depth == self.depth:
                return self.evaluationFunction(gameState)
            
            numAgents = gameState.getNumAgents()
            nextAgent = (agentIndex + 1) % numAgents
            nextDepth = depth + 1 if nextAgent == 0 else depth
            
            if agentIndex == 0:        
                # pacman
                v = -float('inf')
                for action in gameState.getLegalActions(agentIndex):
                    successor = gameState.generateSuccessor(agentIndex, action)
                    v = max(v, alphabeta(nextAgent, nextDepth, successor, alpha, beta))
                    # prune
                    if v > beta:
                        return v
                    alpha = max(alpha, v)
                return v
            else:
                # ghosts
                v = float('inf')
                for action in gameState.getLegalActions(agentIndex):
                    successor = gameState.generateSuccessor(agentIndex, action)
                    v = min(v, alphabeta(nextAgent, nextDepth, successor, alpha, beta))
                    # prune
                    if v < alpha:
                        return v
                    beta = min(beta, v)
                return v
            
        # initial call from pacman
        bestValue = -float('inf')
        alpha = -float('inf')
        beta = float('inf')
        bestAction = None

        for action in gameState.getLegalActions(0):
            successor = gameState.generateSuccessor(0, action)
            value = alphabeta(1, 0, successor, alpha, beta)
            if value > bestValue:
                bestValue = value
                bestAction = action
            alpha = max(alpha, bestValue)
        
        return bestAction


class ExpectimaxAgent(MultiAgentSearchAgent):
    """An agent that uses expectimax search to make decisions.
    
    This agent models ghosts as choosing uniformly at random from their legal moves.
    It uses expectimax search to find optimal actions against probabilistic opponents.
    
    The agent searches to a fixed depth using a supplied evaluation function.
    """

    def getAction(self, gameState: GameState) -> str:
        """Return the expectimax action using self.depth and self.evaluationFunction.
        
        Args:
            gameState: The current game state
            
        Returns:
            str: The selected action (one of Directions.{North,South,East,West,Stop})
            
        All ghosts are modeled as choosing uniformly at random from their legal moves.
        """
        
        "*** YOUR CODE HERE ***"
        def expectimax(agentIndex, depth, gameState):
            if gameState.isWin() or gameState.isLose() or depth == self.depth:
                return self.evaluationFunction(gameState)
            
            numAgents = gameState.getNumAgents()
            nextAgent = (agentIndex + 1) % numAgents
            nextDepth = depth + 1 if nextAgent == 0 else depth

            # pacman
            if agentIndex == 0:
                best = -float('inf')
                for action in gameState.getLegalActions(agentIndex):
                    successor = gameState.generateSuccessor(agentIndex, action)
                    value = expectimax(nextAgent, nextDepth, successor)
                    best = max(best, value)
                return best
            
            # ghost
            else:
                actions = gameState.getLegalActions(agentIndex)
                if not actions:
                    return self.evaluationFunction(gameState)
                
                total = 0
                for action in actions:
                    successor = gameState.generateSuccessor(agentIndex, action)
                    total += expectimax(nextAgent, nextDepth, successor)
                return total / len(actions)
            
        # intial call
        bestScore = -float('inf')
        bestAction = None
        for action in gameState.getLegalActions(0):
            successor = gameState.generateSuccessor(0, action)
            value = expectimax(1, 0, successor)
            if value > bestScore:
                bestScore = value
                bestAction = action
        
        return bestAction


def betterEvaluationFunction(game_state: GameState) -> float:
    """A more sophisticated evaluation function for Pacman game states.
    
    This function evaluates states by combining the game score with a penalty
    based on distance to the closest food pellet. The penalty uses the reciprocal
    of the distance to give higher penalties to food that is farther away.
    
    Args:
        game_state: The game state to evaluate
        
    Returns:
        float: The evaluation score where higher values are better
    """
    
    "*** YOUR CODE HERE ***"
    from util import manhattanDistance

def betterEvaluationFunction(currentGameState: GameState) -> float:
    # define state
    pacmanPos = currentGameState.getPacmanPosition()
    food = currentGameState.getFood().asList()
    capsules = currentGameState.getCapsules()
    ghostStates = currentGameState.getGhostStates()
    scaredTimers = [ghost.scaredTimer for ghost in ghostStates]

    # score
    score = currentGameState.getScore()

    # food distance
    if food:
        foodDistances = [manhattanDistance(pacmanPos, f) for f in food]
        minFoodDist = min(foodDistances)
        foodBonus = 10.0 / minFoodDist
    else:
        foodBonus = 100

    # ghost distance
    ghostPenalty = 0
    scaredGhostBonus = 0

    for i, ghost in enumerate(ghostStates):
        dist = manhattanDistance(pacmanPos, ghost.getPosition())
        if scaredTimers[i] > 0:
            # reward getting close to scared ghosts
            if dist > 0:
                scaredGhostBonus += 20.0 / dist
        else:
            # discourage being close
            if dist < 2:
                ghostPenalty += 200

    # penalize for capsules left
    capsulePenalty = 5 * len(capsules)

    # penalize if there is food left
    foodLeftPenalty = 4 * len(food)

    # combine
    return score + foodBonus + scaredGhostBonus - ghostPenalty - capsulePenalty - foodLeftPenalty

    
# Abbreviation
better = betterEvaluationFunction


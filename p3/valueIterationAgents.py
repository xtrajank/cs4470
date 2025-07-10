"""
Value Iteration Agent Implementation for Markov Decision Processes

# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).



This module implements a value iteration agent that can solve Markov Decision 
Processes (MDPs) using the value iteration algorithm. The agent iteratively
computes optimal state values and policies using the Bellman equation.

Key Features:
- Batch value updates using Bellman equation
- Configurable discount factor and iteration count
- Support for arbitrary MDPs conforming to the mdp.MarkovDecisionProcess interface

Python Version: 3.13
Last Modified: 23 Nov 2024
Modified by: George Rudolph

Changes:
- Added comprehensive module docstring
- Verified Python 3.13 compatibility
- Improved code documentation and type hints
"""

import math
import heapq
import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
    A ValueIterationAgent takes a Markov decision process (see mdp.py) on initialization 
    and runs value iteration for a given number of iterations using the supplied discount factor.
    
    The agent implements value iteration using the Bellman equation to iteratively compute
    optimal values for each state in the MDP.
    """
    def __init__(self, mdp: 'mdp.MarkovDecisionProcess', discount: float = 0.9, iterations: int = 100) -> None:
        """
        Initialize the value iteration agent.

        Args:
            mdp: The Markov Decision Process to solve
            discount: Discount factor gamma for future rewards (default: 0.9)
            iterations: Number of value iteration steps to perform (default: 100)

        Key MDP methods used:
            mdp.getStates(): Returns list of all states
            mdp.getPossibleActions(state): Returns legal actions for state
            mdp.getTransitionStatesAndProbs(state, action): Returns [(nextState, prob), ...]
            mdp.getReward(state, action, nextState): Returns reward for transition
            mdp.isTerminal(state): Returns True if state is terminal
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self) -> None:
        """
        Implements the Bellman Update Equation (AIMA 4 17.10) using batch updates.
        Updates all state values at time k+1 using time k values rather than
        updating values one at a time using newly computed values.
        """
        # Write value iteration code here
        for _ in range(self.iterations):
            new_values = self.values.copy()

            for state in self.mdp.getStates():
                if self.mdp.isTerminal(state):
                    continue

                # get best value from possible actions
                action_values = []
                for action in self.mdp.getPossibleActions(state):
                    q_value = self.computeQValueFromValues(state, action)
                    action_values.append(q_value)

                    if action_values:
                        new_values[state] = max(action_values)

            self.values = new_values

    def getValue(self, state) -> float:
        """
        Return the computed value for the given state.

        Args:
            state: The state to get the value for

        Returns:
            The value V(s) for the given state
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action) -> float:
        """
        Compute the Q-value Q(s,a) for the given state-action pair using
        the current value function V(s).

        Args:
            state: The state to compute Q-value for
            action: The action to compute Q-value for

        Returns:
            The Q-value for the state-action pair
        """
        "*** YOUR CODE HERE ***"
        q_value = 0
        for next_state, prob in self.mdp.getTransitionStatesAndProbs(state, action):
            reward = self.mdp.getReward(state, action, next_state)
            q_value += prob * (reward + self.discount * self.values[next_state])
        return q_value

    def computeActionFromValues(self, state):
        """
        Compute the optimal action to take in a state based on the stored value function.
        
        Args:
            state: The state to compute the optimal action for

        Returns:
            The optimal action, or None if state is terminal or has no legal actions
        """
        "*** YOUR CODE HERE ***"
        if self.mdp.isTerminal(state):
            return None
        
        best_action = None
        max_q_value = float('-inf')

        for action in self.mdp.getPossibleActions(state):
            q_value = self.computeQValueFromValues(state, action)
            if q_value > max_q_value:
                max_q_value = q_value
                best_action = action
        
        return best_action

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
    An AsynchronousValueIterationAgent performs cyclic value iteration, updating one state
    at a time rather than batch updating all states.
    
    The agent cycles through states in order, updating each state's value using the current
    values of other states.
    """
    def __init__(self, mdp: 'mdp.MarkovDecisionProcess', discount: float = 0.9, iterations: int = 1000) -> None:
        """
        Initialize the asynchronous value iteration agent.

        Args:
            mdp: The Markov Decision Process to solve
            discount: Discount factor gamma for future rewards (default: 0.9) 
            iterations: Number of value updates to perform (default: 1000)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self) -> None:
        """
        Performs asynchronous value iteration by cycling through states and
        updating one state value at a time.
        """
        states = self.mdp.getStates()
        num_states = len(states)

        for i in range(self.iterations):
            state = states[i % num_states] 

            if self.mdp.isTerminal(state):
                continue

            best_q = float('-inf')
            for action in self.mdp.getPossibleActions(state):
                q_value = self.computeQValueFromValues(state, action)
                best_q = max(best_q, q_value)

            self.values[state] = best_q



class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
    A PrioritizedSweepingValueIterationAgent implements prioritized sweeping value iteration.

        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    
    This approach updates states in order of the magnitude of their Bellman error, focusing computation on states where values are changing significantly.
    """
    def __init__(self, mdp: 'mdp.MarkovDecisionProcess', discount: float = 0.9, iterations: int = 100, theta: float = 1e-5) -> None:
        """
        Initialize prioritized sweeping value iteration agent.

        Args:
            mdp: The Markov Decision Process to solve
            discount: Discount factor gamma for future rewards (default: 0.9)
            iterations: Maximum number of updates to perform (default: 100)
            theta: Minimum threshold for Bellman error to trigger update (default: 1e-5)
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self) -> None:
        """
        Implements prioritized sweeping value iteration as described in the project.
        Updates states in order of largest Bellman error, maintaining a priority queue
        of states to update.
        """
        states = self.mdp.getStates()
        predecessors = dict()

        for state in states:
            predecessors[state] = set()

        for state in states:
            if self.mdp.isTerminal(state):
                continue

            for action in self.mdp.getPossibleActions(state):
                for next_state, prob in self.mdp.getTransitionStatesAndProbs(state, action):
                    if prob > 0:
                        predecessors[next_state].add(state)

        pq = util.PriorityQueue()

        for state in states:
            if self.mdp.isTerminal(state):
                continue

            current_value = self.values[state]
            best_q_value = max([self.computeQValueFromValues(state, a) for a in self.mdp.getPossibleActions(state)], default=0)
            diff = abs(current_value - best_q_value)
            pq.update(state, -diff)

        for _ in range(self.iterations):
            if pq.isEmpty():
                break

            state = pq.pop()

            if not self.mdp.isTerminal(state):
                # Update value using Bellman backup
                best_q_value = max([self.computeQValueFromValues(state, a)
                                    for a in self.mdp.getPossibleActions(state)], default=0)
                self.values[state] = best_q_value

            # Update predecessors
            for p in predecessors[state]:
                if self.mdp.isTerminal(p):
                    continue

                current_value = self.values[p]
                best_q_value = max([self.computeQValueFromValues(p, a)
                                    for a in self.mdp.getPossibleActions(p)], default=0)
                diff = abs(current_value - best_q_value)

                if diff > self.theta:
                    pq.update(p, -diff)
        
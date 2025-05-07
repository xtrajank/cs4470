"""Project configuration parameters.

This module defines the configuration parameters for the tutorial project,
including file paths and project metadata.

Changes:
    2024-03-19: Updated to Python 3.13 standards
    - Added proper docstrings
    - Added type hints
    - Improved documentation
    - Added explicit string literals

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

from typing import Final

# Student code files to be graded
STUDENT_CODE_DEFAULT: Final[str] = (
    'addition.py,'
    'buyLotsOfFruit.py,'
    'shopSmart.py,'
    'shopAroundTown.py'
)

# Test class file
PROJECT_TEST_CLASSES: Final[str] = 'tutorialTestClasses.py'

# Project metadata
PROJECT_NAME: Final[str] = 'Project 0: Tutorial'

# Bonus features
BONUS_PIC: Final[bool] = False
"""Test classes for autograder functionality.

This module provides the base classes for implementing test cases and questions
in the autograder system.

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
    - Improved error handling
    - Updated string formatting
    - Added dataclasses
    - Improved documentation
"""

from typing import List, Dict, Tuple, Any, Optional, Callable
from dataclasses import dataclass, field
import inspect
import sys


class Question:
    """Base class for questions in a project."""

    def raiseNotDefined(self) -> None:
        """Raise error for unimplemented methods."""
        print(f'Method not implemented: {inspect.stack()[1][3]}')
        sys.exit(1)

    def __init__(self, questionDict: Dict[str, Any], display: Any) -> None:
        """Initialize question with dictionary and display object."""
        self.maxPoints = int(questionDict['max_points'])
        self.testCases: List[Tuple[Any, Callable]] = []
        self.display = display

    def getDisplay(self) -> Any:
        """Get display object."""
        return self.display

    def getMaxPoints(self) -> int:
        """Get maximum points possible."""
        return self.maxPoints

    def addTestCase(self, testCase: Any, thunk: Callable) -> None:
        """Add a test case with its grading function."""
        self.testCases.append((testCase, thunk))

    def execute(self, grades: Any) -> None:
        """Execute all test cases."""
        self.raiseNotDefined()


class PassAllTestsQuestion(Question):
    """Question requiring all tests to pass for credit."""

    def execute(self, grades: Any) -> None:
        """Execute all tests, requiring all to pass."""
        testsFailed = False
        grades.assignZeroCredit()
        
        for _, f in self.testCases:
            if not f(grades):
                testsFailed = True
                
        if testsFailed:
            grades.fail("Tests failed.")
        else:
            grades.assignFullCredit()


class ExtraCreditPassAllTestsQuestion(Question):
    """Question with potential extra credit points."""

    def __init__(self, questionDict: Dict[str, Any], display: Any) -> None:
        """Initialize with extra credit points."""
        super().__init__(questionDict, display)
        self.extraPoints = int(questionDict['extra_points'])

    def execute(self, grades: Any) -> None:
        """Execute all tests with extra credit possibility."""
        testsFailed = False
        grades.assignZeroCredit()
        
        for _, f in self.testCases:
            if not f(grades):
                testsFailed = True
                
        if testsFailed:
            grades.fail("Tests failed.")
        else:
            grades.assignFullCredit()
            grades.addPoints(self.extraPoints)


class HackedPartialCreditQuestion(Question):
    """Question with partial credit based on test case points."""

    def execute(self, grades: Any) -> None:
        """Execute tests with partial credit."""
        grades.assignZeroCredit()
        points = 0
        passed = True
        
        for testCase, f in self.testCases:
            testResult = f(grades)
            if "points" in testCase.testDict:
                if testResult:
                    points += float(testCase.testDict["points"])
            else:
                passed = passed and testResult

        # Handle edge case for q3's logic
        if int(points) == self.maxPoints and not passed:
            grades.assignZeroCredit()
        else:
            grades.addPoints(int(points))


class Q6PartialCreditQuestion(Question):
    """Special case partial credit question for Q6."""

    def execute(self, grades: Any) -> None:
        """Execute with Q6-specific grading logic."""
        grades.assignZeroCredit()
        results = [f(grades) for _, f in self.testCases]
        
        if False in results:
            grades.assignZeroCredit()


class PartialCreditQuestion(Question):
    """Standard partial credit question."""

    def execute(self, grades: Any) -> None:
        """Execute with partial credit possibility."""
        grades.assignZeroCredit()
        
        for _, f in self.testCases:
            if not f(grades):
                grades.assignZeroCredit()
                grades.fail("Tests failed.")
                return False
        return True


class NumberPassedQuestion(Question):
    """Question graded by number of passing tests."""

    def execute(self, grades: Any) -> None:
        """Execute and grade based on number of passing tests."""
        grades.addPoints([f(grades) for _, f in self.testCases].count(True))


@dataclass
class TestCase:
    """Base class for test cases."""
    question: Question
    testDict: Dict[str, Any]
    path: str = field(init=False)
    messages: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize after dataclass creation."""
        self.path = self.testDict['path']

    def raiseNotDefined(self) -> None:
        """Raise error for unimplemented methods."""
        print(f'Method not implemented: {inspect.stack()[1][3]}')
        sys.exit(1)

    def getPath(self) -> str:
        """Get test case path."""
        return self.path

    def __str__(self) -> str:
        """Get string representation."""
        return f"Test Case: {self.path}"

    def execute(self, grades: Any, moduleDict: Dict, solutionDict: Dict) -> None:
        """Execute test case."""
        self.raiseNotDefined()

    def writeSolution(self, moduleDict: Dict, filePath: str) -> bool:
        """Write solution to file."""
        return True

    def testPass(self, grades: Any) -> bool:
        """Record a passing test."""
        grades.addMessage(f'PASS: {self.path}')
        for line in self.messages:
            grades.addMessage(f'    {line}')
        return True

    def testFail(self, grades: Any) -> bool:
        """Record a failing test."""
        grades.addMessage(f'FAIL: {self.path}')
        for line in self.messages:
            grades.addMessage(f'    {line}')
        return False

    def testPartial(self, grades: Any, points: float, maxPoints: float) -> bool:
        """Record a partially passing test."""
        grades.addPoints(points)
        extraCredit = max(0, points - maxPoints)
        regularCredit = points - extraCredit

        grades.addMessage(
            f'{"PASS" if points >= maxPoints else "FAIL"}: '
            f'{self.path} ({regularCredit} of {maxPoints} points)'
        )
        
        if extraCredit > 0:
            grades.addMessage(f'EXTRA CREDIT: {extraCredit} points')

        for line in self.messages:
            grades.addMessage(f'    {line}')

        return True

    def addMessage(self, message: str) -> None:
        """Add a message to the test case."""
        self.messages.extend(message.split('\n'))
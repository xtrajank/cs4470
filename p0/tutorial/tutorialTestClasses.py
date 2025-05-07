"""Tutorial test classes for autograder functionality.

This module provides specialized test cases for the tutorial assignments,
particularly the EvalTest class which evaluates Python code against solutions.

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

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import testClasses
from testClasses import TestCase, Question


@dataclass
class EvalTest(TestCase):
    """Test case that evaluates Python code and compares the output to a solution."""
    
    question: Question
    testDict: Dict[str, Any]
    
    def __post_init__(self):
        """Initialize test case attributes from testDict."""
        self.preamble = self.testDict.get('preamble', '')
        self.test = self.testDict.get('test', '')
        self.success = self.testDict.get('success', '')
        self.failure = self.testDict.get('failure', '')

    def evalCode(self, moduleDict: Dict[str, Any]) -> str:
        """
        Evaluate test code using the provided module bindings.
        
        Args:
            moduleDict: Dictionary of module bindings
            
        Returns:
            Result of evaluating the test code
            
        Raises:
            Exception: If evaluation fails
        """
        bindings = dict(moduleDict)
        
        # Execute preamble if it exists
        if self.preamble:
            try:
                exec(self.preamble, bindings)
            except Exception as e:
                raise Exception(f"Error in preamble: {str(e)}")
                
        # Execute test code
        try:
            return str(eval(self.test, bindings))
        except Exception as e:
            raise Exception(f"Error evaluating test: {str(e)}")

    def execute(self, grades: Any, moduleDict: Dict[str, Any], solutionDict: Dict[str, Any]) -> bool:
        """
        Execute the test case and grade the result.
        
        Args:
            grades: Grading object
            moduleDict: Dictionary of module bindings
            solutionDict: Dictionary of solution bindings
            
        Returns:
            True if test passes, False otherwise
        """
        result = self.evalCode(moduleDict)
        solution = solutionDict.get('result', '')
        
        if result == solution:
            grades.addMessage('PASS: %s' % self.success)
            grades.addMessage('\t correct result: "%s"' % solution)
            return True
        else:
            grades.addMessage('FAIL: %s' % self.failure)
            grades.addMessage('\t student result: "%s"' % result)
            grades.addMessage('\t correct result: "%s"' % solution)
            return False

    def writeSolution(self, moduleDict: Dict[str, Any], filePath: str) -> bool:
        """
        Write solution for the test to a file.
        
        Args:
            moduleDict: Dictionary of module bindings
            filePath: Path to write solution file
            
        Returns:
            True if solution was written successfully
            
        Raises:
            IOError: If file cannot be written
        """
        path = Path(filePath)
        
        try:
            with path.open('w', encoding='utf-8') as handle:
                handle.write(
                    f'# This is the solution file for {self.path}.\n'
                    '# The result of evaluating the test must equal '
                    'the below when cast to a string.\n'
                    f'result: "{self.evalCode(moduleDict)}"\n'
                )
            return True
            
        except IOError as e:
            raise IOError(f"Error writing solution file: {str(e)}")


class TestCase(testClasses.TestCase):
    """Base test case class that provides common functionality."""
    
    def __init__(self, question: Question, testDict: Dict[str, Any]):
        """
        Initialize the test case.
        
        Args:
            question: Question object this test belongs to
            testDict: Dictionary containing test data
        """
        super().__init__(question, testDict)
        self.maxPoints = int(testDict.get('maxPoints', 0))
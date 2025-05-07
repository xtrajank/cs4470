"""Common code for autograders.

This module provides grading functionality for student project submissions.

Changes:
    2024-03-19: Updated to Python 3.13 standards
    - Added type hints
    - Modernized imports and string formatting
    - Improved error handling
    - Updated file operations to use pathlib
    - Added proper documentation

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

from typing import Dict, List, Set, Tuple, Any, Optional, Union
from pathlib import Path
import time
import sys
import json
import traceback
from collections import defaultdict
import util
from html import escape


class Grades:
    """A data structure for project grades, along with formatting code to display them."""

    def __init__(
        self,
        projectName: str,
        questionsAndMaxesList: List[Tuple[str, int]],
        gsOutput: bool = False,
        edxOutput: bool = False,
        muteOutput: bool = False,
    ) -> None:
        """Initialize the grading system.

        Args:
            projectName: Name of the project
            questionsAndMaxesList: List of (question name, max points) tuples
            gsOutput: Whether to generate GradeScope output
            edxOutput: Whether to generate edX output
            muteOutput: Whether to mute output
        """
        self.questions = [el[0] for el in questionsAndMaxesList]
        self.maxes = dict(questionsAndMaxesList)
        self.points = Counter()
        self.messages = {q: [] for q in self.questions}
        self.project = projectName
        self.start = time.localtime()[1:6]
        self.sane = True  # Sanity checks
        self.currentQuestion: Optional[str] = None
        self.edxOutput = edxOutput
        self.gsOutput = gsOutput
        self.mute = muteOutput
        self.prereqs: Dict[str, Set[str]] = defaultdict(set)

        print(f'Starting on {self.start[0]}-{self.start[1]} at {self.start[2]:02d}:{self.start[3]:02d}:{self.start[4]:02d}')

    def addPrereq(self, question: str, prereq: str) -> None:
        """Add a prerequisite question.

        Args:
            question: Question that has the prerequisite
            prereq: Prerequisite question
        """
        self.prereqs[question].add(prereq)

    def grade(
        self,
        gradingModule: Any,
        exceptionMap: Dict[str, Any] = {},
        bonusPic: bool = False
    ) -> None:
        """Grade each question.

        Args:
            gradingModule: Module with grading functions
            exceptionMap: Map of exceptions to hints
            bonusPic: Whether to show bonus picture
        """
        completedQuestions: Set[str] = set()
        
        for q in self.questions:
            print(f'\nQuestion {q}')
            print('=' * (9 + len(q)))
            print()
            self.currentQuestion = q

            incompleted = self.prereqs[q].difference(completedQuestions)
            if incompleted:
                prereq = incompleted.pop()
                print(
                    f"*** NOTE: Make sure to complete Question {prereq} before working on Question {q},\n"
                    f"*** because Question {q} builds upon your answer for Question {prereq}."
                )
                continue

            if self.mute:
                util.mutePrint()
            
            try:
                # Call the question's function with timeout
                util.TimeoutFunction(getattr(gradingModule, q), 1800)(self)
            except Exception as inst:
                self.addExceptionMessage(q, inst, traceback)
                self.addErrorHints(exceptionMap, inst, q[1])
            except:
                self.fail('FAIL: Terminated with a string exception.')
            finally:
                if self.mute:
                    util.unmutePrint()

            if self.points[q] >= self.maxes[q]:
                completedQuestions.add(q)

            print(f'\n### Question {q}: {self.points[q]}/{self.maxes[q]} ###\n')

        print(f'\nFinished at {time.localtime()[3]:02d}:{time.localtime()[4]:02d}:{time.localtime()[5]:02d}')
        print("\nProvisional grades\n==================")

        for q in self.questions:
            print(f'Question {q}: {self.points[q]}/{self.maxes[q]}')
        
        print('------------------')
        total_points = self.points.totalCount()
        total_possible = sum(self.maxes.values())
        print(f'Total: {total_points}/{total_possible}')

        if bonusPic and total_points == 25:
            self._print_bonus_pic()

        print(
            "\nYour grades are NOT yet registered. To register your grades, make sure\n"
            "to follow your instructor's guidelines to receive credit on your project.\n"
        )

        if self.edxOutput:
            self.produceOutput()
        if self.gsOutput:
            self.produceGradeScopeOutput()

    def addExceptionMessage(self, q: str, inst: Exception, tb: Any) -> None:
        """Format the exception message.

        Args:
            q: Question name
            inst: Exception instance
            tb: Traceback object
        """
        self.fail(f'FAIL: Exception raised: {inst}')
        self.addMessage('')
        for line in tb.format_exc().split('\n'):
            self.addMessage(line)

    def addErrorHints(
        self,
        exceptionMap: Dict[str, Any],
        errorInstance: Exception,
        questionNum: str
    ) -> None:
        """Add error hints based on the exception type.

        Args:
            exceptionMap: Map of exceptions to hints
            errorInstance: The exception instance
            questionNum: Question number
        """
        typeOf = str(type(errorInstance))
        questionName = f'q{questionNum}'
        errorHint = ''

        # Question specific error hints
        if questionMap := exceptionMap.get(questionName):
            if typeHint := questionMap.get(typeOf):
                errorHint = typeHint
        # Fall back to general error messages
        elif typeHint := exceptionMap.get(typeOf):
            errorHint = typeHint

        if errorHint:
            for line in errorHint.split('\n'):
                self.addMessage(line)

    def produceGradeScopeOutput(self) -> None:
        """Generate GradeScope output file."""
        total_score = sum(self.points.values())
        total_possible = sum(self.maxes.values())
        
        out_dct = {
            'score': total_score,
            'max_score': total_possible,
            'output': f"Total score ({total_score} / {total_possible})",
            'tests': [
                {
                    'name': name,
                    'score': self.points[name],
                    'max_score': self.maxes[name],
                    'output': (f"  Question {name[1] if len(name) == 2 else name} "
                              f"({self.points[name]}/{self.maxes[name]}) "
                              f"{'X' if self.points[name] < self.maxes[name] else ''}"),
                    'tags': []
                }
                for name in self.questions
            ]
        }

        Path('gradescope_response.json').write_text(json.dumps(out_dct))
    def produceOutput(self) -> None:
        """Generate edX output files."""
        output_content = self._generate_edx_output()
        Path('edx_response.html').write_text(output_content)
        Path('edx_grade').write_text(str(self.points.totalCount()))

    def fail(self, message: str, raw: bool = False) -> None:
        """Set sanity check bit to false and output a message.

        Args:
            message: Message to display
            raw: Whether the message is raw HTML
        """
        self.sane = False
        self.assignZeroCredit()
        self.addMessage(message, raw)

    def assignZeroCredit(self) -> None:
        """Assign zero credit for current question."""
        if self.currentQuestion is not None:
            self.points[self.currentQuestion] = 0

    def addPoints(self, amt: Union[int, float]) -> None:
        """Add points to current question.

        Args:
            amt: Amount of points to add
        """
        if self.currentQuestion is not None:
            self.points[self.currentQuestion] += amt

    def deductPoints(self, amt: Union[int, float]) -> None:
        """Deduct points from current question.

        Args:
            amt: Amount of points to deduct
        """
        if self.currentQuestion is not None:
            self.points[self.currentQuestion] -= amt

    def assignFullCredit(self, message: str = "", raw: bool = False) -> None:
        """Assign full credit for current question.

        Args:
            message: Optional message to display
            raw: Whether the message is raw HTML
        """
        if self.currentQuestion is not None:
            self.points[self.currentQuestion] = self.maxes[self.currentQuestion]
            if message:
                self.addMessage(message, raw)

    def addMessage(self, message: str, raw: bool = False) -> None:
        """Add a message to the current question.

        Args:
            message: Message to add
            raw: Whether the message is raw HTML
        """
        if not raw:
            if self.mute:
                util.unmutePrint()
            print(f'*** {message}')
            if self.mute:
                util.mutePrint()
            message = escape(message)
        if self.currentQuestion is not None:
            self.messages[self.currentQuestion].append(message)

    def _print_bonus_pic(self) -> None:
        """Print the bonus picture ASCII art."""
        print("""
                     ALL HAIL GRANDPAC.
              LONG LIVE THE GHOSTBUSTING KING.

                  ---      ----      ---
                  |  \    /  + \    /  |
                  | + \--/      \--/ + |
                  |   +     +          |
                  | +     +        +   |
                @@@@@@@@@@@@@@@@@@@@@@@@@@
              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            \   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
             \ /  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
              V   \   @@@@@@@@@@@@@@@@@@@@@@@@@@@@
                   \ /  @@@@@@@@@@@@@@@@@@@@@@@@@@
                    V     @@@@@@@@@@@@@@@@@@@@@@@@
                            @@@@@@@@@@@@@@@@@@@@@@
                    /\      @@@@@@@@@@@@@@@@@@@@@@
                   /  \  @@@@@@@@@@@@@@@@@@@@@@@@@
              /\  /    @@@@@@@@@@@@@@@@@@@@@@@@@@@
             /  \ @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            /    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                @@@@@@@@@@@@@@@@@@@@@@@@@@
                    @@@@@@@@@@@@@@@@@@
        """)


class Counter(dict):
    """Dict with default 0."""

    def __getitem__(self, idx: Any) -> Union[int, float]:
        """Get item with default 0.

        Args:
            idx: Dictionary key

        Returns:
            Value for key or 0 if not found
        """
        try:
            return super().__getitem__(idx)
        except KeyError:
            return 0

    def totalCount(self) -> Union[int, float]:
        """Get sum of all values.

        Returns:
            Sum of all values in the dictionary
        """
        return sum(self.values())
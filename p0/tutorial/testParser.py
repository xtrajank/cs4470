"""Test parser for autograder test files.

This module provides functionality to parse test files and emit test dictionaries.

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
    - Added error handling
    - Improved documentation
    - Added dataclass
    - Added proper file handling
"""

from typing import List, Dict, Tuple, TextIO, Iterator
from dataclasses import dataclass, field
import re
import sys
from pathlib import Path


@dataclass
class TestParser:
    """Parser for test files with special formatting."""
    
    path: Path
    _raw_lines: List[str] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Convert string path to Path object if needed."""
        if isinstance(self.path, str):
            self.path = Path(self.path)

    def removeComments(self, rawlines: List[str]) -> str:
        """Remove comments from lines of text.
        
        Args:
            rawlines: List of strings containing possible comments

        Returns:
            String with all comments removed and lines joined
        """
        return '\n'.join(
            line.split('#')[0] 
            for line in rawlines
        )

    def parse(self) -> Dict[str, any]:
        """Parse the test file into a dictionary.

        Returns:
            Dictionary containing test data with special keys:
            - __raw_lines__: Original file lines
            - path: Path to test file
            - __emit__: List of tuples for reconstruction
            
        Raises:
            FileNotFoundError: If test file doesn't exist
            ValueError: If test file format is invalid
        """
        if not self.path.exists():
            raise FileNotFoundError(f"Test file not found: {self.path}")

        # Initialize test dictionary
        test: Dict[str, any] = {
            'path': str(self.path),
            '__emit__': []
        }

        # Read and parse file
        try:
            with open(self.path, encoding='utf-8') as handle:
                self._raw_lines = handle.read().splitlines()
        except Exception as e:
            raise ValueError(f"Error reading test file: {e}")

        test['__raw_lines__'] = self._raw_lines
        test_text = self.removeComments(self._raw_lines)
        lines = test_text.splitlines()

        i = 0
        while i < len(lines):
            # Skip blank lines
            if re.match(r'\A\s*\Z', lines[i]):
                test['__emit__'].append(("raw", self._raw_lines[i]))
                i += 1
                continue

            # Match single-line property
            if m := re.match(r'\A([^"]*?):\s*"([^"]*)"\s*\Z', lines[i]):
                test[m.group(1)] = m.group(2)
                test['__emit__'].append(("oneline", m.group(1)))
                i += 1
                continue

            # Match multi-line property
            if m := re.match(r'\A([^"]*?):\s*"""\s*\Z', lines[i]):
                msg = []
                i += 1
                while i < len(lines) and not re.match(r'\A\s*"""\s*\Z', lines[i]):
                    msg.append(self._raw_lines[i])
                    i += 1
                if i >= len(lines):
                    raise ValueError(
                        f"Unterminated multiline string in {self.path}"
                    )
                test[m.group(1)] = '\n'.join(msg)
                test['__emit__'].append(("multiline", m.group(1)))
                i += 1
                continue

            raise ValueError(
                f"Invalid format in test file {self.path} at line {i + 1}"
            )

        return test


def emitTestDict(testDict: Dict[str, any], handle: TextIO) -> None:
    """Write test dictionary back to a file.

    Args:
        testDict: Dictionary containing test data
        handle: File handle to write to

    Raises:
        ValueError: If emit format is invalid
    """
    for kind, data in testDict['__emit__']:
        try:
            if kind == "raw":
                handle.write(f"{data}\n")
            elif kind == "oneline":
                handle.write(f'{data}: "{testDict[data]}"\n')
            elif kind == "multiline":
                handle.write(f'{data}: """\n{testDict[data]}\n"""\n')
            else:
                raise ValueError(f"Invalid __emit__ kind: {kind}")
        except Exception as e:
            raise ValueError(f"Error writing test data: {e}")
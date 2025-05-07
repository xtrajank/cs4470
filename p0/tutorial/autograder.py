"""Autograder for student code evaluation.

This module provides functionality to automatically grade student code submissions.
It supports multiple test cases, dependencies between questions, and various output formats.

Changes:
    2024-03-19: Updated to Python 3.13 standards
    - Improved error handling
    - Added type hints
    - Modernized imports
    - Updated string formatting
    - Removed deprecated code
    - Added pathlib for file operations
    - Improved documentation

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

from typing import Dict, List, Optional, Any, Union, Set
from pathlib import Path
import grading
import importlib.util
import argparse
import re
import sys
import projectParams
import random
import pprint
from dataclasses import dataclass

random.seed(0)

try:
    from pacman import GameState
except ImportError:
    pass

# Error Hint Map
ERROR_HINT_MAP = {
    'q1': {
        "<type 'exceptions.IndexError'>": """
        We noticed that your project threw an IndexError on q1.
        While many things may cause this, it may have been from
        assuming a certain number of successors from a state space
        or assuming a certain number of actions available from a given
        state. Try making your code more general (no hardcoded indices)
        and submit again!
        """
    },
    'q3': {
        "<type 'exceptions.AttributeError'>": """
        We noticed that your project threw an AttributeError on q3.
        While many things may cause this, it may have been from assuming
        a certain size or structure to the state space. For example, if you have
        a line of code assuming that the state is (x, y) and we run your code
        on a state space with (x, y, z), this error could be thrown. Try
        making your code more general and submit again!
        """
    }
}

@dataclass
class TestCase:
    """Container for test case information."""
    name: str
    test_dict: Dict[str, Any]
    solution_dict: Dict[str, Any]
    test_out_file: Path

def readCommand(argv: List[str]) -> argparse.Namespace:
    """Parse command line arguments.

    Args:
        argv: List of command line arguments

    Returns:
        Parsed argument namespace
    """
    parser = argparse.ArgumentParser(description='Run public tests on student code')
    
    # Create argument groups
    dir_group = parser.add_argument_group('Directory Options')
    output_group = parser.add_argument_group('Output Options')
    
    # Directory options
    dir_group.add_argument('--test-directory',
                          dest='testRoot',
                          default='test_cases',
                          help='Root test directory containing question subdirectories')
    
    dir_group.add_argument('--student-code',
                          dest='studentCode',
                          default=projectParams.STUDENT_CODE_DEFAULT,
                          help='comma separated list of student code files')
    
    dir_group.add_argument('--code-directory',
                          dest='codeRoot',
                          default="",
                          help='Root directory containing the student and testClass code')
    
    dir_group.add_argument('--test-case-code',
                          dest='testCaseCode',
                          default=projectParams.PROJECT_TEST_CLASSES,
                          help='class containing testClass classes for this project')
    
    # Output options
    output_group.add_argument('--generate-solutions',
                          dest='generateSolutions',
                          action='store_true',
                          default=False,
                          help='Write solutions generated to .solution file')
    
    output_group.add_argument('--edx-output',
                          dest='edxOutput',
                          action='store_true',
                          default=False,
                          help='Generate edX output files')
    
    output_group.add_argument('--gradescope-output',
                          dest='gsOutput',
                          action='store_true',
                          default=False,
                          help='Generate GradeScope output files')
    
    output_group.add_argument('--mute',
                          dest='muteOutput',
                          action='store_true',
                          default=False,
                          help='Mute output from executing tests')
    
    output_group.add_argument('--print-tests', '-p',
                          dest='printTestCase',
                          action='store_true',
                          default=False,
                          help='Print each test case before running them.')
    
    dir_group.add_argument('--no-graphics',
                          dest='noGraphics',
                          action='store_true',
                          default=False,
                          help='No graphics display for pacman games.')
    
    # Optional arguments
    output_group.add_argument('--test', '-t',
                          dest='runTest',
                          default=None,
                          help='Run one particular test. Relative to test root.')
    
    output_group.add_argument('--question', '-q',
                          dest='gradeQuestion',
                          default=None,
                          help='Grade one particular question.')
    
    return parser.parse_args(argv)

def confirmGenerate() -> None:
    """Confirm whether to overwrite solution files."""
    print('WARNING: this action will overwrite any solution files.')
    print('Are you sure you want to proceed? (yes/no)')
    while True:
        ans = sys.stdin.readline().strip()
        if ans == 'yes':
            break
        elif ans == 'no':
            sys.exit(0)
        else:
            print('Please answer either "yes" or "no"')

def loadModuleFile(moduleName: str, filePath: str) -> Any:
    """Load a Python module from a file.

    Args:
        moduleName: Name to give the module
        filePath: Path to the module file

    Returns:
        Loaded module object

    Raises:
        ImportError: If module cannot be loaded
    """
    spec = importlib.util.spec_from_file_location(moduleName, filePath)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module {moduleName} from {filePath}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def readFile(path: Union[str, Path], root: str = "") -> str:
    """Read file from disk at specified path.

    Args:
        path: Path to the file
        root: Optional root directory

    Returns:
        Contents of the file as string
    """
    file_path = Path(root) / path
    return file_path.read_text(encoding='utf-8')

def splitStrings(d: Dict[str, Any]) -> Dict[str, Any]:
    """Split string values in dictionary on newlines.

    Args:
        d: Input dictionary

    Returns:
        Dictionary with string values split into lists
    """
    d2 = dict(d)
    for k in list(d2.keys()):
        if k.startswith("__"):
            del d2[k]
            continue
        if isinstance(d2[k], str) and '\n' in d2[k]:
            d2[k] = d2[k].split('\n')
    return d2

def printTest(testDict: Dict[str, Any], solutionDict: Dict[str, Any]) -> None:
    """Print test case and solution information.

    Args:
        testDict: Test case dictionary
        solutionDict: Solution dictionary
    """
    pp = pprint.PrettyPrinter(indent=4)
    print("Test case:")
    for line in testDict.get("__raw_lines__", []):
        print(f"   | {line}")
    print("Solution:")
    for line in solutionDict.get("__raw_lines__", []):
        print(f"   | {line}")

def getDepends(testParser: Any, testRoot: str, question: str) -> List[str]:
    """Get all dependencies for a question.

    Args:
        testParser: Parser for test files
        testRoot: Root directory for tests
        question: Question to find dependencies for

    Returns:
        List of question dependencies in order
    """
    allDeps = [question]
    config_path = Path(testRoot) / question / 'CONFIG'
    questionDict = testParser.TestParser(str(config_path)).parse()
    
    if 'depends' in questionDict:
        depends = questionDict['depends'].split()
        for d in depends:
            # Run dependencies first
            allDeps = getDepends(testParser, testRoot, d) + allDeps
    return allDeps

def getTestSubdirs(testParser: Any, testRoot: str, 
                   questionToGrade: Optional[str]) -> List[str]:
    """Get list of questions to grade.

    Args:
        testParser: Parser for test files
        testRoot: Root directory for tests
        questionToGrade: Specific question to grade, if any

    Returns:
        List of test subdirectories to process
    """
    config_path = Path(testRoot) / 'CONFIG'
    problemDict = testParser.TestParser(str(config_path)).parse()
    
    if questionToGrade is not None:
        questions = getDepends(testParser, testRoot, questionToGrade)
        if len(questions) > 1:
            print(f'Note: due to dependencies, the following tests will be run: {" ".join(questions)}')
        return questions
    
    if 'order' in problemDict:
        return problemDict['order'].split()
    
    return sorted(d.name for d in Path(testRoot).iterdir() 
                 if d.is_dir() and not d.name.startswith('.'))

def getDisplay(graphicsByDefault: bool, args: Optional[argparse.Namespace] = None) -> Any:
    """Get appropriate display for the game.

    Args:
        graphicsByDefault: Whether to use graphics by default
        args: Command line arguments

    Returns:
        Display object
    """
    graphics = graphicsByDefault
    if args is not None and args.noGraphics:
        graphics = False
    
    if graphics:
        try:
            import graphicsDisplay
            return graphicsDisplay.PacmanGraphics(1, frameTime=.05)
        except ImportError:
            pass
    
    import textDisplay
    return textDisplay.NullGraphics()

def runTest(testName: str, moduleDict: Dict[str, Any], 
           printTestCase: bool = False, display: Optional[Any] = None) -> None:
    """Run a single test case.

    Args:
        testName: Name of the test to run
        moduleDict: Dictionary of loaded modules
        printTestCase: Whether to print test case details
        display: Display object to use
    """
    import testParser
    import testClasses
    for module in moduleDict:
        setattr(sys.modules[__name__], module, moduleDict[module])

    testDict = testParser.TestParser(f"{testName}.test").parse()
    solutionDict = testParser.TestParser(f"{testName}.solution").parse()
    test_out_file = Path(f'{testName}.test_output')
    testDict['test_out_file'] = str(test_out_file)
    testClass = getattr(projectTestClasses, testDict['class'])

    questionClass = getattr(testClasses, 'Question')
    question = questionClass({'max_points': 0}, display)
    testCase = testClass(question, testDict)

    if printTestCase:
        printTest(testDict, solutionDict)

    # This is a fragile hack to create a stub grades object
    grades = grading.Grades(projectParams.PROJECT_NAME, [(None,0)])
    testCase.execute(grades, moduleDict, solutionDict)

def evaluate(generateSolutions: bool, testRoot: str, moduleDict: Dict[str, Any], 
            exceptionMap: Dict[str, Any] = ERROR_HINT_MAP,
            edxOutput: bool = False, muteOutput: bool = False, 
            gsOutput: bool = False, printTestCase: bool = False, 
            questionToGrade: Optional[str] = None, 
            display: Optional[Any] = None) -> float:
    """Evaluate student code.

    Args:
        generateSolutions: Whether to generate solution files
        testRoot: Root directory for tests
        moduleDict: Dictionary of loaded modules
        exceptionMap: Map of exceptions to hints
        edxOutput: Whether to generate edX output
        muteOutput: Whether to mute output
        gsOutput: Whether to generate Gradescope output
        printTestCase: Whether to print test cases
        questionToGrade: Specific question to grade
        display: Display object to use

    Returns:
        Total points earned
    """
    import testParser
    import testClasses
    
    for module in moduleDict:
        setattr(sys.modules[__name__], module, moduleDict[module])

    questions: List[tuple] = []
    questionDicts: Dict[str, Any] = {}
    test_subdirs = getTestSubdirs(testParser, testRoot, questionToGrade)
    
    for q in test_subdirs:
        subdir_path = Path(testRoot) / q
        if not subdir_path.is_dir() or q[0] == '.':
            continue

        # Create a question object
        questionDict = testParser.TestParser(str(subdir_path / 'CONFIG')).parse()
        questionClass = getattr(testClasses, questionDict['class'])
        question = questionClass(questionDict, display)
        questionDicts[q] = questionDict

        # Load test cases into question
        tests = [t for t in subdir_path.iterdir() 
                if t.suffix == '.test' and not t.name.startswith(('.', '#', '~'))]
        tests = sorted(t.stem for t in tests)
        
        for t in tests:
            test_file = subdir_path / f'{t}.test'
            solution_file = subdir_path / f'{t}.solution'
            test_out_file = subdir_path / f'{t}.test_output'
            
            testDict = testParser.TestParser(str(test_file)).parse()
            if testDict.get("disabled", "false").lower() == "true":
                continue
                
            testDict['test_out_file'] = str(test_out_file)
            testClass = getattr(projectTestClasses, testDict['class'])
            testCase = testClass(question, testDict)

            def makefun(testCase: Any, solution_file: Path) -> Any:
                if generateSolutions:
                    return lambda grades: testCase.writeSolution(moduleDict, str(solution_file))
                else:
                    testDict = testParser.TestParser(str(test_file)).parse()
                    solutionDict = testParser.TestParser(str(solution_file)).parse()
                    if printTestCase:
                        return lambda grades: printTest(testDict, solutionDict) or testCase.execute(grades, moduleDict, solutionDict)
                    else:
                        return lambda grades: testCase.execute(grades, moduleDict, solutionDict)
            
            question.addTestCase(testCase, makefun(testCase, solution_file))

        # Note extra function is necessary for scoping reasons
        def makefun(question: Any) -> Any:
            return lambda grades: question.execute(grades)
        
        setattr(sys.modules[__name__], q, makefun(question))
        questions.append((q, question.getMaxPoints()))

    grades = grading.Grades(projectParams.PROJECT_NAME, questions,
                          gsOutput=gsOutput, edxOutput=edxOutput, 
                          muteOutput=muteOutput)
                          
    if questionToGrade is None:
        for q in questionDicts:
            for prereq in questionDicts[q].get('depends', '').split():
                grades.addPrereq(q, prereq)

    grades.grade(sys.modules[__name__], bonusPic=projectParams.BONUS_PIC)
    return grades.points

def main() -> None:
    """Main entry point for the autograder."""
    args = readCommand(sys.argv[1:])
    if args.generateSolutions:
        confirmGenerate()
    
    codePaths = args.studentCode.split(',')
    moduleDict = {}
    
    # Load student code modules
    for cp in codePaths:
        moduleName = re.match(r'.*?([^/]*)\.py', cp).group(1)
        moduleDict[moduleName] = loadModuleFile(
            moduleName, 
            str(Path(args.codeRoot) / cp)
        )
    
    # Load test classes
    moduleName = re.match(r'.*?([^/]*)\.py', args.testCaseCode).group(1)
    moduleDict['projectTestClasses'] = loadModuleFile(
        moduleName, 
        str(Path(args.codeRoot) / args.testCaseCode)
    )

    if args.runTest is not None:
        runTest(
            args.runTest, 
            moduleDict, 
            printTestCase=args.printTestCase, 
            display=getDisplay(True, args)
        )
    else:
        evaluate(
            args.generateSolutions, 
            args.testRoot, 
            moduleDict,
            gsOutput=args.gsOutput, 
            edxOutput=args.edxOutput, 
            muteOutput=args.muteOutput, 
            printTestCase=args.printTestCase, 
            questionToGrade=args.gradeQuestion, 
            display=getDisplay(args.gradeQuestion is not None, args)
        )

if __name__ == '__main__':
    main()
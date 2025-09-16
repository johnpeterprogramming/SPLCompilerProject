"""
SPL (Students' Programming Language) - Shared Types and Constants
COS341 Semester Project 2025

This module contains shared types, enums, and constants used across
all phases of the SPL compiler (lexer, parser, AST, code generation).
"""

from enum import Enum
from typing import NamedTuple, Dict, Set


class TokenType(Enum):
    """Enumeration of all token types in SPL"""
    
    # Keywords - Program Structure
    GLOB = "glob"
    PROC = "proc"
    FUNC = "func"
    MAIN = "main"
    VAR = "var"
    LOCAL = "local"
    RETURN = "return"
    
    # Keywords - Control Flow
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    DO = "do"
    UNTIL = "until"
    
    # Keywords - Operations
    HALT = "halt"
    PRINT = "print"
    
    # Operators - Unary
    NEG = "neg"
    NOT = "not"
    
    # Operators - Binary Comparison
    EQ = "eq"
    GT = ">"
    
    # Operators - Binary Logical
    OR = "or"
    AND = "and"
    
    # Operators - Binary Arithmetic
    PLUS = "plus"
    MINUS = "minus"
    MULT = "mult"
    DIV = "div"
    
    # Delimiters
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    SEMICOLON = ";"
    ASSIGN = "="
    
    # Literals
    NUMBER = "NUMBER"
    STRING = "STRING"
    USER_DEFINED_NAME = "USER_DEFINED_NAME"
    
    # Special
    EOF = "EOF"
    WHITESPACE = "WHITESPACE"
    COMMENT = "COMMENT"


class Token(NamedTuple):
    """Represents a token in the SPL language"""
    type: TokenType
    value: str
    line: int
    column: int
    
    def __str__(self) -> str:
        """String representation for debugging"""
        return f"Token({self.type.name}, {repr(self.value)}, {self.line}:{self.column})"
    
    def __repr__(self) -> str:
        """Detailed representation for debugging"""
        return self.__str__()


class SPLError(Exception):
    """Base class for all SPL compiler errors"""
    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        """Format the error message with location info"""
        if self.line > 0:
            return f"{self.__class__.__name__} at line {self.line}, column {self.column}: {self.message}"
        return f"{self.__class__.__name__}: {self.message}"


class LexerError(SPLError):
    """Exception raised when lexical analysis fails"""
    pass

class ParseError(SPLError):
    """Error raised during parsing (syntax errors)."""
    pass


# Future error types (placeholders for when parser/semantic analysis are implemented)
# class ParseError(SPLError):
#     """Exception raised when parsing fails"""
#     pass

# class SemanticError(SPLError):
#     """Exception raised when semantic analysis fails"""
#     pass

# class CodeGenError(SPLError):
#     """Exception raised during code generation"""
#     pass


# SPL Language Constants and Specifications
class SPLConstants:
    """Constants for SPL language specifications"""
    
    # String constraints
    MAX_STRING_LENGTH = 15
    
    # Parameter constraints
    MAX_PARAMETERS = 3
    
    # Regex patterns for vocabulary rules
    USER_DEFINED_NAME_PATTERN = r'^[a-z][a-z]*[0-9]*$'
    NUMBER_PATTERN = r'^(0|[1-9][0-9]*)$'
    STRING_CONTENT_PATTERN = r'^[a-zA-Z0-9]*$'
    
    # Keywords mapping for lexer
    KEYWORDS: Dict[str, TokenType] = {
        'glob': TokenType.GLOB,
        'proc': TokenType.PROC,
        'func': TokenType.FUNC,
        'main': TokenType.MAIN,
        'var': TokenType.VAR,
        'local': TokenType.LOCAL,
        'return': TokenType.RETURN,
        'halt': TokenType.HALT,
        'print': TokenType.PRINT,
        'while': TokenType.WHILE,
        'do': TokenType.DO,
        'until': TokenType.UNTIL,
        'if': TokenType.IF,
        'else': TokenType.ELSE,
        'neg': TokenType.NEG,
        'not': TokenType.NOT,
        'eq': TokenType.EQ,
        'or': TokenType.OR,
        'and': TokenType.AND,
        'plus': TokenType.PLUS,
        'minus': TokenType.MINUS,
        'mult': TokenType.MULT,
        'div': TokenType.DIV,
    }
    
    # Single character tokens mapping for lexer
    SINGLE_CHAR_TOKENS: Dict[str, TokenType] = {
        '(': TokenType.LPAREN,
        ')': TokenType.RPAREN,
        '{': TokenType.LBRACE,
        '}': TokenType.RBRACE,
        ';': TokenType.SEMICOLON,
        '=': TokenType.ASSIGN,
        '>': TokenType.GT,
    }
    
    # Token groups for lexer
    UNARY_OPERATORS: Set[TokenType] = {TokenType.NEG, TokenType.NOT}
    
    BINARY_OPERATORS: Set[TokenType] = {
        TokenType.EQ, TokenType.GT, TokenType.OR, TokenType.AND,
        TokenType.PLUS, TokenType.MINUS, TokenType.MULT, TokenType.DIV
    }
    
    COMPARISON_OPERATORS: Set[TokenType] = {TokenType.EQ, TokenType.GT}
    
    LOGICAL_OPERATORS: Set[TokenType] = {TokenType.OR, TokenType.AND}
    
    ARITHMETIC_OPERATORS: Set[TokenType] = {
        TokenType.PLUS, TokenType.MINUS, TokenType.MULT, TokenType.DIV
    }
    
    # Program structure keywords
    STRUCTURE_KEYWORDS: Set[TokenType] = {
        TokenType.GLOB, TokenType.PROC, TokenType.FUNC, TokenType.MAIN
    }
    
    # Statement keywords
    STATEMENT_KEYWORDS: Set[TokenType] = {
        TokenType.HALT, TokenType.PRINT, TokenType.IF, TokenType.WHILE, TokenType.DO
    }
    
    # Type keywords
    TYPE_KEYWORDS: Set[TokenType] = {TokenType.VAR, TokenType.LOCAL}


# Future: Operator precedence and associativity for parser (when implemented)
# class OperatorInfo(NamedTuple):
#     """Information about an operator for parsing"""
#     precedence: int
#     left_associative: bool

# class SPLOperators:
#     """Operator precedence and associativity information"""
#     pass

# Future: Grammar production rules for parser (when implemented)
# class SPLGrammar:
#     """Reference information about SPL grammar productions"""
#     pass


# Utility functions for type checking
def is_keyword(token_type: TokenType) -> bool:
    """Check if token type is a keyword"""
    return token_type in SPLConstants.KEYWORDS.values()


def is_operator(token_type: TokenType) -> bool:
    """Check if token type is an operator"""
    return token_type in SPLConstants.UNARY_OPERATORS or token_type in SPLConstants.BINARY_OPERATORS


def is_delimiter(token_type: TokenType) -> bool:
    """Check if token type is a delimiter"""
    return token_type in SPLConstants.SINGLE_CHAR_TOKENS.values()


def is_literal(token_type: TokenType) -> bool:
    """Check if token type is a literal"""
    return token_type in {TokenType.NUMBER, TokenType.STRING, TokenType.USER_DEFINED_NAME}


def token_type_to_string(token_type: TokenType) -> str:
    """Convert token type to human-readable string"""
    return token_type.value if token_type.value != token_type.name else token_type.name

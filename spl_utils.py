"""
SPL (Students' Programming Language) - Shared Utilities
COS341 Semester Project 2025

This module contains utility functions and helper classes used across
all phases of the SPL compiler.
"""

import re
from typing import List, Optional, TextIO
from spl_types import Token, TokenType, SPLConstants, SPLError


class SourceLocation:
    """Represents a location in source code"""
    def __init__(self, line: int, column: int, filename: Optional[str] = None):
        self.line = line
        self.column = column
        self.filename = filename
    
    def __str__(self) -> str:
        location = f"line {self.line}, column {self.column}"
        if self.filename:
            location = f"{self.filename}:{location}"
        return location
    
    def __repr__(self) -> str:
        return f"SourceLocation({self.line}, {self.column}, {self.filename!r})"


class SPLValidator:
    """Validation utilities for SPL language constructs"""
    
    @staticmethod
    def validate_user_defined_name(name: str) -> bool:
        """Validate a user-defined name according to SPL rules"""
        if not name:
            return False
        
        # Check against regex pattern
        if not re.match(SPLConstants.USER_DEFINED_NAME_PATTERN, name):
            return False
        
        # Check it's not a keyword
        return name not in SPLConstants.KEYWORDS
    
    @staticmethod
    def validate_number(number_str: str) -> bool:
        """Validate a number string according to SPL rules"""
        return bool(re.match(SPLConstants.NUMBER_PATTERN, number_str))
    
    @staticmethod
    def validate_string_content(content: str) -> bool:
        """Validate string content according to SPL rules"""
        if len(content) > SPLConstants.MAX_STRING_LENGTH:
            return False
        return bool(re.match(SPLConstants.STRING_CONTENT_PATTERN, content))
    
    @staticmethod
    def validate_parameter_count(count: int) -> bool:
        """Validate parameter count is within SPL limits"""
        return 0 <= count <= SPLConstants.MAX_PARAMETERS

class ErrorReporter:
    """Utility for collecting and reporting compiler errors"""
    
    def __init__(self):
        self.errors: List[SPLError] = []
        self.warnings: List[str] = []
    
    def add_error(self, error: SPLError):
        """Add an error to the collection"""
        self.errors.append(error)
    
    def add_warning(self, message: str, line: int = 0, column: int = 0):
        """Add a warning message"""
        if line > 0:
            warning = f"Warning at line {line}, column {column}: {message}"
        else:
            warning = f"Warning: {message}"
        self.warnings.append(warning)
    
    def has_errors(self) -> bool:
        """Check if any errors have been collected"""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if any warnings have been collected"""
        return len(self.warnings) > 0
    
    def print_errors(self, file: TextIO = None):
        """Print all errors to file or stdout"""
        import sys
        if file is None:
            file = sys.stderr
        
        for error in self.errors:
            print(f"ERROR: {error}", file=file)
    
    def print_warnings(self, file: TextIO = None):
        """Print all warnings to file or stdout"""
        import sys
        if file is None:
            file = sys.stderr
        
        for warning in self.warnings:
            print(warning, file=file)
    
    def clear(self):
        """Clear all errors and warnings"""
        self.errors.clear()
        self.warnings.clear()


class DebugPrinter:
    """Utility for debug printing with indentation"""
    
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.indent_level = 0
        self.indent_size = 2
    
    def print(self, message: str):
        """Print a debug message with current indentation"""
        if self.enabled:
            indent = " " * (self.indent_level * self.indent_size)
            print(f"{indent}{message}")
    
    def enter(self, context: str):
        """Enter a new debug context"""
        self.print(f"-> {context}")
        self.indent_level += 1
    
    def exit(self, context: str = ""):
        """Exit current debug context"""
        self.indent_level = max(0, self.indent_level - 1)
        if context:
            self.print(f"<- {context}")
    
    def enable(self):
        """Enable debug printing"""
        self.enabled = True
    
    def disable(self):
        """Disable debug printing"""
        self.enabled = False


def format_token_list(tokens: List[Token], max_tokens: int = 50) -> str:
    """Format a list of tokens for debugging output"""
    if not tokens:
        return "[]"
    
    if len(tokens) <= max_tokens:
        token_strs = [f"{t.type.name}({t.value!r})" for t in tokens]
    else:
        token_strs = [f"{t.type.name}({t.value!r})" for t in tokens[:max_tokens]]
        token_strs.append(f"... and {len(tokens) - max_tokens} more")
    
    return "[" + ", ".join(token_strs) + "]"


def create_error_token(message: str, line: int = 0, column: int = 0) -> Token:
    """Create a special error token for error recovery"""
    # Using COMMENT type as a placeholder for error tokens
    return Token(TokenType.COMMENT, f"ERROR: {message}", line, column)


def tokens_to_string(tokens: List[Token], include_positions: bool = False) -> str:
    """Convert list of tokens back to readable string representation"""
    if not tokens:
        return ""
    
    parts = []
    current_line = 1
    
    for token in tokens:
        if token.type == TokenType.EOF:
            break
        
        # Add newlines if needed
        if include_positions and token.line > current_line:
            parts.extend(["\n"] * (token.line - current_line))
            current_line = token.line
        
        # Add token value
        if token.type == TokenType.STRING:
            parts.append(f'"{token.value}"')
        elif token.type in SPLConstants.SINGLE_CHAR_TOKENS.values():
            parts.append(token.value)
        else:
            parts.append(token.value)
        
        # Add space after token (except for some delimiters)
        if (token.type not in {TokenType.LPAREN, TokenType.LBRACE} and 
            tokens.index(token) < len(tokens) - 1):
            next_token = tokens[tokens.index(token) + 1]
            if next_token.type not in {TokenType.RPAREN, TokenType.RBRACE, 
                                     TokenType.SEMICOLON, TokenType.EOF}:
                parts.append(" ")
    
    return "".join(parts)


class ConfigManager:
    """Simple configuration manager for compiler settings"""
    
    def __init__(self):
        self.settings = {
            'debug_lexer': False,
            # Future debug modes (when implemented)
            # 'debug_parser': False,
            # 'debug_semantic': False,
            # 'debug_codegen': False,
            'optimize_code': True,
            'target_language': 'python',  # Future: could support multiple targets
            'max_errors': 10,
            'show_warnings': True,
        }
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value):
        """Set configuration value"""
        self.settings[key] = value
    
    def enable_all_debug(self):
        """Enable all debug modes"""
        for key in self.settings:
            if key.startswith('debug_'):
                self.settings[key] = True
    
    def disable_all_debug(self):
        """Disable all debug modes"""
        for key in self.settings:
            if key.startswith('debug_'):
                self.settings[key] = False


# Global configuration instance
config = ConfigManager()

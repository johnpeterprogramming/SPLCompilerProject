"""
SPL (Students' Programming Language) Lexer
COS341 Semester Project 2025

This module implements the lexical analyzer for the SPL compiler.
It tokenizes the input source code according to the SPL grammar specification.
"""

import re
from typing import List, Optional

# Import shared types and utilities
from spl_types import (
    Token, TokenType, LexerError, SPLConstants
)
from spl_utils import SPLValidator, DebugPrinter


class SPLLexer:
    """Lexical analyzer for the SPL programming language"""
    
    def __init__(self, source_code: str, debug: bool = False):
        """Initialize the lexer with source code"""
        self.source = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self.debug_printer = DebugPrinter(debug)
    
    def current_char(self) -> Optional[str]:
        """Get the current character or None if at end"""
        if self.position >= len(self.source):
            return None
        return self.source[self.position]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        """Peek at character ahead by offset positions"""
        peek_pos = self.position + offset
        if peek_pos >= len(self.source):
            return None
        return self.source[peek_pos]
    
    def advance(self) -> None:
        """Move to the next character"""
        if self.position < len(self.source):
            if self.source[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1
    
    def skip_whitespace(self) -> None:
        """Skip whitespace characters (spaces, tabs, newlines)"""
        while self.current_char() and self.current_char().isspace():
            self.advance()
    
    def skip_comment(self) -> None:
        """Skip single-line comments starting with //"""
        if (self.current_char() == '/' and 
            self.peek_char() == '/'):
            # Skip the '//' 
            self.advance()
            self.advance()
            # Skip until end of line
            while self.current_char() and self.current_char() != '\n':
                self.advance()
    
    def read_string(self) -> str:
        """Read a string literal between quotes"""
        value = ""
        start_line = self.line
        start_column = self.column
        
        self.debug_printer.print(f"Reading string literal at {start_line}:{start_column}")
        
        # Skip opening quote
        self.advance()
        
        while self.current_char() and self.current_char() != '"':
            if len(value) >= SPLConstants.MAX_STRING_LENGTH:
                raise LexerError("String literal exceeds maximum length of 15 characters", 
                               start_line, start_column)
            value += self.current_char()
            self.advance()
        
        if not self.current_char():
            raise LexerError("Unterminated string literal", start_line, start_column)
        
        # Skip closing quote
        self.advance()
        
        # Validate string content using shared validator
        if not SPLValidator.validate_string_content(value):
            raise LexerError("String literal contains invalid characters", start_line, start_column)
        
        self.debug_printer.print(f"String literal: {repr(value)}")
        return value
    
    def read_number(self) -> str:
        """Read a number literal"""
        value = ""
        start_line = self.line
        start_column = self.column
        
        self.debug_printer.print(f"Reading number at {start_line}:{start_column}")
        
        # Handle zero or numbers starting with 1-9
        if self.current_char() == '0':
            value = '0'
            self.advance()
            # Zero should not be followed by more digits
            if self.current_char() and self.current_char().isdigit():
                raise LexerError("Invalid number format: leading zeros not allowed", 
                               self.line, self.column)
        else:
            # Number starting with 1-9
            while self.current_char() and self.current_char().isdigit():
                value += self.current_char()
                self.advance()
        
        # Validate using shared validator
        if not SPLValidator.validate_number(value):
            raise LexerError(f"Invalid number format: {value}", start_line, start_column)
        
        self.debug_printer.print(f"Number: {value}")
        return value
    
    def read_identifier(self) -> str:
        """Read an identifier (user-defined name)"""
        value = ""
        start_line = self.line
        start_column = self.column
        
        self.debug_printer.print(f"Reading identifier at {start_line}:{start_column}")
        
        # First part: [a-z]+
        if not (self.current_char() and self.current_char().islower()):
            raise LexerError("Identifier must start with lowercase letter", 
                           self.line, self.column)
        
        while self.current_char() and self.current_char().islower():
            value += self.current_char()
            self.advance()
        
        # Optional second part: more lowercase letters
        while self.current_char() and self.current_char().islower():
            value += self.current_char()
            self.advance()
        
        # Optional third part: digits
        while self.current_char() and self.current_char().isdigit():
            value += self.current_char()
            self.advance()
        
        # Basic pattern validation (don't check keywords here - that's done in tokenize)
        if not re.match(SPLConstants.USER_DEFINED_NAME_PATTERN, value):
            raise LexerError(f"Invalid identifier format: {value}", start_line, start_column)
        
        self.debug_printer.print(f"Identifier: {value}")
        return value
    
    def tokenize(self) -> List[Token]:
        """Tokenize the entire source code"""
        self.tokens = []
        self.debug_printer.print("Starting tokenization")
        
        while self.current_char():
            start_line = self.line
            start_column = self.column
            char = self.current_char()
            
            # Skip whitespace
            if char.isspace():
                self.skip_whitespace()
                continue
            
            # Skip comments
            if char == '/' and self.peek_char() == '/':
                self.skip_comment()
                continue
            
            # String literals
            if char == '"':
                string_value = self.read_string()
                self.tokens.append(Token(TokenType.STRING, string_value, start_line, start_column))
                continue
            
            # Numbers
            if char.isdigit():
                number_value = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, number_value, start_line, start_column))
                continue
            
            # Single character tokens
            if char in SPLConstants.SINGLE_CHAR_TOKENS:
                token_type = SPLConstants.SINGLE_CHAR_TOKENS[char]
                self.tokens.append(Token(token_type, char, start_line, start_column))
                self.advance()
                continue
            
            # Identifiers and keywords
            if char.islower():
                identifier = self.read_identifier()
                # Check if it's a keyword using shared constants
                if identifier in SPLConstants.KEYWORDS:
                    token_type = SPLConstants.KEYWORDS[identifier]
                else:
                    token_type = TokenType.USER_DEFINED_NAME
                
                self.tokens.append(Token(token_type, identifier, start_line, start_column))
                continue
            
            # Unknown character
            raise LexerError(f"Unexpected character: '{char}'", start_line, start_column)
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        
        self.debug_printer.print(f"Tokenization complete: {len(self.tokens)} tokens")
        return self.tokens
    
    def get_tokens(self) -> List[Token]:
        """Get the list of tokens (tokenize if not done yet)"""
        if not self.tokens:
            self.tokenize()
        return self.tokens


def tokenize_spl(source_code: str, debug: bool = False) -> List[Token]:
    """Convenience function to tokenize SPL source code"""
    lexer = SPLLexer(source_code, debug)
    return lexer.tokenize()
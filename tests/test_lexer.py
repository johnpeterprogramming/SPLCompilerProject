"""
Test suite for the SPL Lexer
COS341 Semester Project 2025

Comprehensive tests for the lexical analyzer including:
- Token type recognition
- Keywords vs identifiers
- Number parsing
- String parsing
- Error handling
- Complex programs
"""

import unittest
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import SPLLexer, tokenize_spl
from spl_types import Token, TokenType, LexerError


class TestTokenTypes(unittest.TestCase):
    """Test basic token type recognition"""
    
    def test_keywords(self):
        """Test all SPL keywords are recognized correctly"""
        keywords_test_cases = [
            ("glob", TokenType.GLOB),
            ("proc", TokenType.PROC),
            ("func", TokenType.FUNC),
            ("main", TokenType.MAIN),
            ("var", TokenType.VAR),
            ("local", TokenType.LOCAL),
            ("return", TokenType.RETURN),
            ("halt", TokenType.HALT),
            ("print", TokenType.PRINT),
            ("while", TokenType.WHILE),
            ("do", TokenType.DO),
            ("until", TokenType.UNTIL),
            ("if", TokenType.IF),
            ("else", TokenType.ELSE),
            ("neg", TokenType.NEG),
            ("not", TokenType.NOT),
            ("eq", TokenType.EQ),
            ("or", TokenType.OR),
            ("and", TokenType.AND),
            ("plus", TokenType.PLUS),
            ("minus", TokenType.MINUS),
            ("mult", TokenType.MULT),
            ("div", TokenType.DIV),
        ]
        
        for keyword, expected_type in keywords_test_cases:
            with self.subTest(keyword=keyword):
                tokens = tokenize_spl(keyword)
                self.assertEqual(len(tokens), 2)  # keyword + EOF
                self.assertEqual(tokens[0].type, expected_type)
                self.assertEqual(tokens[0].value, keyword)
    
    def test_delimiters(self):
        """Test delimiter tokens"""
        delimiters_test_cases = [
            ("(", TokenType.LPAREN),
            (")", TokenType.RPAREN),
            ("{", TokenType.LBRACE),
            ("}", TokenType.RBRACE),
            (";", TokenType.SEMICOLON),
            ("=", TokenType.ASSIGN),
            (">", TokenType.GT),
        ]
        
        for delimiter, expected_type in delimiters_test_cases:
            with self.subTest(delimiter=delimiter):
                tokens = tokenize_spl(delimiter)
                self.assertEqual(len(tokens), 2)  # delimiter + EOF
                self.assertEqual(tokens[0].type, expected_type)
                self.assertEqual(tokens[0].value, delimiter)


class TestNumbers(unittest.TestCase):
    """Test number parsing according to SPL rules"""
    
    def test_valid_numbers(self):
        """Test valid number formats"""
        valid_numbers = [
            "0",
            "1",
            "42",
            "123",
            "999",
            "1000000"
        ]
        
        for number in valid_numbers:
            with self.subTest(number=number):
                tokens = tokenize_spl(number)
                self.assertEqual(len(tokens), 2)  # number + EOF
                self.assertEqual(tokens[0].type, TokenType.NUMBER)
                self.assertEqual(tokens[0].value, number)
    
    def test_invalid_numbers(self):
        """Test invalid number formats should raise errors"""
        invalid_numbers = [
            "01",  # Leading zero
            "000", # Multiple leading zeros
            "0123" # Zero followed by digits
        ]
        
        for number in invalid_numbers:
            with self.subTest(number=number):
                with self.assertRaises(LexerError):
                    tokenize_spl(number)


class TestStrings(unittest.TestCase):
    """Test string parsing according to SPL rules"""
    
    def test_valid_strings(self):
        """Test valid string formats"""
        valid_strings = [
            ('""', ""),
            ('"hello"', "hello"),
            ('"123"', "123"),
            ('"abc123"', "abc123"),
            ('"HELLO"', "HELLO"),
            ('"a1b2c3"', "a1b2c3"),
            ('"123456789012345"', "123456789012345"),  # Max length 15
        ]
        
        for string_input, expected_value in valid_strings:
            with self.subTest(string_input=string_input):
                tokens = tokenize_spl(string_input)
                self.assertEqual(len(tokens), 2)  # string + EOF
                self.assertEqual(tokens[0].type, TokenType.STRING)
                self.assertEqual(tokens[0].value, expected_value)
    
    def test_invalid_strings(self):
        """Test invalid string formats should raise errors"""
        invalid_strings = [
            '"unterminated',  # No closing quote
            '"toolongstring123456"',  # Exceeds 15 characters
            '"hello world"',  # Contains space (not allowed in SPL)
            '"hello@world"',  # Contains special character
            '"hello-world"',  # Contains hyphen
        ]
        
        for string_input in invalid_strings:
            with self.subTest(string_input=string_input):
                with self.assertRaises(LexerError):
                    tokenize_spl(string_input)


class TestIdentifiers(unittest.TestCase):
    """Test user-defined name parsing according to SPL rules"""
    
    def test_valid_identifiers(self):
        """Test valid identifier formats"""
        valid_identifiers = [
            "a",
            "abc",
            "hello",
            "variable",
            "a1",
            "abc123",
            "hello456",
            "test1234567890",
            "verylongname999"
        ]
        
        for identifier in valid_identifiers:
            with self.subTest(identifier=identifier):
                tokens = tokenize_spl(identifier)
                self.assertEqual(len(tokens), 2)  # identifier + EOF
                self.assertEqual(tokens[0].type, TokenType.USER_DEFINED_NAME)
                self.assertEqual(tokens[0].value, identifier)
    
    def test_identifier_vs_keyword(self):
        """Test that keywords are not treated as identifiers"""
        # This should be a keyword, not an identifier
        tokens = tokenize_spl("while")
        self.assertEqual(tokens[0].type, TokenType.WHILE)
        
        # This should be an identifier (keywords + digits = identifier)
        tokens = tokenize_spl("while123")
        self.assertEqual(tokens[0].type, TokenType.USER_DEFINED_NAME)


class TestWhitespaceAndComments(unittest.TestCase):
    """Test whitespace and comment handling"""
    
    def test_whitespace_skipping(self):
        """Test that whitespace is properly skipped"""
        test_cases = [
            "   hello   ",
            "\thello\t",
            "\nhello\n",
            " \t\n hello \t\n ",
        ]
        
        for test_input in test_cases:
            with self.subTest(test_input=repr(test_input)):
                tokens = tokenize_spl(test_input)
                # Should only have identifier + EOF
                self.assertEqual(len(tokens), 2)
                self.assertEqual(tokens[0].type, TokenType.USER_DEFINED_NAME)
                self.assertEqual(tokens[0].value, "hello")
    
    def test_comment_skipping(self):
        """Test that comments are properly skipped"""
        test_cases = [
            "hello // this is a comment",
            "hello//comment",
            "// comment at start\nhello",
            "hello // comment\n// another comment",
        ]
        
        for test_input in test_cases:
            with self.subTest(test_input=repr(test_input)):
                tokens = tokenize_spl(test_input)
                # Should only have identifier + EOF (comments skipped)
                self.assertEqual(len(tokens), 2)
                self.assertEqual(tokens[0].type, TokenType.USER_DEFINED_NAME)
                self.assertEqual(tokens[0].value, "hello")


class TestComplexPrograms(unittest.TestCase):
    """Test lexing of complete SPL program fragments"""
    
    def test_simple_program_structure(self):
        """Test tokenizing a simple program structure"""
        program = """
        glob {
            x
        }
        main {
            var { y }
            halt
        }
        """
        
        tokens = tokenize_spl(program)
        expected_types = [
            TokenType.GLOB, TokenType.LBRACE, TokenType.USER_DEFINED_NAME,
            TokenType.RBRACE, TokenType.MAIN, TokenType.LBRACE,
            TokenType.VAR, TokenType.LBRACE, TokenType.USER_DEFINED_NAME,
            TokenType.RBRACE, TokenType.HALT, TokenType.RBRACE, TokenType.EOF
        ]
        
        actual_types = [token.type for token in tokens]
        self.assertEqual(actual_types, expected_types)
    
    def test_function_definition(self):
        """Test tokenizing a function definition"""
        program = """
        func {
            add(x y) {
                local { result }
                result = x plus y;
                return result
            }
        }
        """
        
        tokens = tokenize_spl(program)
        # Verify we get the right sequence of tokens
        self.assertGreater(len(tokens), 10)
        self.assertEqual(tokens[0].type, TokenType.FUNC)
        self.assertEqual(tokens[-1].type, TokenType.EOF)
        
        # Check that identifiers are properly recognized
        identifier_tokens = [t for t in tokens if t.type == TokenType.USER_DEFINED_NAME]
        self.assertEqual(len(identifier_tokens), 8)  # add, x, y, result (appears twice each)
    
    def test_arithmetic_expression(self):
        """Test tokenizing arithmetic expressions"""
        program = "result = (a plus b) mult (c minus d)"
        
        tokens = tokenize_spl(program)
        expected_types = [
            TokenType.USER_DEFINED_NAME, TokenType.ASSIGN, TokenType.LPAREN,
            TokenType.USER_DEFINED_NAME, TokenType.PLUS, TokenType.USER_DEFINED_NAME,
            TokenType.RPAREN, TokenType.MULT, TokenType.LPAREN,
            TokenType.USER_DEFINED_NAME, TokenType.MINUS, TokenType.USER_DEFINED_NAME,
            TokenType.RPAREN, TokenType.EOF
        ]
        
        actual_types = [token.type for token in tokens]
        self.assertEqual(actual_types, expected_types)
    
    def test_conditional_statement(self):
        """Test tokenizing conditional statements"""
        program = """
        if (x > 0) {
            print "positive"
        } else {
            print "notpositive"
        }
        """
        
        tokens = tokenize_spl(program)
        # Check key tokens are present
        token_types = [token.type for token in tokens]
        
        self.assertIn(TokenType.IF, token_types)
        self.assertIn(TokenType.ELSE, token_types)
        self.assertIn(TokenType.PRINT, token_types)
        self.assertIn(TokenType.GT, token_types)
        self.assertIn(TokenType.STRING, token_types)
    
    def test_loop_statements(self):
        """Test tokenizing loop statements"""
        program1 = "while (x > 0) { x = x minus 1 }"
        program2 = "do { x = x plus 1 } until (x eq 10)"
        
        tokens1 = tokenize_spl(program1)
        token_types1 = [token.type for token in tokens1]
        self.assertIn(TokenType.WHILE, token_types1)
        
        tokens2 = tokenize_spl(program2)
        token_types2 = [token.type for token in tokens2]
        self.assertIn(TokenType.DO, token_types2)
        self.assertIn(TokenType.UNTIL, token_types2)


class TestErrorHandling(unittest.TestCase):
    """Test proper error handling and reporting"""
    
    def test_line_and_column_tracking(self):
        """Test that line and column numbers are tracked correctly"""
        program = """glob {
    x
}"""
        tokens = tokenize_spl(program)
        
        # glob should be at line 1, column 1
        self.assertEqual(tokens[0].line, 1)
        self.assertEqual(tokens[0].column, 1)
        
        # x should be at line 2, column 5 (after 4 spaces)
        x_token = next(t for t in tokens if t.value == "x")
        self.assertEqual(x_token.line, 2)
        self.assertEqual(x_token.column, 5)
    
    def test_error_reporting(self):
        """Test that errors include proper line and column information"""
        program = """glob {
    x = 01  // Invalid number
}"""
        
        with self.assertRaises(LexerError) as context:
            tokenize_spl(program)
        
        error = context.exception
        self.assertEqual(error.line, 2)
        self.assertIn("leading zeros", str(error))
    
    def test_unexpected_character(self):
        """Test handling of unexpected characters"""
        with self.assertRaises(LexerError) as context:
            tokenize_spl("hello @ world")
        
        error = context.exception
        self.assertIn("Unexpected character", str(error))
        self.assertIn("@", str(error))


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def test_empty_input(self):
        """Test lexing empty input"""
        tokens = tokenize_spl("")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.EOF)
    
    def test_only_whitespace(self):
        """Test lexing input with only whitespace"""
        tokens = tokenize_spl("   \n\t  ")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.EOF)
    
    def test_only_comments(self):
        """Test lexing input with only comments"""
        tokens = tokenize_spl("// comment 1\n// comment 2")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.EOF)
    
    def test_adjacent_tokens(self):
        """Test tokens that are adjacent with no whitespace"""
        tokens = tokenize_spl("hello(world)")
        expected_types = [
            TokenType.USER_DEFINED_NAME, TokenType.LPAREN,
            TokenType.USER_DEFINED_NAME, TokenType.RPAREN, TokenType.EOF
        ]
        actual_types = [token.type for token in tokens]
        self.assertEqual(actual_types, expected_types)
    
    def test_maximum_string_length(self):
        """Test string at maximum allowed length"""
        max_string = '"' + "a" * 15 + '"'  # 15 characters
        tokens = tokenize_spl(max_string)
        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(len(tokens[0].value), 15)


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)
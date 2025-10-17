"""
Tests for SPL Semantic Analyzer
COS341 Semester Project 2025

Tests for all name-scope rules and semantic checking.
"""

import unittest
from lexer import tokenize_spl
from parser import parse_spl
from semantic_analyzer import analyze_semantics
from spl_types import SemanticError


class TestSemanticAnalyzer(unittest.TestCase):
    """Test semantic analysis and name-scope rules"""
    
    def _analyze_program(self, program_text):
        """Helper to tokenize, parse, and analyze a program"""
        tokens = tokenize_spl(program_text)
        ast = parse_spl(tokens)
        symbol_table, errors = analyze_semantics(ast)
        return symbol_table, errors
    
    # ============= Everywhere Scope Tests =============
    
    def test_valid_program_no_conflicts(self):
        """Test a valid program with no name conflicts"""
        program = """
        glob { x y }
        proc { myproc() { local {} halt } }
        func { myfunc() { local {} halt; return 0 } }
        main { var { z } halt }
        """
        symbol_table, errors = self._analyze_program(program)
        self.assertFalse(errors.has_errors(), 
                        f"Expected no errors, got: {[str(e) for e in errors.errors]}")
    
    def test_variable_conflicts_with_procedure(self):
        """Test variable name conflicts with procedure name"""
        program = """
        glob { myname }
        proc { myname() { local {} halt } }
        func { }
        main { var {} halt }
        """
        symbol_table, errors = self._analyze_program(program)
        self.assertTrue(errors.has_errors())
        self.assertTrue(any("conflicts with procedure" in str(e) for e in errors.errors))
    
    def test_variable_conflicts_with_function(self):
        """Test variable name conflicts with function name"""
        program = """
        glob { compute }
        proc { }
        func { compute() { local {} halt; return 0 } }
        main { var {} halt }
        """
        symbol_table, errors = self._analyze_program(program)
        self.assertTrue(errors.has_errors())
        self.assertTrue(any("conflicts with function" in str(e) for e in errors.errors))
    
    def test_procedure_conflicts_with_function(self):
        """Test procedure name conflicts with function name"""
        program = """
        glob { }
        proc { process() { local {} halt } }
        func { process() { local {} halt; return 0 } }
        main { var {} halt }
        """
        symbol_table, errors = self._analyze_program(program)
        self.assertTrue(errors.has_errors())
        self.assertTrue(any("conflicts with function" in str(e) for e in errors.errors))
    
    # ============= Duplicate Declaration Tests =============
    
    def test_duplicate_global_variables(self):
        """Test duplicate global variable declarations"""
        program = """
        glob { x y x }
        proc { }
        func { }
        main { var {} halt }
        """
        symbol_table, errors = self._analyze_program(program)
        self.assertTrue(errors.has_errors())
        self.assertTrue(any("Duplicate global variable" in str(e) for e in errors.errors))
    
    def test_duplicate_procedures(self):
        """Test duplicate procedure declarations"""
        program = """
        glob { }
        proc { 
            myproc() { local {} halt }
            myproc() { local {} halt }
        }
        func { }
        main { var {} halt }
        """
        symbol_table, errors = self._analyze_program(program)
        self.assertTrue(errors.has_errors())
        self.assertTrue(any("Duplicate procedure" in str(e) for e in errors.errors))
    
    def test_duplicate_functions(self):
        """Test duplicate function declarations"""
        program = """
        glob { }
        proc { }
        func { 
            calc() { local {} halt; return 0 }
            calc() { local {} halt; return 0 }
        }
        main { var {} halt }
        """
        symbol_table, errors = self._analyze_program(program)
        self.assertTrue(errors.has_errors())
        self.assertTrue(any("Duplicate function" in str(e) for e in errors.errors))
    
    def test_duplicate_main_variables(self):
        """Test duplicate variable declarations in main"""
        program = """
        glob { }
        proc { }
        func { }
        main { var { a b a } halt }
        """
        symbol_table, errors = self._analyze_program(program)
        self.assertTrue(errors.has_errors())
        self.assertTrue(any("Duplicate variable" in str(e) and "main" in str(e) 
                          for e in errors.errors))
    
    # ============= Parameter Tests =============
    
    def test_duplicate_parameters_in_procedure(self):
        """Test duplicate parameters in procedure"""
        program = """
        glob { }
        proc { myproc(x y x) { local {} halt } }
        func { }
        main { var {} halt }
        """
        symbol_table, errors = self._analyze_program(program)
        self.assertTrue(errors.has_errors())
        self.assertTrue(any("Duplicate parameter" in str(e) for e in errors.errors))
    
    def test_duplicate_parameters_in_function(self):
        """Test duplicate parameters in function"""
        program = """
        glob { }
        proc { }
        func { calc(a b a) { local {} halt; return 0 } }
        main { var {} halt }
        """
        symbol_table, errors = self._analyze_program(program)
        self.assertTrue(errors.has_errors())
        self.assertTrue(any("Duplicate parameter" in str(e) for e in errors.errors))
    
    def test_parameter_shadowing_in_procedure(self):
        """Test local variable shadowing parameter in procedure"""
        program = """
        glob { }
        proc { myproc(x) { local { x } halt } }
        func { }
        main { var {} halt }
        """
        symbol_table, errors = self._analyze_program(program)
        self.assertTrue(errors.has_errors())
        self.assertTrue(any("shadows parameter" in str(e) for e in errors.errors))
    
    def test_parameter_shadowing_in_function(self):
        """Test local variable shadowing parameter in function"""
        program = """
        glob { }
        proc { }
        func { calc(a) { local { a } halt; return 0 } }
        main { var {} halt }
        """
        symbol_table, errors = self._analyze_program(program)
        self.assertTrue(errors.has_errors())
        self.assertTrue(any("shadows parameter" in str(e) for e in errors.errors))
    
    # ============= Local Variable Tests =============
    
    def test_duplicate_local_variables(self):
        """Test duplicate local variable declarations"""
        program = """
        glob { }
        proc { myproc() { local { temp temp } halt } }
        func { }
        main { var {} halt }
        """
        symbol_table, errors = self._analyze_program(program)
        self.assertTrue(errors.has_errors())
        self.assertTrue(any("Duplicate local variable" in str(e) for e in errors.errors))
    
    def test_valid_local_variables(self):
        """Test valid local variables that don't shadow"""
        program = """
        glob { global1 }
        proc { myproc(param1) { local { local1 local2 } halt } }
        func { }
        main { var {} halt }
        """
        symbol_table, errors = self._analyze_program(program)
        self.assertFalse(errors.has_errors(),
                        f"Expected no errors, got: {[str(e) for e in errors.errors]}")
    
    # ============= Variable Resolution Tests =============
    
    def test_undeclared_variable_in_procedure(self):
        """Test undeclared variable in procedure"""
        program = """
        glob { x }
        proc { myproc() { local {} y = 10; halt } }
        func { }
        main { var {} halt }
        """
        symbol_table, errors = self._analyze_program(program)
        self.assertTrue(errors.has_errors())
        self.assertTrue(any("Undeclared variable 'y'" in str(e) for e in errors.errors))
    
    def test_undeclared_variable_in_function(self):
        """Test undeclared variable in function"""
        program = """
        glob { }
        proc { }
        func { calc() { local {} z = unknown; halt; return 0 } }
        main { var {} halt }
        """
        symbol_table, errors = self._analyze_program(program)
        self.assertTrue(errors.has_errors())
        self.assertTrue(any("Undeclared variable" in str(e) for e in errors.errors))
    
    def test_undeclared_variable_in_main(self):
        """Test undeclared variable in main"""
        program = """
        glob { x }
        proc { }
        func { }
        main { var { a } b = 5; halt }
        """
        symbol_table, errors = self._analyze_program(program)
        self.assertTrue(errors.has_errors())
        self.assertTrue(any("Undeclared variable 'b'" in str(e) for e in errors.errors))
    
    def test_parameter_resolution(self):
        """Test that parameters are correctly resolved"""
        program = """
        glob { }
        proc { myproc(x) { local {} x = 10; halt } }
        func { }
        main { var {} halt }
        """
        symbol_table, errors = self._analyze_program(program)
        self.assertFalse(errors.has_errors(),
                        f"Expected no errors, got: {[str(e) for e in errors.errors]}")
    
    def test_local_variable_resolution(self):
        """Test that local variables are correctly resolved"""
        program = """
        glob { }
        proc { myproc() { local { temp } temp = 5; halt } }
        func { }
        main { var {} halt }
        """
        symbol_table, errors = self._analyze_program(program)
        self.assertFalse(errors.has_errors(),
                        f"Expected no errors, got: {[str(e) for e in errors.errors]}")
    
    def test_global_variable_resolution_in_procedure(self):
        """Test that global variables are accessible in procedure"""
        program = """
        glob { global1 }
        proc { myproc() { local {} global1 = 10; halt } }
        func { }
        main { var {} halt }
        """
        symbol_table, errors = self._analyze_program(program)
        self.assertFalse(errors.has_errors(),
                        f"Expected no errors, got: {[str(e) for e in errors.errors]}")
    
    def test_global_variable_resolution_in_main(self):
        """Test that global variables are accessible in main"""
        program = """
        glob { global1 }
        proc { }
        func { }
        main { var { local1 } global1 = 100; halt }
        """
        symbol_table, errors = self._analyze_program(program)
        self.assertFalse(errors.has_errors(),
                        f"Expected no errors, got: {[str(e) for e in errors.errors]}")
    
    def test_resolution_hierarchy(self):
        """Test variable resolution hierarchy: param > local > global"""
        program = """
        glob { x }
        proc { 
            proc1(x) { local {} x = 1; halt }
            proc2() { local { x } x = 2; halt }
            proc3() { local {} x = 3; halt }
        }
        func { }
        main { var {} halt }
        """
        symbol_table, errors = self._analyze_program(program)
        self.assertFalse(errors.has_errors(),
                        f"Expected no errors, got: {[str(e) for e in errors.errors]}")
    
    # ============= Complex Program Tests =============
    
    def test_complex_valid_program(self):
        """Test a complex valid program"""
        program = """
        glob { result counter }
        proc {
            init() { local { temp } counter = 0; halt }
            increment(val) { local {} counter = ( counter plus val ); halt }
        }
        func {
            add(x y) { local { sum } sum = ( x plus y ); return sum }
            multiply(a b) { local { prod temp } prod = ( a mult b ); return prod }
        }
        main {
            var { num1 num2 }
            num1 = 10;
            num2 = 20;
            result = add(num1 num2);
            print result;
            halt
        }
        """
        symbol_table, errors = self._analyze_program(program)
        self.assertFalse(errors.has_errors(),
                        f"Expected no errors, got: {[str(e) for e in errors.errors]}")
    
    def test_complex_program_with_errors(self):
        """Test a complex program with multiple errors"""
        program = """
        glob { x x }
        proc { 
            proc1(a a) { local { a } halt }
            proc1() { local {} halt }
        }
        func {
            proc1() { local {} halt; return 0 }
        }
        main { var { y y } z = 10; halt }
        """
        symbol_table, errors = self._analyze_program(program)
        self.assertTrue(errors.has_errors())
        # Should have multiple errors
        self.assertGreater(len(errors.errors), 3)
    
    # ============= Variable Usage in Expressions Tests =============
    
    def test_variables_in_expressions(self):
        """Test variable usage in complex expressions"""
        program = """
        glob { a b }
        proc { }
        func { calc(x y) { local { z } z = ( ( x plus y ) mult 2 ); return z } }
        main { var { c } c = ( a plus b ); halt }
        """
        symbol_table, errors = self._analyze_program(program)
        self.assertFalse(errors.has_errors(),
                        f"Expected no errors, got: {[str(e) for e in errors.errors]}")
    
    def test_undeclared_in_expression(self):
        """Test undeclared variable in expression"""
        program = """
        glob { a }
        proc { }
        func { }
        main { var { c } c = ( a plus undeclared ); halt }
        """
        symbol_table, errors = self._analyze_program(program)
        self.assertTrue(errors.has_errors())
        self.assertTrue(any("Undeclared variable 'undeclared'" in str(e) 
                          for e in errors.errors))
    
    def test_variables_in_conditions(self):
        """Test variable usage in conditions"""
        program = """
        glob { x }
        proc { }
        func { }
        main { 
            var { y z }
            y = 10;
            if ( x eq y ) { z = 1; halt } else { z = 0; halt };
            halt
        }
        """
        symbol_table, errors = self._analyze_program(program)
        self.assertFalse(errors.has_errors(),
                        f"Expected no errors, got: {[str(e) for e in errors.errors]}")
    
    # ============= Same Name Different Scopes Tests =============
    
    def test_same_name_different_scopes(self):
        """Test same variable name in different scopes (should be allowed)"""
        program = """
        glob { temp }
        proc { 
            proc1() { local { temp } temp = 1; halt }
            proc2() { local { temp } temp = 2; halt }
        }
        func { 
            func1() { local { temp } temp = 3; return temp }
        }
        main { var { temp } temp = 4; halt }
        """
        symbol_table, errors = self._analyze_program(program)
        self.assertFalse(errors.has_errors(),
                        f"Expected no errors, got: {[str(e) for e in errors.errors]}")
        
        # Verify all temps are in symbol table but in different scopes
        temps = symbol_table.lookup_by_name('temp')
        self.assertGreater(len(temps), 1)


class TestSymbolTable(unittest.TestCase):
    """Test symbol table functionality"""
    
    def test_symbol_table_creation(self):
        """Test that symbol table is correctly populated"""
        program = """
        glob { x y }
        proc { myproc(a) { local { b } halt } }
        func { myfunc() { local {} halt; return 0 } }
        main { var { z } halt }
        """
        tokens = tokenize_spl(program)
        ast = parse_spl(tokens)
        symbol_table, errors = analyze_semantics(ast)
        
        # Check that we have symbols
        self.assertGreater(len(symbol_table.symbols), 0)
        
        # Check global variables
        global_vars = symbol_table.get_symbols_in_scope(symbol_table.by_scope.keys().__iter__().__next__())
        
        # Check that we can lookup symbols
        x_symbols = symbol_table.lookup_by_name('x')
        self.assertEqual(len(x_symbols), 1)
        self.assertEqual(x_symbols[0].name, 'x')


if __name__ == '__main__':
    unittest.main()


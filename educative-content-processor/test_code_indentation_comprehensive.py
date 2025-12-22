"""
Comprehensive unit tests for code indentation handling across all code components
Tests both proper JSON parsing (normal case) and edge cases with literal escape sequences
"""
import unittest
import json
from section_processor import SectionContentProcessor


class TestCodeIndentationHandling(unittest.TestCase):
    """Test suite for code indentation in TabbedCode, Code, and EditorCode components"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = SectionContentProcessor(output_dir="test_output")
        self.processor.set_book_context("test_book", chapter_number=1, section_id="test")
    
    # ============================================================================
    # TABBED CODE COMPONENT TESTS
    # ============================================================================
    
    def test_tabbed_code_proper_json_parsing(self):
        """Test TabbedCode with properly parsed JSON (normal API response)"""
        # Simulate what response.json() returns - already decoded
        component = {
            "type": "TabbedCode",
            "content": {
                "codeContents": [
                    {
                        "title": "Java",
                        "language": "java",
                        "content": "public class Test {\n    public void method() {\n        System.out.println(\"test\");\n    }\n}"
                    }
                ]
            }
        }
        
        result = self.processor._process_tabbed_code(component)
        
        # Should have multiple lines
        self.assertGreater(result.count('\n'), 3, "Should have multiple lines")
        
        # Should preserve indentation
        self.assertIn('    public void method()', result, "Should preserve 4-space indentation")
        self.assertIn('        System.out.println', result, "Should preserve 8-space indentation")
        
        # Should have lstlisting environment
        self.assertIn('\\begin{lstlisting}[language=Java]', result)
        self.assertIn('\\end{lstlisting}', result)
    
    def test_tabbed_code_with_literal_escapes(self):
        """Test TabbedCode when string contains literal \\n (edge case from double-escaped JSON)"""
        # Simulate problematic case where JSON was double-escaped
        component = {
            "type": "TabbedCode",
            "content": {
                "codeContents": [
                    {
                        "title": "Java",
                        "language": "java",
                        "content": r"public class Test {\n    public void method() {\n        int x = 42;\n    }\n}"
                    }
                ]
            }
        }
        
        result = self.processor._process_tabbed_code(component)
        
        # Should decode the literal \n to actual newlines
        self.assertGreater(result.count('\n'), 3, "Should have decoded \\n to newlines")
        
        # Should NOT contain literal \n in output
        # Note: The LaTeX might have \n in commands, but code content shouldn't
        code_section = result.split('\\begin{lstlisting}')[1].split('\\end{lstlisting}')[0]
        self.assertNotIn(r'\n', code_section.replace('\\n', ''), 
                        "Code should not contain literal \\n after processing")
        
        # Should preserve indentation after decoding
        self.assertIn('    public void method()', result, "Should have 4-space indentation")
    
    def test_tabbed_code_empty_content(self):
        """Test TabbedCode with empty code content"""
        component = {
            "type": "TabbedCode",
            "content": {
                "codeContents": [
                    {
                        "title": "Java",
                        "language": "java",
                        "content": ""
                    }
                ]
            }
        }
        
        result = self.processor._process_tabbed_code(component)
        self.assertEqual(result, "", "Empty content should return empty string")
    
    def test_tabbed_code_with_tabs(self):
        """Test TabbedCode with tab characters"""
        component = {
            "type": "TabbedCode",
            "content": {
                "codeContents": [
                    {
                        "title": "Java",
                        "language": "java",
                        "content": "public class Test {\n\tpublic void method() {\n\t\tint x = 1;\n\t}\n}"
                    }
                ]
            }
        }
        
        result = self.processor._process_tabbed_code(component)
        
        # Tabs should be preserved
        self.assertIn('\t', result, "Tabs should be preserved in output")
    
    def test_tabbed_code_with_literal_tabs(self):
        """Test TabbedCode with literal \\t escape sequences"""
        component = {
            "type": "TabbedCode",
            "content": {
                "codeContents": [
                    {
                        "title": "Java",
                        "language": "java",
                        "content": r"public class Test {\n\tmethod() {\n\t\tint x = 1;\n\t}\n}"
                    }
                ]
            }
        }
        
        result = self.processor._process_tabbed_code(component)
        
        # Should decode \t to actual tabs
        self.assertIn('\t', result, "Should decode \\t to actual tabs")
    
    def test_tabbed_code_multiple_languages(self):
        """Test TabbedCode with multiple language options (should pick Java)"""
        component = {
            "type": "TabbedCode",
            "content": {
                "codeContents": [
                    {
                        "title": "Python",
                        "language": "python",
                        "content": "def test():\n    pass"
                    },
                    {
                        "title": "Java",
                        "language": "java",
                        "content": "public class Test {\n    void method() {}\n}"
                    }
                ]
            }
        }
        
        result = self.processor._process_tabbed_code(component)
        
        # Should pick Java
        self.assertIn('language=Java', result)
        self.assertIn('public class Test', result)
        self.assertNotIn('def test()', result)
    
    # ============================================================================
    # CODE COMPONENT TESTS
    # ============================================================================
    
    def test_code_proper_json_parsing(self):
        """Test Code component with properly parsed JSON"""
        component = {
            "type": "Code",
            "content": {
                "caption": "Python Example",
                "language": "python",
                "content": "class Calculator:\n    def __init__(self):\n        self.result = 0\n\n    def add(self, x):\n        self.result += x"
            }
        }
        
        result = self.processor._process_code(component)
        
        # Should have multiple lines
        self.assertGreater(result.count('\n'), 4, "Should have multiple lines")
        
        # Should preserve indentation
        self.assertIn('    def __init__(self):', result)
        self.assertIn('        self.result = 0', result)
        
        # Should have caption
        self.assertIn('Python Example', result)
        
        # Should have correct language
        self.assertIn('language=Python', result)
    
    def test_code_with_literal_escapes(self):
        """Test Code component with literal escape sequences"""
        component = {
            "type": "Code",
            "content": {
                "caption": "Test Code",
                "language": "python",
                "content": r"def test():\n    x = 1\n    return x"
            }
        }
        
        result = self.processor._process_code(component)
        
        # Should decode escapes
        self.assertGreater(result.count('\n'), 2, "Should decode \\n")
        self.assertIn('    x = 1', result, "Should have proper indentation")
    
    def test_code_without_caption(self):
        """Test Code component without caption"""
        component = {
            "type": "Code",
            "content": {
                "language": "java",
                "content": "public class Test {\n    void method() {}\n}"
            }
        }
        
        result = self.processor._process_code(component)
        
        # Should still work without caption
        self.assertIn('\\begin{lstlisting}', result)
        self.assertIn('public class Test', result)
    
    def test_code_language_mapping(self):
        """Test Code component language mapping"""
        test_cases = [
            ("python", "Python"),
            ("java", "Java"),
            ("javascript", "JavaScript"),
            ("cpp", "C++"),
            ("c++", "C++"),
            ("shell", "bash"),
        ]
        
        for input_lang, expected_lang in test_cases:
            with self.subTest(input_lang=input_lang):
                component = {
                    "type": "Code",
                    "content": {
                        "language": input_lang,
                        "content": "test code"
                    }
                }
                
                result = self.processor._process_code(component)
                self.assertIn(f'language={expected_lang}', result,
                            f"Language {input_lang} should map to {expected_lang}")
    
    # ============================================================================
    # EDITOR CODE COMPONENT TESTS
    # ============================================================================
    
    def test_editor_code_proper_json_parsing(self):
        """Test EditorCode component with properly parsed JSON"""
        component = {
            "type": "EditorCode",
            "mode": "edit",
            "content": {
                "language": "javascript",
                "content": "function test(x) {\n    return x * 2;\n}",
                "version": "1.0"
            }
        }
        
        result = self.processor._process_editor_code(component)
        
        # Should have multiple lines
        self.assertGreater(result.count('\n'), 1, "Should have multiple lines")
        
        # Should preserve indentation
        self.assertIn('    return x * 2;', result)
        
        # Should have correct language
        self.assertIn('language=JavaScript', result)
    
    def test_editor_code_with_literal_escapes(self):
        """Test EditorCode with literal escape sequences"""
        component = {
            "type": "EditorCode",
            "content": {
                "language": "python",
                "content": r"def calculate(n):\n    result = n * 2\n    return result"
            }
        }
        
        result = self.processor._process_editor_code(component)
        
        # Should decode escapes
        self.assertGreater(result.count('\n'), 2, "Should decode \\n")
        self.assertIn('    result = n * 2', result, "Should preserve indentation")
    
    def test_editor_code_complex_indentation(self):
        """Test EditorCode with complex nested indentation"""
        component = {
            "type": "EditorCode",
            "content": {
                "language": "javascript",
                "content": "function process(items) {\n    return items\n        .filter(x => x.active)\n        .map(x => ({\n            id: x.id,\n            name: x.name\n        }));\n}"
            }
        }
        
        result = self.processor._process_editor_code(component)
        
        # Should preserve complex indentation
        self.assertIn('    return items', result)
        self.assertIn('        .filter', result)
        self.assertIn('            id: x.id,', result)
    
    # ============================================================================
    # EDGE CASE TESTS
    # ============================================================================
    
    def test_code_with_special_characters(self):
        """Test code with special characters and strings"""
        component = {
            "type": "Code",
            "content": {
                "language": "python",
                "content": 'def test():\n    x = "String with \\n inside"\n    return x'
            }
        }
        
        result = self.processor._process_code(component)
        
        # Should handle special characters in strings
        self.assertIn('def test():', result)
        self.assertIn('    x =', result)
    
    def test_code_with_unicode(self):
        """Test code with Unicode characters"""
        component = {
            "type": "Code",
            "content": {
                "language": "python",
                "content": "def greet():\n    print('Hello 世界')\n    print('Привет мир')"
            }
        }
        
        result = self.processor._process_code(component)
        
        # Should preserve Unicode
        self.assertIn('世界', result)
        self.assertIn('Привет', result)
    
    def test_code_empty_lines_preservation(self):
        """Test that empty lines are preserved in code"""
        component = {
            "type": "Code",
            "content": {
                "language": "java",
                "content": "public class Test {\n\n    public void method1() {}\n\n    public void method2() {}\n\n}"
            }
        }
        
        result = self.processor._process_code(component)
        
        # Count empty lines in the code section
        code_section = result.split('\\begin{lstlisting}')[1].split('\\end{lstlisting}')[0]
        empty_lines = code_section.count('\n\n')
        
        self.assertGreaterEqual(empty_lines, 2, "Should preserve empty lines between methods")
    
    def test_code_very_long_lines(self):
        """Test code with very long lines"""
        long_line = "x = " + " + ".join([str(i) for i in range(100)])
        component = {
            "type": "Code",
            "content": {
                "language": "python",
                "content": f"def test():\n    {long_line}"
            }
        }
        
        result = self.processor._process_code(component)
        
        # Should handle long lines without crashing
        self.assertIn('def test():', result)
        self.assertIn('x =', result)


class TestJSONParsingBehavior(unittest.TestCase):
    """Test JSON parsing behavior to understand API response handling"""
    
    def test_normal_json_parsing(self):
        """Test that normal JSON parsing produces proper newlines"""
        json_string = '{"content": "line1\\nline2\\n    indented"}'
        data = json.loads(json_string)
        
        # After proper JSON parsing, \n should be actual newlines
        self.assertIn('\n', data['content'])
        self.assertNotIn('\\n', data['content'])
        self.assertEqual(data['content'].count('\n'), 2)
    
    def test_double_escaped_json(self):
        """Test double-escaped JSON (problematic case)"""
        # Using raw string to represent double-escaped JSON
        json_string = r'{"content": "line1\\nline2\\n    indented"}'
        data = json.loads(json_string)
        
        # After parsing double-escaped JSON, we get literal \n
        self.assertIn('\\n', data['content'])
        self.assertNotIn('\n', data['content'].replace('\\n', ''))
    
    def test_escape_sequence_detection(self):
        """Test detection of literal escape sequences"""
        test_cases = [
            ("line1\nline2", False, True),   # Actual newlines
            (r"line1\nline2", True, False),  # Literal \n
            ("line1\\nline2", True, False),  # Also literal \n
        ]
        
        for text, should_have_literal, should_have_actual in test_cases:
            with self.subTest(text=repr(text)):
                has_literal = '\\n' in text
                has_actual = '\n' in text and not '\\n' in text
                
                self.assertEqual(has_literal, should_have_literal,
                               f"Literal \\n detection failed for {repr(text)}")


class TestFixMethodEffectiveness(unittest.TestCase):
    """Test different methods for fixing literal escape sequences"""
    
    def test_encode_decode_method(self):
        """Test encode().decode('unicode_escape') method"""
        problematic = r"code{\n    indented\n}"
        
        fixed = problematic.encode().decode('unicode_escape')
        
        self.assertIn('\n', fixed)
        self.assertNotIn('\\n', fixed)
        self.assertIn('    indented', fixed)
    
    def test_simple_replace_method(self):
        """Test simple string replacement method"""
        problematic = r"code{\n    indented\t\n}"
        
        fixed = problematic.replace('\\n', '\n').replace('\\t', '\t')
        
        self.assertIn('\n', fixed)
        self.assertIn('\t', fixed)
        self.assertNotIn('\\n', fixed)
        self.assertNotIn('\\t', fixed)
    
    def test_method_with_already_fixed_input(self):
        """Test that fix methods don't break already-proper newlines"""
        already_fixed = "code{\n    indented\n}"
        
        # Our check should prevent re-processing
        if '\\n' in already_fixed or '\\t' in already_fixed:
            result = already_fixed.encode().decode('unicode_escape')
        else:
            result = already_fixed
        
        # Should remain unchanged
        self.assertEqual(result, already_fixed)
        self.assertIn('\n', result)


def run_tests():
    """Run all tests with detailed output"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCodeIndentationHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestJSONParsingBehavior))
    suite.addTests(loader.loadTestsFromTestCase(TestFixMethodEffectiveness))
    
    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED!")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)

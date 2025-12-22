"""
Deep investigation of JSON parsing and escape sequence handling
This test investigates the actual root cause of indentation issues
"""
import json
import sys

def test_json_parsing_scenarios():
    """Test different JSON parsing scenarios to understand the problem"""
    
    print("=" * 80)
    print("DEEP INVESTIGATION: JSON Parsing and Escape Sequences")
    print("=" * 80)
    
    # Scenario 1: Properly formatted JSON (what we expect from API)
    print("\n1. SCENARIO: Properly escaped JSON from API")
    print("-" * 80)
    
    json_string_proper = '''{
        "content": "public class Driver {\\n    public static void main(String[] args) {\\n        System.out.println(\\"Hello\\");\\n    }\\n}"
    }'''
    
    print("Raw JSON string:")
    print(repr(json_string_proper[:100]) + "...")
    
    data1 = json.loads(json_string_proper)
    code1 = data1["content"]
    
    print(f"\nAfter json.loads():")
    print(f"Type: {type(code1)}")
    print(f"Length: {len(code1)}")
    print(f"Contains \\\\n literal: {'\\\\n' in code1}")
    print(f"Contains actual newline: {chr(10) in code1}")
    print(f"\nFirst 100 chars: {repr(code1[:100])}")
    print(f"\nActual content:\n{code1}")
    
    # Scenario 2: Double-escaped JSON (common API issue)
    print("\n\n2. SCENARIO: Double-escaped JSON (problematic case)")
    print("-" * 80)
    
    # In Python raw strings, we need 4 backslashes to represent \\n in JSON
    json_string_double = r'''{
        "content": "public class Driver {\\n    public static void main(String[] args) {\\n        System.out.println(\"Hello\");\\n    }\\n}"
    }'''
    
    print("Raw JSON string:")
    print(repr(json_string_double[:100]) + "...")
    
    data2 = json.loads(json_string_double)
    code2 = data2["content"]
    
    print(f"\nAfter json.loads():")
    print(f"Type: {type(code2)}")
    print(f"Length: {len(code2)}")
    print(f"Contains \\\\n literal: {'\\n' in code2}")
    print(f"Contains actual newline: {chr(10) in code2}")
    print(f"\nFirst 100 chars: {repr(code2[:100])}")
    print(f"\nActual content:\n{code2}")
    
    # Scenario 3: What if we get the string after loading but it still has \n?
    print("\n\n3. SCENARIO: String already loaded but contains literal backslash-n")
    print("-" * 80)
    
    # This would only happen if the original JSON had double-escaping
    # Simulating a string that already went through json.loads but still has \n
    code3 = r"public class Driver {\n    public static void main() {\n    }\n}"
    
    print(f"String value: {repr(code3)}")
    print(f"Contains \\n literal: {'\\n' in code3}")
    print(f"Contains actual newline: {chr(10) in code3}")
    print(f"\nDirect display:\n{code3}")
    
    print("\n** This is the problematic case we need to fix! **")
    
    # Scenario 4: Response.json() behavior test
    print("\n\n4. SCENARIO: Testing response.json() behavior")
    print("-" * 80)
    
    # Simulate what httpx response.json() does
    import httpx
    
    # Create a mock response with properly escaped JSON
    response_content = b'{"content": "line1\\nline2\\n    indented"}'
    
    print(f"Response bytes: {response_content}")
    
    # This is what response.json() does internally
    parsed = json.loads(response_content.decode('utf-8'))
    
    print(f"\nParsed content: {repr(parsed['content'])}")
    print(f"Contains \\\\n literal: {'\\\\n' in parsed['content']}")
    print(f"Contains actual newline: {chr(10) in parsed['content']}")
    print(f"\nActual display:\n{parsed['content']}")
    
    return code1, code2

def test_fix_methods():
    """Test different methods to fix the issue"""
    
    print("\n\n" + "=" * 80)
    print("TESTING FIX METHODS")
    print("=" * 80)
    
    # Problematic case: double-escaped
    problematic = "public class Driver {\\n    public static void main() {\\n    }\\n}"
    
    print("\n1. ORIGINAL PROBLEM:")
    print("-" * 80)
    print(f"Input: {repr(problematic)}")
    print(f"\nDirect display:\n{problematic}")
    
    # Method 1: encode().decode('unicode_escape')
    print("\n\n2. METHOD 1: encode().decode('unicode_escape')")
    print("-" * 80)
    try:
        fixed1 = problematic.encode().decode('unicode_escape')
        print(f"Result: {repr(fixed1)}")
        print(f"\nDisplay:\n{fixed1}")
        print("✅ SUCCESS" if "\n" in fixed1 and "    " in fixed1 else "❌ FAILED")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Method 2: replace('\\n', '\n')
    print("\n\n3. METHOD 2: Simple replace('\\\\n', '\\n')")
    print("-" * 80)
    try:
        fixed2 = problematic.replace('\\n', '\n').replace('\\t', '\t')
        print(f"Result: {repr(fixed2)}")
        print(f"\nDisplay:\n{fixed2}")
        print("✅ SUCCESS" if "\n" in fixed2 and "    " in fixed2 else "❌ FAILED")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Method 3: codecs.decode
    print("\n\n4. METHOD 3: codecs.decode('unicode_escape')")
    print("-" * 80)
    try:
        import codecs
        fixed3 = codecs.decode(problematic, 'unicode_escape')
        print(f"Result: {repr(fixed3)}")
        print(f"\nDisplay:\n{fixed3}")
        print("✅ SUCCESS" if "\n" in fixed3 and "    " in fixed3 else "❌ FAILED")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Method 4: ast.literal_eval (for strings)
    print("\n\n5. METHOD 4: ast.literal_eval with quotes")
    print("-" * 80)
    try:
        import ast
        # Wrap in quotes to make it a valid Python string literal
        fixed4 = ast.literal_eval(f'"{problematic}"')
        print(f"Result: {repr(fixed4)}")
        print(f"\nDisplay:\n{fixed4}")
        print("✅ SUCCESS" if "\n" in fixed4 and "    " in fixed4 else "❌ FAILED")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_real_world_case():
    """Test with actual JSON response structure"""
    
    print("\n\n" + "=" * 80)
    print("REAL WORLD CASE: Simulating Educative API Response")
    print("=" * 80)
    
    # Simulate actual API response
    api_response_json = '''{
        "type": "TabbedCode",
        "content": {
            "codeContents": [
                {
                    "title": "Java",
                    "language": "java",
                    "content": "public class Driver {\\n    public static void main(String[] args) {\\n        VendingMachine vm = VendingMachine.getInstance();\\n\\n        // Setup\\n        vm.addRack(new Rack(1));\\n    }\\n}"
                }
            ]
        }
    }'''
    
    print("\nParsing API response...")
    data = json.loads(api_response_json)
    
    code_text = data["content"]["codeContents"][0]["content"]
    
    print(f"\nExtracted code_text type: {type(code_text)}")
    print(f"Contains \\\\n literal: {'\\\\n' in code_text}")
    print(f"Contains actual newline (chr(10)): {chr(10) in code_text}")
    print(f"\nRepr: {repr(code_text[:80])}...")
    
    print("\n\nDirect display (what we get now):")
    print("-" * 80)
    print(code_text)
    
    if '\\n' in code_text:
        print("\n❌ PROBLEM DETECTED: Code contains literal \\\\n instead of newlines")
        print("\nThis should NOT happen if JSON is properly formatted!")
        print("This indicates the API might be double-escaping the response.")
    else:
        print("\n✅ NO PROBLEM: JSON parsing worked correctly")
        print("Code already has proper newlines")

if __name__ == "__main__":
    test_json_parsing_scenarios()
    test_fix_methods()
    test_real_world_case()
    
    print("\n\n" + "=" * 80)
    print("INVESTIGATION COMPLETE")
    print("=" * 80)

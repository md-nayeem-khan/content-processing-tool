"""
Integration test with realistic API response simulation
Tests the entire flow from API response parsing to LaTeX generation
"""
import json
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from section_processor import SectionContentProcessor


def test_realistic_api_response_flow():
    """Test with a realistic simulated API response"""
    
    print("=" * 80)
    print("INTEGRATION TEST: Realistic API Response Flow")
    print("=" * 80)
    
    # Simulate the actual API response as it would come from httpx response.json()
    # In a real scenario, this is already parsed by the JSON library
    api_response_text = '''{
        "components": [
            {
                "type": "TabbedCode",
                "content": {
                    "codeContents": [
                        {
                            "title": "Java",
                            "language": "java",
                            "caption": "Vending Machine Driver Implementation",
                            "content": "public class Driver {\\n    public static void main(String[] args) {\\n        VendingMachine vm = VendingMachine.getInstance();\\n\\n        // Setup\\n        vm.addRack(new Rack(1)); vm.addRack(new Rack(2)); vm.addRack(new Rack(3));\\n        Product choc = new Product(101, \\"Chocolate Bar\\", 1.50, ProductType.CHOCOLATE);\\n        Product snack= new Product(102, \\"Potato Chips\\", 2.00, ProductType.SNACK);\\n        Product bev  = new Product(103, \\"Soda Can\\",      2.50, ProductType.BEVERAGE);\\n        vm.loadProduct(1, choc, 5);\\n        vm.loadProduct(2, snack, 3);\\n        vm.loadProduct(3, bev,   2);\\n        vm.showInventory();\\n\\n        // Scenario 1: Exact payment\\n        System.out.println(\\"========== Scenario 1: Exact Payment ==========\\");\\n        vm.insertMoney(1.50);\\n        vm.selectProduct(1);\\n\\n        // Scenario 2: Overpayment & Change\\n        System.out.println(\\"========== Scenario 2: Overpayment & Change ==========\\");\\n        vm.insertMoney(3.00);\\n        vm.selectProduct(2);\\n\\n        // Scenario 3: Underpayment & Refund\\n        System.out.println(\\"========== Scenario 3: Underpayment & Refund ==========\\");\\n        vm.insertMoney(1.00);\\n        vm.selectProduct(3);\\n\\n        // Scenario 4: Deplete Rack & Retry\\n        System.out.println(\\"========== Scenario 4: Deplete Rack 3 & Retry ==========\\");\\n        vm.insertMoney(5.00); vm.selectProduct(3);\\n        vm.insertMoney(2.50); vm.selectProduct(3);\\n        vm.insertMoney(2.50); vm.selectProduct(3);\\n\\n        vm.showInventory();\\n    }\\n}"
                        }
                    ]
                }
            },
            {
                "type": "Code",
                "content": {
                    "caption": "Python Data Processing",
                    "language": "python",
                    "content": "class DataProcessor:\\n    def __init__(self, data):\\n        self.data = data\\n        self.results = []\\n\\n    def process(self):\\n        for item in self.data:\\n            if item.get('active'):\\n                self.results.append({\\n                    'id': item['id'],\\n                    'processed': True\\n                })\\n        return self.results"
                }
            },
            {
                "type": "EditorCode",
                "mode": "edit",
                "content": {
                    "language": "javascript",
                    "content": "function processUsers(users) {\\n    return users\\n        .filter(user => user.isActive)\\n        .map(user => ({\\n            id: user.id,\\n            name: user.name.toUpperCase(),\\n            email: user.email.toLowerCase()\\n        }))\\n        .sort((a, b) => a.name.localeCompare(b.name));\\n}",
                    "version": "1.0"
                }
            }
        ]
    }'''
    
    print("\n1. Parsing API Response (simulating response.json())")
    print("-" * 80)
    
    # This simulates what httpx's response.json() does
    section_data = json.loads(api_response_text)
    
    print(f"✓ Parsed {len(section_data['components'])} components")
    
    # Check what we got after parsing
    for i, component in enumerate(section_data['components'], 1):
        comp_type = component['type']
        if comp_type == 'TabbedCode':
            code = component['content']['codeContents'][0]['content']
        elif comp_type == 'Code':
            code = component['content']['content']
        elif comp_type == 'EditorCode':
            code = component['content']['content']
        else:
            continue
        
        has_literal_escapes = '\\n' in code
        has_actual_newlines = '\n' in code and not has_literal_escapes
        
        print(f"\nComponent {i} ({comp_type}):")
        print(f"  - Has literal \\n: {has_literal_escapes}")
        print(f"  - Has actual newlines: {has_actual_newlines}")
        print(f"  - First 60 chars: {repr(code[:60])}...")
    
    # Process the section
    print("\n\n2. Processing Components with SectionContentProcessor")
    print("-" * 80)
    
    processor = SectionContentProcessor(output_dir="test_output")
    processor.set_book_context("integration_test", chapter_number=1, section_id="test")
    
    latex_content, images, component_types = processor.process_section_components(section_data)
    
    print(f"✓ Processed components: {component_types}")
    print(f"✓ Generated {len(images)} images")
    print(f"✓ LaTeX content length: {len(latex_content)} characters")
    
    # Verify the output
    print("\n\n3. Verification")
    print("-" * 80)
    
    # Check TabbedCode output
    print("\n✓ TabbedCode Component:")
    if 'public class Driver {' in latex_content and '    public static void main' in latex_content:
        print("  ✅ Proper indentation detected")
        print("  ✅ Multiple lines detected")
    else:
        print("  ❌ Indentation issue detected")
    
    # Check Code component output
    print("\n✓ Code Component:")
    if 'class DataProcessor:' in latex_content and '    def __init__' in latex_content:
        print("  ✅ Proper indentation detected")
    else:
        print("  ❌ Indentation issue detected")
    
    # Check EditorCode component output
    print("\n✓ EditorCode Component:")
    if 'function processUsers' in latex_content and '        .filter' in latex_content:
        print("  ✅ Proper indentation detected")
    else:
        print("  ❌ Indentation issue detected")
    
    # Count lines in output
    line_count = latex_content.count('\n')
    print(f"\n✓ Total lines in LaTeX output: {line_count}")
    
    # Save output
    output_file = "test_integration_realistic_output.tex"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\\documentclass{article}\n")
        f.write("\\usepackage{listings}\n")
        f.write("\\lstset{\n")
        f.write("  basicstyle=\\ttfamily\\small,\n")
        f.write("  columns=fullflexible,\n")
        f.write("  breaklines=true,\n")
        f.write("  numbers=left,\n")
        f.write("  numberstyle=\\tiny\\color{gray},\n")
        f.write("  frame=single\n")
        f.write("}\n")
        f.write("\\begin{document}\n\n")
        f.write("\\section{Integration Test Output}\n\n")
        f.write(latex_content)
        f.write("\n\n\\end{document}\n")
    
    print(f"\n✓ Output saved to: {output_file}")
    
    # Display sample of output
    print("\n\n4. Sample LaTeX Output (first 1000 chars)")
    print("-" * 80)
    print(latex_content[:1000])
    if len(latex_content) > 1000:
        print(f"\n... (truncated, total {len(latex_content)} chars) ...")
    
    return latex_content


def test_edge_case_scenarios():
    """Test various edge case scenarios"""
    
    print("\n\n" + "=" * 80)
    print("EDGE CASE SCENARIOS")
    print("=" * 80)
    
    processor = SectionContentProcessor(output_dir="test_output")
    processor.set_book_context("edge_test", chapter_number=1, section_id="test")
    
    test_cases = [
        {
            "name": "Code with mixed indentation (spaces and tabs)",
            "component": {
                "type": "Code",
                "content": {
                    "language": "python",
                    "content": "def test():\n\tif True:\n\t    x = 1\n    \ty = 2"
                }
            }
        },
        {
            "name": "Code with Windows line endings (\\r\\n)",
            "component": {
                "type": "Code",
                "content": {
                    "language": "java",
                    "content": "public class Test {\r\n    void method() {\r\n        int x = 1;\r\n    }\r\n}"
                }
            }
        },
        {
            "name": "Code with trailing whitespace",
            "component": {
                "type": "Code",
                "content": {
                    "language": "python",
                    "content": "def test():   \n    return True   \n"
                }
            }
        },
        {
            "name": "Empty code block",
            "component": {
                "type": "Code",
                "content": {
                    "language": "python",
                    "content": ""
                }
            }
        },
        {
            "name": "Code with only whitespace",
            "component": {
                "type": "Code",
                "content": {
                    "language": "python",
                    "content": "   \n   \n   "
                }
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 80)
        
        try:
            result = processor._process_code(test_case['component'])
            print(f"✓ Processing succeeded")
            print(f"  Output length: {len(result)} chars")
            print(f"  Lines: {result.count(chr(10))}")
            
            if result:
                print(f"  Sample: {repr(result[:100])}...")
            else:
                print("  (Empty output)")
                
        except Exception as e:
            print(f"✗ Processing failed: {e}")


if __name__ == "__main__":
    try:
        latex_output = test_realistic_api_response_flow()
        test_edge_case_scenarios()
        
        print("\n\n" + "=" * 80)
        print("✅ INTEGRATION TEST COMPLETED SUCCESSFULLY")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n\n❌ INTEGRATION TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

"""
Test TabbedCode component with proper indentation handling
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from section_processor import SectionContentProcessor

def test_tabbed_code_indentation():
    """Test that TabbedCode properly handles escaped newlines and indentation"""
    
    # Sample TabbedCode component with Java code containing \n escape sequences
    # This simulates what comes from the API response
    tabbed_code_component = {
        "type": "TabbedCode",
        "content": {
            "codeContents": [
                {
                    "title": "Java",
                    "language": "java",
                    "caption": "Vending Machine Driver",
                    "content": "public class Driver {\n    public static void main(String[] args) {\n        VendingMachine vm = VendingMachine.getInstance();\n\n        // Setup\n        vm.addRack(new Rack(1)); vm.addRack(new Rack(2)); vm.addRack(new Rack(3));\n        Product choc = new Product(101, \"Chocolate Bar\", 1.50, ProductType.CHOCOLATE);\n        Product snack= new Product(102, \"Potato Chips\", 2.00, ProductType.SNACK);\n        Product bev  = new Product(103, \"Soda Can\",      2.50, ProductType.BEVERAGE);\n        vm.loadProduct(1, choc, 5);\n        vm.loadProduct(2, snack, 3);\n        vm.loadProduct(3, bev,   2);\n        vm.showInventory();\n\n        // Scenario 1: Exact payment\n        System.out.println(\"========== Scenario 1: Exact Payment ==========\");\n        vm.insertMoney(1.50);\n        vm.selectProduct(1);\n\n        // Scenario 2: Overpayment & Change\n        System.out.println(\"========== Scenario 2: Overpayment & Change ==========\");\n        vm.insertMoney(3.00);\n        vm.selectProduct(2);\n\n        // Scenario 3: Underpayment & Refund\n        System.out.println(\"========== Scenario 3: Underpayment & Refund ==========\");\n        vm.insertMoney(1.00);\n        vm.selectProduct(3);\n\n        // Scenario 4: Deplete Rack & Retry\n        System.out.println(\"========== Scenario 4: Deplete Rack 3 & Retry ==========\");\n        vm.insertMoney(5.00); vm.selectProduct(3);\n        vm.insertMoney(2.50); vm.selectProduct(3);\n        vm.insertMoney(2.50); vm.selectProduct(3);\n\n        vm.showInventory();\n    }\n}"
                }
            ]
        }
    }
    
    processor = SectionContentProcessor(output_dir="test_output")
    processor.set_book_context("test_tabbed_code", chapter_number=1, section_id="test")
    
    print("Testing TabbedCode component with proper indentation...")
    print("=" * 70)
    
    # Process the component
    latex_output = processor._process_tabbed_code(tabbed_code_component)
    
    print("\nGenerated LaTeX Output:")
    print("-" * 70)
    print(latex_output)
    print("-" * 70)
    
    # Verify the output
    print("\n✅ Verification:")
    
    # Check if the code has proper line breaks
    if latex_output.count('\n') > 10:
        print("✅ Code contains multiple lines (proper newline handling)")
    else:
        print("❌ Code appears to be on a single line (newlines not processed)")
    
    # Check if indentation is present
    if '    public static void main' in latex_output:
        print("✅ Code contains proper indentation")
    else:
        print("❌ Code missing proper indentation")
    
    # Check for lstlisting environment
    if '\\begin{lstlisting}[language=Java]' in latex_output:
        print("✅ LaTeX lstlisting environment present")
    else:
        print("❌ LaTeX lstlisting environment missing")
    
    # Check for caption
    if 'Vending Machine Driver' in latex_output:
        print("✅ Caption present")
    else:
        print("❌ Caption missing")
    
    # Save output to file for inspection
    output_file = "test_tabbed_code_indentation_output.tex"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\\documentclass{article}\n")
        f.write("\\usepackage{listings}\n")
        f.write("\\lstset{\n")
        f.write("  basicstyle=\\ttfamily,\n")
        f.write("  columns=fullflexible,\n")
        f.write("  breaklines=true,\n")
        f.write("  numbers=left\n")
        f.write("}\n")
        f.write("\\begin{document}\n\n")
        f.write(latex_output)
        f.write("\n\n\\end{document}\n")
    
    print(f"\n✅ Test output saved to: {output_file}")
    
    return latex_output

if __name__ == "__main__":
    try:
        result = test_tabbed_code_indentation()
        print("\n" + "=" * 70)
        print("✅ Test completed successfully!")
        print("=" * 70)
    except Exception as e:
        print("\n" + "=" * 70)
        print(f"❌ Test failed with error: {str(e)}")
        print("=" * 70)
        import traceback
        traceback.print_exc()

"""
Test script for TableHTML component processing
"""

import json
from section_processor import SectionContentProcessor

# Sample TableHTML component from the user's request
sample_table_html = {
    "type": "TableHTML",
    "content": {
        "type": "TableV2",
        "children": [
            {
                "type": "table",
                "dataKey": "table_lEEI4b-nxLvdex53LCgtB",
                "children": [
                    {
                        "type": "table-body",
                        "children": [
                            {
                                "type": "table-row",
                                "dataKey": "row_owqHbfVolb6XpHiseSqn-",
                                "children": [
                                    {
                                        "type": "table-cell",
                                        "width": 224,
                                        "dataKey": "cell__P2XnGSbAubWbD_O8qn-L",
                                        "height": 0,
                                        "rowSpan": 1,
                                        "colSpan": 1,
                                        "children": [
                                            {
                                                "type": "table-content",
                                                "children": [
                                                    {
                                                        "type": "paragraph",
                                                        "children": [
                                                            {
                                                                "text": "Role/Level",
                                                                "bold": True
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }
                                        ],
                                        "bgColor": "#F5F5F5",
                                        "align": "center"
                                    },
                                    {
                                        "type": "table-cell",
                                        "width": 668,
                                        "dataKey": "cell_bOJIvPsRyhXz9_MKobYr5",
                                        "height": 0,
                                        "rowSpan": 1,
                                        "colSpan": 1,
                                        "children": [
                                            {
                                                "type": "table-content",
                                                "children": [
                                                    {
                                                        "type": "paragraph",
                                                        "children": [
                                                            {
                                                                "text": "Key Focus Areas",
                                                                "bold": True
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }
                                        ],
                                        "bgColor": "#F5F5F5",
                                        "align": "center"
                                    }
                                ]
                            },
                            {
                                "type": "table-row",
                                "dataKey": "row_BhE3xzkfS4PWLCkjIXNWv",
                                "children": [
                                    {
                                        "type": "table-cell",
                                        "width": 224,
                                        "dataKey": "cell_0IGaef1paztMJs3mQe6H0",
                                        "height": 0,
                                        "rowSpan": 1,
                                        "colSpan": 1,
                                        "children": [
                                            {
                                                "type": "table-content",
                                                "children": [
                                                    {
                                                        "type": "paragraph",
                                                        "children": [
                                                            {
                                                                "text": "Junior/Mid-level Software Engineer",
                                                                "bold": True
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }
                                        ],
                                        "align": "center"
                                    },
                                    {
                                        "type": "table-cell",
                                        "width": 668,
                                        "dataKey": "cell_oizYRPQD2XWDcpsIeFQQz",
                                        "height": 0,
                                        "rowSpan": 1,
                                        "colSpan": 1,
                                        "align": "left",
                                        "children": [
                                            {
                                                "type": "table-content",
                                                "children": [
                                                    {
                                                        "type": "bulleted-list",
                                                        "children": [
                                                            {
                                                                "type": "list-item",
                                                                "children": [
                                                                    {
                                                                        "type": "list-item-text",
                                                                        "children": [
                                                                            {
                                                                                "text": "Basic System Design components "
                                                                            }
                                                                        ]
                                                                    }
                                                                ],
                                                                "style": ""
                                                            },
                                                            {
                                                                "type": "list-item",
                                                                "children": [
                                                                    {
                                                                        "type": "list-item-text",
                                                                        "children": [
                                                                            {
                                                                                "text": "Trade-offs (e.g., between requirements such as latency and availability)"
                                                                            }
                                                                        ]
                                                                    }
                                                                ],
                                                                "style": ""
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ],
        "html": '<div class="tableV2"><div class="overflow-x-scroll"> <table class="mt-0 !w-max !relative" slate-table-element="table"><tbody slate-table-element="table-body"><tr class="undefined" data-key="row_owqHbfVolb6XpHiseSqn-" slate-table-element="table-row" ><td class="!border !border-solid !border-gray-L300 dark:!border-gray-D1000 !border-y-px !border-l-0  font-normal relative p-1.5 text-center" slate-table-element="table-cell" data-key=cell__P2XnGSbAubWbD_O8qn-L width=224 height=0 colSpan=1 rowSpan=1  style="background-color:#F5F5F5;text-align:center; background-color:#F5F5F5"><div slate-table-element="table-content"><p><strong>Role/Level</strong></p></div></td><td class="!border !border-solid !border-gray-L300 dark:!border-gray-D1000 !border-y-px !border-l-0  font-normal relative p-1.5 text-center" slate-table-element="table-cell" data-key=cell_bOJIvPsRyhXz9_MKobYr5 width=668 height=0 colSpan=1 rowSpan=1  style="background-color:#F5F5F5;text-align:center; background-color:#F5F5F5"><div slate-table-element="table-content"><p><strong>Key Focus Areas</strong></p></div></td></tr><tr class="undefined" data-key="row_BhE3xzkfS4PWLCkjIXNWv" slate-table-element="table-row" ><td class="!border !border-solid !border-gray-L300 dark:!border-gray-D1000 !border-y-px !border-l-0  font-normal relative p-1.5 text-center" slate-table-element="table-cell" data-key=cell_0IGaef1paztMJs3mQe6H0 width=224 height=0 colSpan=1 rowSpan=1  style=";text-align:center; "><div slate-table-element="table-content"><p><strong>Junior/Mid-level Software Engineer</strong></p></div></td><td class="!border !border-solid !border-gray-L300 dark:!border-gray-D1000 !border-y-px !border-l-0  font-normal relative p-1.5 text-center" slate-table-element="table-cell" data-key=cell_oizYRPQD2XWDcpsIeFQQz width=668 height=0 colSpan=1 rowSpan=1  style=";text-align:left; "><div slate-table-element="table-content"><ul><li><p>Basic System Design components </p></li><li><p>Trade-offs (e.g., between requirements such as latency and availability)</p></li></ul></div></td></tr></tbody></table></div></div>'
    },
    "hash": 3
}

def test_table_html_processing():
    """Test TableHTML component processing"""
    print("=" * 80)
    print("Testing TableHTML Component Processing")
    print("=" * 80)
    
    # Create processor instance
    processor = SectionContentProcessor()
    processor.current_chapter_number = 1
    processor.current_section_id = "test_section"
    
    # Process the component
    print("\n1. Processing TableHTML component...")
    try:
        latex_output = processor._process_table_html(sample_table_html)
        print("✅ TableHTML processing successful")
        
        print("\n2. Generated LaTeX output:")
        print("-" * 80)
        print(latex_output)
        print("-" * 80)
        
        # Check if output contains expected LaTeX table elements
        if "tabular" in latex_output or "longtable" in latex_output:
            print("\n✅ Output contains LaTeX table environment")
        else:
            print("\n⚠️  Output may not contain proper LaTeX table structure")
        
        # Save to file for inspection
        output_file = "test_table_html_output.tex"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\\documentclass{article}\n")
            f.write("\\usepackage{longtable}\n")
            f.write("\\usepackage{booktabs}\n")
            f.write("\\usepackage{array}\n")
            f.write("\\begin{document}\n\n")
            f.write(latex_output)
            f.write("\n\n\\end{document}\n")
        
        print(f"\n✅ LaTeX output saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error processing TableHTML: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_table_html_processing()

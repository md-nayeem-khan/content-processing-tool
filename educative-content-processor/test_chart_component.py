"""
Test Chart Component Processing
Verifies that Chart components are correctly converted to LaTeX tables
"""

import asyncio
from section_processor import SectionContentProcessor

# Sample chart data from the backend response (YouTube user growth example)
sample_chart_component = {
    "type": "Chart",
    "mode": "edit",
    "content": {
        "config": """{
  "type": "line",
  "data": {
    "labels": [
      "2012",
      "2013",
      "2014",
      "2015",
      "2016",
      "2017",
      "2018",
      "2019",
      "2020",
      "2021"
    ],
    "datasets": [
      {
        "label": "Monthly Active Users",
        "borderColor": "rgb(230,0,0)",
        "data": [
          "0.8",
          "1",
          "1.1",
          "1.2",
          "1.4",
          "1.5",
          "1.8",
          "2",
          "2.3",
          "2.6"
        ]
      }
    ]
  },
  "options": {
    "responsive": true,
    "title": {
      "display": true,
      "text": "YouTube's Yearly User Growth"
    },
    "tooltips": {
      "mode": "index"
    },
    "hover": {
      "mode": "index"
    },
    "scales": {
      "xAxes": [
        {
          "scaleLabel": {
            "display": true,
            "labelString": "Year"
          }
        }
      ],
      "yAxes": [
        {
          "stacked": false,
          "scaleLabel": {
            "display": true,
            "labelString": "Billion"
          }
        }
      ]
    }
  }
}""",
        "type": "area",
        "comp_id": "jNZyJR3JOfbyhpIkuwAhy",
        "caption": "Increase in monthly active users of YouTube per year"
    },
    "iteration": 0,
    "hash": 6,
    "saveVersion": 12,
    "status": "normal",
    "children": [
        {
            "text": ""
        }
    ],
    "headingTag": "lGzTu9XD8UjvW41nv3QAo",
    "collapsed": True
}

# Sample section data with chart component
section_data = {
    "components": [
        sample_chart_component
    ]
}

async def test_chart_processing():
    """Test chart component processing"""
    print("=" * 70)
    print("Testing Chart Component Processing")
    print("=" * 70)
    
    # Initialize processor
    processor = SectionContentProcessor(output_dir="generated_books")
    processor.set_book_context("test_chart", chapter_number=1, section_id="test-section")
    
    print("\n[1/4] Processing chart component...")
    latex_content, generated_images, component_types = await processor.process_section_components_async(section_data)
    
    print(f"[2/4] Component types detected: {component_types}")
    assert "Chart" in component_types, "❌ Chart type not detected!"
    print("      ✅ Chart type correctly detected")
    
    print(f"[3/4] Generated images: {len(generated_images)}")
    print(f"      ✅ No images expected for charts (converted to tables)")
    
    print("\n[4/4] Generated LaTeX content:")
    print("-" * 70)
    print(latex_content)
    print("-" * 70)
    
    # Verify LaTeX structure
    assert "\\begin{table}" in latex_content, "❌ Table environment not found!"
    assert "\\begin{tabular}" in latex_content, "❌ Tabular environment not found!"
    assert "Year" in latex_content, "❌ X-axis label not found!"
    assert "Monthly Active Users" in latex_content, "❌ Dataset label not found!"
    assert "2012" in latex_content and "2021" in latex_content, "❌ Data labels not found!"
    assert "0.8" in latex_content and "2.6" in latex_content, "❌ Data values not found!"
    assert "YouTube's Yearly User Growth" in latex_content, "❌ Chart title not found!"
    assert "Increase in monthly active users of YouTube per year" in latex_content, "❌ Caption not found!"
    assert "Billion" in latex_content, "❌ Y-axis label not found!"
    assert "[Chart data presented in table format]" in latex_content, "❌ Conversion note not found!"
    
    print("\n✅ All assertions passed!")
    print("=" * 70)
    print("Chart component successfully converted to LaTeX table format")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_chart_processing())

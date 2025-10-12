"""
Test Chart Component with LaTeX Output
Creates a standalone LaTeX file to visualize the chart table output
"""

import asyncio
from section_processor import SectionContentProcessor

# Sample chart data - YouTube user growth
youtube_chart = {
    "type": "Chart",
    "mode": "edit",
    "content": {
        "config": """{
  "type": "line",
  "data": {
    "labels": ["2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021"],
    "datasets": [
      {
        "label": "Monthly Active Users",
        "borderColor": "rgb(230,0,0)",
        "data": ["0.8", "1", "1.1", "1.2", "1.4", "1.5", "1.8", "2", "2.3", "2.6"]
      }
    ]
  },
  "options": {
    "responsive": true,
    "title": {
      "display": true,
      "text": "YouTube's Yearly User Growth"
    },
    "scales": {
      "xAxes": [{"scaleLabel": {"display": true, "labelString": "Year"}}],
      "yAxes": [{"scaleLabel": {"display": true, "labelString": "Billion"}}]
    }
  }
}""",
        "type": "area",
        "caption": "Increase in monthly active users of YouTube per year"
    }
}

# Sample chart with multiple datasets
multi_dataset_chart = {
    "type": "Chart",
    "mode": "edit",
    "content": {
        "config": """{
  "type": "bar",
  "data": {
    "labels": ["Q1", "Q2", "Q3", "Q4"],
    "datasets": [
      {
        "label": "Revenue 2023",
        "data": ["100", "120", "115", "140"]
      },
      {
        "label": "Revenue 2024",
        "data": ["110", "135", "130", "160"]
      }
    ]
  },
  "options": {
    "title": {
      "display": true,
      "text": "Quarterly Revenue Comparison"
    },
    "scales": {
      "xAxes": [{"scaleLabel": {"display": true, "labelString": "Quarter"}}],
      "yAxes": [{"scaleLabel": {"display": true, "labelString": "Million USD"}}]
    }
  }
}""",
        "type": "bar",
        "caption": "Revenue comparison between 2023 and 2024"
    }
}

# Section with multiple charts
section_data = {
    "components": [
        {
            "type": "MarkdownEditor",
            "content": {
                "text": "# Chart Examples\n\nThis section demonstrates how charts are converted to tables in LaTeX format."
            }
        },
        youtube_chart,
        {
            "type": "MarkdownEditor",
            "content": {
                "text": "The chart above shows the growth of YouTube's user base over a decade."
            }
        },
        multi_dataset_chart,
        {
            "type": "MarkdownEditor",
            "content": {
                "text": "The second chart compares revenue across multiple years."
            }
        }
    ]
}

async def generate_chart_latex():
    """Generate LaTeX file with chart examples"""
    print("Generating LaTeX file with chart examples...")
    
    # Initialize processor
    processor = SectionContentProcessor(output_dir="generated_books")
    processor.set_book_context("test_chart", chapter_number=1, section_id="chart-examples")
    
    # Process components
    latex_content, _, component_types = await processor.process_section_components_async(section_data)
    
    print(f"Component types: {component_types}")
    
    # Create complete LaTeX document
    latex_document = r"""\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{graphicx}
\usepackage{adjustbox}
\usepackage{hyperref}
\usepackage{listings}
\usepackage{xcolor}
\usepackage{amsmath}
\usepackage{geometry}
\geometry{margin=1in}

\title{Chart Component Test}
\author{Content Processing Tool}
\date{\today}

\begin{document}

\maketitle

\section*{Introduction}

This document demonstrates how Chart components from the Educative platform are converted to LaTeX table format for PDF generation.

""" + latex_content + r"""

\section*{Conclusion}

Charts are successfully converted to tabular format, preserving all data while making it suitable for PDF output.

\end{document}
"""
    
    # Write to file
    output_file = "test_chart_output.tex"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(latex_document)
    
    print(f"\n✅ LaTeX file generated: {output_file}")
    print(f"✅ Component types processed: {', '.join(component_types)}")
    print("\nTo compile the PDF, run:")
    print(f"  pdflatex {output_file}")
    
    return latex_content

if __name__ == "__main__":
    asyncio.run(generate_chart_latex())

"""
Full Integration Test for Quiz Component
Tests Quiz component alongside other components in a complete section
"""

import asyncio
from section_processor import SectionContentProcessor

# Sample section with multiple components including Quiz
section_data = {
    "components": [
        {
            "type": "SlateHTML",
            "content": {
                "html": "<h2>Database Selection Guide</h2><p>This section covers how to choose the right database for your application.</p>"
            }
        },
        {
            "type": "MarkdownEditor",
            "content": {
                "text": "## Key Considerations\n\nWhen selecting a database, consider:\n\n- **Data structure**: Structured vs unstructured\n- **Consistency requirements**: ACID vs eventual consistency\n- **Scale**: Read/write patterns and volume\n- **Performance**: Latency and throughput needs"
            }
        },
        {
            "type": "Quiz",
            "content": {
                "questions": [
                    {
                        "questionText": "Which database should we use when we have unstructured data and there's a need for high performance?",
                        "questionOptions": [
                            {
                                "text": "MongoDB",
                                "id": "opt1",
                                "correct": True,
                                "explanation": {
                                    "mdText": "MongoDB is a database that stores unstructured data and provides high performance in data-relevant operations.",
                                    "mdHtml": "<p>MongoDB is a database that stores unstructured data and provides high performance in data-relevant operations.</p>\n"
                                },
                                "mdHtml": "<p>MongoDB</p>\n"
                            },
                            {
                                "text": "MySQL",
                                "id": "opt2",
                                "correct": False,
                                "explanation": {
                                    "mdText": "",
                                    "mdHtml": ""
                                },
                                "mdHtml": "<p>MySQL</p>\n"
                            },
                            {
                                "text": "Oracle",
                                "id": "opt3",
                                "correct": False,
                                "explanation": {
                                    "mdText": "",
                                    "mdHtml": ""
                                },
                                "mdHtml": "<p>Oracle</p>\n"
                            }
                        ],
                        "multipleAnswers": False,
                        "questionTextHtml": "<p>Which database should we use when we have unstructured data and there's a need for high performance?</p>\n",
                        "id": "q1"
                    },
                    {
                        "questionText": "**(Select all that apply.)** We should use a key-value database for which scenarios?",
                        "questionOptions": [
                            {
                                "text": "When we create a social network like Facebook with a lot of complex relationships",
                                "id": "opt1",
                                "correct": False,
                                "explanation": {
                                    "mdText": "A graph database is a suitable option to store a social network with many complex relationships.",
                                    "mdHtml": "<p>A graph database is a suitable option to store a social network with many complex relationships.</p>\n"
                                },
                                "mdHtml": "<p>When we create a social network like Facebook with a lot of complex relationships</p>\n"
                            },
                            {
                                "text": "When we need to persist user state in our application",
                                "id": "opt2",
                                "correct": True,
                                "explanation": {
                                    "mdText": "User states are stored using a key-value database. A user ID can be considered key, and states can be assumed as values.",
                                    "mdHtml": "<p>User states are stored using a key-value database. A user ID can be considered key, and states can be assumed as values.</p>\n"
                                },
                                "mdHtml": "<p>When we need to persist user state in our application</p>\n"
                            },
                            {
                                "text": "When we implement caching in our application",
                                "id": "opt3",
                                "correct": True,
                                "explanation": {
                                    "mdText": "A cache like Memcached and Redis are key-value stores used for caching in different use-cases.",
                                    "mdHtml": "<p>A cache like Memcached and Redis are key-value stores used for caching in different use-cases.</p>\n"
                                },
                                "mdHtml": "<p>When we implement caching in our application</p>\n"
                            }
                        ],
                        "multipleAnswers": True,
                        "questionTextHtml": "<p><strong>(Select all that apply.)</strong> We should use a key-value database for which scenarios?</p>\n",
                        "id": "q2"
                    }
                ],
                "comp_id": "quiz1",
                "title": "Database Selection Quiz",
                "titleMdHtml": ""
            }
        },
        {
            "type": "MarkdownEditor",
            "content": {
                "text": "## Summary\n\nChoosing the right database is crucial for application success. Consider your data structure, consistency needs, and performance requirements when making your decision."
            }
        }
    ]
}

async def test_full_integration():
    """Test Quiz component in a full section with multiple components"""
    print("=" * 80)
    print("Full Integration Test: Quiz Component with Other Components")
    print("=" * 80)
    
    # Initialize processor
    processor = SectionContentProcessor(output_dir="generated_books")
    processor.set_book_context("test_quiz_integration", chapter_number=1, section_id="database-selection")
    
    try:
        # Process all components asynchronously
        latex_output, generated_images, component_types = await processor.process_section_components_async(section_data)
        
        print("\n" + "=" * 80)
        print("Component Types Processed:")
        print("=" * 80)
        for comp_type in component_types:
            print(f"  ✅ {comp_type}")
        
        print("\n" + "=" * 80)
        print("Generated LaTeX Output:")
        print("=" * 80)
        print(latex_output)
        print("=" * 80)
        
        # Create a complete LaTeX document
        full_document = r"""\documentclass[12pt,a4paper]{book}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{amsmath}
\usepackage{listings}
\usepackage{xcolor}

\title{Database Selection Guide}
\author{Integration Test}
\date{\today}

\begin{document}

\maketitle

\chapter{Database Fundamentals}

\section{Database Selection}

""" + latex_output + r"""

\end{document}
"""
        
        # Save to file
        output_file = "test_quiz_full_integration.tex"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(full_document)
        
        print(f"\n✅ Full LaTeX document saved to: {output_file}")
        print(f"✅ Generated {len(generated_images)} images")
        print(f"✅ Processed {len(component_types)} component types")
        
        # Verify key elements
        assert "Quiz" in component_types, "Quiz component not processed"
        assert "SlateHTML" in component_types, "SlateHTML component not processed"
        assert "MarkdownEditor" in component_types, "MarkdownEditor component not processed"
        assert "\\subsection*{Database Selection Quiz}" in latex_output, "Quiz title missing"
        assert "[CORRECT]" in latex_output, "Correct answer markers missing"
        assert "MongoDB" in latex_output, "Quiz content missing"
        assert "Key Considerations" in latex_output, "Markdown content missing"
        
        print("\n✅ All integration tests passed!")
        print("✅ Quiz component works correctly with other components!")
        
        print("\nTo compile the document:")
        print(f"  pdflatex {output_file}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(test_full_integration())

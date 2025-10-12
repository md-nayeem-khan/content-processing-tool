"""
Test Quiz component LaTeX compilation
"""

import json
from section_processor import SectionContentProcessor

# Sample Quiz data
quiz_data = {
    "type": "Quiz",
    "mode": "edit",
    "content": {
        "questions": [
            {
                "questionText": "Which database should we use when we have unstructured data and there's a need for high performance?",
                "questionOptions": [
                    {
                        "text": "MongoDB",
                        "id": "8tzRkjoGlFOrwXocqR3jS",
                        "correct": True,
                        "explanation": {
                            "mdText": "MongoDB is a database that stores unstructured data and provides high performance in data-relevant operations. ",
                            "mdHtml": "<p>MongoDB is a database that stores unstructured data and provides high performance in data-relevant operations.</p>\n"
                        },
                        "mdHtml": "<p>MongoDB</p>\n"
                    },
                    {
                        "text": "MySQL",
                        "id": "WXeUlJBY-sGf_ftTcveiX",
                        "correct": False,
                        "explanation": {
                            "mdText": "",
                            "mdHtml": ""
                        },
                        "mdHtml": "<p>MySQL</p>\n"
                    }
                ],
                "multipleAnswers": False,
                "questionTextHtml": "<p>Which database should we use when we have unstructured data and there's a need for high performance?</p>\n",
                "id": "xMtoUSUgcUiz8-UXIiQuh"
            },
            {
                "questionText": "**(Select all that apply.)** We should use a document-oriented database for which applications?",
                "questionOptions": [
                    {
                        "text": "Web-based multiplayer games",
                        "id": "lv5PeFTYRPqQTTnuxRkXd",
                        "correct": True,
                        "explanation": {
                            "mdText": "Documents such as JSON and YML store objects in the same structure (as in the game), making the operations within the game easier.",
                            "mdHtml": "<p>Documents such as JSON and YML store objects in the same structure (as in the game), making the operations within the game easier.</p>\n"
                        },
                        "mdHtml": "<p>Web-based multiplayer games</p>\n"
                    },
                    {
                        "text": "Real-time feeds",
                        "id": "RncFYt6EJyOvfMBgwiSog",
                        "correct": True,
                        "explanation": {
                            "mdText": "The real-time feed contains variably structured data for which a document database is a suitable option.",
                            "mdHtml": "<p>The real-time feed contains variably structured data for which a document database is a suitable option.</p>\n"
                        },
                        "mdHtml": "<p>Real-time feeds</p>\n"
                    }
                ],
                "multipleAnswers": True,
                "questionTextHtml": "<p><strong>(Select all that apply.)</strong> We should use a document-oriented database for which applications?</p>\n",
                "id": "BVRmGWiRzro2Vqn4v0nQ5"
            }
        ],
        "comp_id": "k2vLcq9WOC6JgBDoQ5mLG",
        "title": "Database Selection Quiz",
        "titleMdHtml": ""
    }
}

def test_quiz_compilation():
    """Test the Quiz component in a full LaTeX document"""
    print("=" * 80)
    print("Testing Quiz Component LaTeX Compilation")
    print("=" * 80)
    
    # Initialize processor
    processor = SectionContentProcessor(output_dir="generated_books")
    processor.set_book_context("test_quiz", chapter_number=1, section_id="test-section")
    
    # Process the quiz component
    try:
        quiz_latex = processor._process_quiz(quiz_data)
        
        # Create a complete LaTeX document
        full_document = r"""\documentclass[12pt,a4paper]{book}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{amsmath}
\usepackage{listings}
\usepackage{xcolor}

\title{Quiz Test Document}
\author{Test}
\date{\today}

\begin{document}

\maketitle

\chapter{Database Concepts}

\section{Introduction}

This section contains a quiz to test your understanding of database selection.

""" + quiz_latex + r"""

\section{Conclusion}

This concludes the quiz section.

\end{document}
"""
        
        # Save to file
        output_file = "test_quiz_compile.tex"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(full_document)
        
        print(f"\n✅ Full LaTeX document saved to: {output_file}")
        print("\nTo compile the document, run:")
        print(f"  pdflatex {output_file}")
        
        # Display the quiz portion
        print("\n" + "=" * 80)
        print("Quiz LaTeX Content:")
        print("=" * 80)
        print(quiz_latex)
        print("=" * 80)
        
        print("\n✅ Quiz processor test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    test_quiz_compilation()

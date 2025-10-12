"""
Test Quiz component processing
"""

import json
from section_processor import SectionContentProcessor

# Sample Quiz data from the user's request
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
                    },
                    {
                        "text": "Oracle",
                        "id": "Me1CaEGUclHa9JTCo1wbV",
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
                "id": "xMtoUSUgcUiz8-UXIiQuh"
            },
            {
                "questionText": "When should we avoid choosing a relational database for our application? ",
                "questionOptions": [
                    {
                        "text": "When we write an application that expects to handle a large number of read-write operations and concurrent users, but strong consistency is not required",
                        "correct": True,
                        "explanation": {
                            "mdText": "When strong consistency is not required, and there are many read-write operations and concurrent users, a better choice is to use a NoSQL database. Hence, this is the right option to avoid the relational database. ",
                            "mdHtml": "<p>When strong consistency is not required, and there are many read-write operations and concurrent users, a better choice is to use a NoSQL database. Hence, this is the right option to avoid the relational database.</p>\n"
                        },
                        "id": "Ur_HsnvYZHbnMbifJ0UKv",
                        "mdHtml": "<p>When we write an application that expects to handle a large number of read-write operations and concurrent users, but strong consistency is not required</p>\n"
                    },
                    {
                        "text": "When we write a financial application, like a stock trading application, and we need our data to be consistent at all times",
                        "correct": False,
                        "explanation": {
                            "mdText": "",
                            "mdHtml": ""
                        },
                        "id": "Z8plrGRzab15MkteeFzox",
                        "mdHtml": "<p>When we write a financial application, like a stock trading application, and we need our data to be consistent at all times</p>\n"
                    },
                    {
                        "text": "When we write an application to store a lot of complex structured data",
                        "correct": False,
                        "explanation": {
                            "mdText": "",
                            "mdHtml": ""
                        },
                        "id": "nMG3oT-l3eG8RCJUAFUQN",
                        "mdHtml": "<p>When we write an application to store a lot of complex structured data</p>\n"
                    }
                ],
                "multipleAnswers": False,
                "questionTextHtml": "<p>When should we avoid choosing a relational database for our application?</p>\n",
                "id": "KyvtKgp_fJus-zw1lz2jY"
            },
            {
                "questionText": "**(Select all that apply.)** We should use a document-oriented database for which applications?",
                "questionOptions": [
                    {
                        "text": "Web-based multiplayer games",
                        "id": "lv5PeFTYRPqQTTnuxRkXd",
                        "correct": True,
                        "explanation": {
                            "mdText": "Documents such as JSON and YML store objects in the same structure (as in the game), making the operations within the game easier. Therefore, such games require document-oriented databases to use. ",
                            "mdHtml": "<p>Documents such as JSON and YML store objects in the same structure (as in the game), making the operations within the game easier. Therefore, such games require document-oriented databases to use.</p>\n"
                        },
                        "mdHtml": "<p>Web-based multiplayer games</p>\n"
                    },
                    {
                        "text": "Banking application requiring consistency",
                        "id": "bUEApmnjxLuUCkGi9-aEg",
                        "correct": False,
                        "explanation": {
                            "mdText": "",
                            "mdHtml": ""
                        },
                        "mdHtml": "<p>Banking application requiring consistency</p>\n"
                    },
                    {
                        "text": "Social network application, like Facebook, containing complex relationships",
                        "id": "44CqJ3fpGgGOu-x0oT79j",
                        "correct": False,
                        "explanation": {
                            "mdText": "",
                            "mdHtml": ""
                        },
                        "mdHtml": "<p>Social network application, like Facebook, containing complex relationships</p>\n"
                    },
                    {
                        "text": "Real-time feeds",
                        "id": "RncFYt6EJyOvfMBgwiSog",
                        "correct": True,
                        "explanation": {
                            "mdText": "The real-time feed contains variably structured data (one feed can have different components than the others) for which a document database is a suitable option. ",
                            "mdHtml": "<p>The real-time feed contains variably structured data (one feed can have different components than the others) for which a document database is a suitable option.</p>\n"
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
        "title": "",
        "titleMdHtml": ""
    },
    "iteration": 0,
    "hash": 19,
    "saveVersion": 49,
    "status": "normal",
    "children": [
        {
            "text": ""
        }
    ],
    "headingTag": "N8TmnxV25eI6cka3M69p-",
    "collapsed": True
}

def test_quiz_processor():
    """Test the Quiz component processor"""
    print("=" * 80)
    print("Testing Quiz Component Processor")
    print("=" * 80)
    
    # Initialize processor
    processor = SectionContentProcessor(output_dir="generated_books")
    processor.set_book_context("test_quiz", chapter_number=1, section_id="test-section")
    
    # Process the quiz component
    try:
        latex_output = processor._process_quiz(quiz_data)
        
        print("\n" + "=" * 80)
        print("Generated LaTeX Output:")
        print("=" * 80)
        print(latex_output)
        print("=" * 80)
        
        # Save to file for inspection
        output_file = "test_quiz_output.tex"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(latex_output)
        
        print(f"\n✅ LaTeX output saved to: {output_file}")
        
        # Verify key elements are present
        assert "\\subsection*{Quiz}" in latex_output, "Quiz title missing"
        assert "Question 1:" in latex_output, "Question 1 missing"
        assert "Question 2:" in latex_output, "Question 2 missing"
        assert "Question 3:" in latex_output, "Question 3 missing"
        assert "[CORRECT]" in latex_output, "Correct answer marker missing"
        assert "MongoDB" in latex_output, "MongoDB option missing"
        assert "Explanation:" in latex_output, "Explanation missing"
        assert "(Select all that apply.)" in latex_output, "Multiple answers hint missing"
        
        print("\n✅ All assertions passed!")
        print("✅ Quiz processor is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Error processing quiz: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    test_quiz_processor()

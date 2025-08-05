"""
Test the LaTeX book generation API endpoint
"""

import httpx
import json

def test_latex_endpoint():
    """Test the /generate-latex-book endpoint"""
    
    url = "http://localhost:8000/generate-latex-book"
    
    payload = {
        "educative_course_name": "learn-html-css-javascript-from-scratch",
        "book_name": "html_css_js_complete_guide",
        "use_env_credentials": True
    }
    
    try:
        print("🚀 Testing LaTeX Book Generation API Endpoint")
        print("=" * 60)
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        print()
        
        response = httpx.post(url, json=payload, timeout=120.0)  # Increased timeout
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            
            print("=== LATEX GENERATION RESPONSE ===")
            print(f"Success: {data.get('success')}")
            print(f"Book Path: {data.get('book_path')}")
            print(f"Source: {data.get('source')}")
            
            book_data = data.get('book_data', {})
            print(f"\nBook Information:")
            print(f"  Title: {book_data.get('title')}")
            print(f"  Chapters: {book_data.get('chapters')}")
            print(f"  Sections: {book_data.get('sections')}")
            
            generated_files = data.get('generated_files', [])
            print(f"\nGenerated Files ({len(generated_files)}):")
            for file_name in generated_files:
                print(f"  - {file_name}")
            
            print("\n✅ LaTeX book generation successful!")
            
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print("Response:")
                print(json.dumps(error_data, indent=2))
            except:
                print("Response:")
                print(response.text)
                
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_latex_endpoint()

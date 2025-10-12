"""
Test CanvasAnimation Component Processing

This test verifies that CanvasAnimation components (multi-image sliders) are correctly processed.
"""

import asyncio
import os
from section_processor import SectionContentProcessor

async def test_canvas_animation():
    """Test CanvasAnimation with multiple images"""
    
    # Sample CanvasAnimation component data
    test_component = {
        "type": "LazyLoadPlaceholder",
        "content": {
            "actualType": "CanvasAnimation",
            "widgetIndex": 13,
            "contentRevision": "417",
            "pageId": 4570386150981632,
            "height": 400,
            "width": 900,
            "slidesCount": 7
        }
    }
    
    # Sample section data with CanvasAnimation
    section_data = {
        "components": [
            {
                "type": "MarkdownEditor",
                "content": {
                    "text": "# Test Section with Animation\n\nThis section contains a canvas animation slider."
                }
            },
            test_component,
            {
                "type": "MarkdownEditor",
                "content": {
                    "text": "This text comes after the animation."
                }
            }
        ],
        "summary": {
            "title": "Test Section with CanvasAnimation",
            "description": "Testing canvas animation processing"
        }
    }
    
    # Initialize processor
    processor = SectionContentProcessor(output_dir="generated_books")
    
    # Set book context with credentials (use environment variables)
    processor.set_book_context(
        book_name="test_canvas_animation",
        chapter_number=1,
        section_id="test_section_canvas",
        author_id="10370001",  # Example author_id
        collection_id="4941429335392256",  # Example collection_id
        token=os.getenv("EDUCATIVE_TOKEN"),
        cookie=os.getenv("EDUCATIVE_COOKIE")
    )
    
    print("=" * 80)
    print("Testing CanvasAnimation Component Processing")
    print("=" * 80)
    
    try:
        # Process the section
        latex_content, generated_images, component_types = await processor.process_section_components_async(section_data)
        
        print("\n✅ Processing completed successfully!")
        print(f"\nComponent types found: {component_types}")
        print(f"Generated images: {len(generated_images)} images")
        
        for idx, img in enumerate(generated_images, 1):
            print(f"   [{idx}] {img}")
        
        print(f"\nLaTeX content length: {len(latex_content)} characters")
        
        print("\n" + "=" * 80)
        print("Generated LaTeX Content (first 1000 chars):")
        print("=" * 80)
        print(latex_content[:1000])
        print("..." if len(latex_content) > 1000 else "")
        print("=" * 80)
        
        # Verify CanvasAnimation was processed
        if "LazyLoadPlaceholder" in component_types:
            print("\n✅ LazyLoadPlaceholder component was detected")
        else:
            print("\n⚠️  LazyLoadPlaceholder component was not detected")
        
        # Check if multiple images were generated
        if len(generated_images) > 1:
            print(f"✅ Multiple images generated ({len(generated_images)} images)")
        elif len(generated_images) == 1:
            print("⚠️  Only 1 image generated (expected multiple for CanvasAnimation)")
        else:
            print("⚠️  No images were generated")
        
        # Check LaTeX content for subfigures
        if "subfigure" in latex_content:
            print("✅ LaTeX content includes subfigure environment (multi-image layout)")
        elif "includegraphics" in latex_content:
            print("⚠️  LaTeX has images but no subfigures (may be single image)")
        else:
            print("⚠️  LaTeX content does not include expected image content")
        
        # Count subfigures
        subfigure_count = latex_content.count("\\begin{subfigure}")
        if subfigure_count > 0:
            print(f"✅ Found {subfigure_count} subfigures in LaTeX output")
        
        # Save output for inspection
        output_file = "test_canvas_animation_output.tex"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        print(f"\n💾 Full LaTeX output saved to: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def test_mixed_lazy_load():
    """Test section with both MxGraphWidget and CanvasAnimation"""
    
    section_data = {
        "components": [
            {
                "type": "MarkdownEditor",
                "content": {"text": "# Mixed LazyLoadPlaceholder Test"}
            },
            {
                "type": "LazyLoadPlaceholder",
                "content": {
                    "actualType": "MxGraphWidget",
                    "widgetIndex": 4,
                    "contentRevision": "423",
                    "pageId": 6043988183744512
                }
            },
            {
                "type": "MarkdownEditor",
                "content": {"text": "Now here's an animation:"}
            },
            {
                "type": "LazyLoadPlaceholder",
                "content": {
                    "actualType": "CanvasAnimation",
                    "widgetIndex": 13,
                    "contentRevision": "417",
                    "pageId": 4570386150981632,
                    "slidesCount": 7
                }
            }
        ],
        "summary": {"title": "Mixed Test"}
    }
    
    processor = SectionContentProcessor(output_dir="generated_books")
    processor.set_book_context(
        book_name="test_mixed",
        chapter_number=1,
        section_id="test_mixed_section",
        author_id="10370001",
        collection_id="4941429335392256",
        token=os.getenv("EDUCATIVE_TOKEN"),
        cookie=os.getenv("EDUCATIVE_COOKIE")
    )
    
    print("\n" + "=" * 80)
    print("Testing Mixed LazyLoadPlaceholder Types")
    print("=" * 80)
    
    try:
        latex_content, generated_images, component_types = await processor.process_section_components_async(section_data)
        
        print(f"\n✅ Processing completed!")
        print(f"Total images generated: {len(generated_images)}")
        print(f"Component types: {set(component_types)}")
        
        # Check for both single figures and subfigures
        single_figures = latex_content.count("\\begin{figure}") - latex_content.count("\\begin{subfigure}")
        subfigures = latex_content.count("\\begin{subfigure}")
        
        print(f"\nLaTeX structure:")
        print(f"  - Figure environments: {latex_content.count('\\begin{figure}')}")
        print(f"  - Subfigure environments: {subfigures}")
        print(f"  - Single images: {single_figures}")
        
        if single_figures > 0 and subfigures > 0:
            print("✅ Successfully mixed single images and multi-image layouts")
            return True
        else:
            print("⚠️  Expected both single and multi-image layouts")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

async def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("CanvasAnimation Component Test Suite")
    print("=" * 80)
    
    results = []
    
    # Test 1: CanvasAnimation processing
    print("\n[Test 1/2] CanvasAnimation Processing")
    result1 = await test_canvas_animation()
    results.append(("CanvasAnimation Processing", result1))
    
    # Test 2: Mixed LazyLoadPlaceholder types
    print("\n[Test 2/2] Mixed LazyLoadPlaceholder Types")
    result2 = await test_mixed_lazy_load()
    results.append(("Mixed LazyLoadPlaceholder", result2))
    
    # Summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())

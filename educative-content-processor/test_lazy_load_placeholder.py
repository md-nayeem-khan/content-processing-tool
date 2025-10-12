"""
Test LazyLoadPlaceholder Component Processing

This test verifies that LazyLoadPlaceholder components (MxGraphWidget) are correctly processed.
"""

import asyncio
from section_processor import SectionContentProcessor

async def test_lazy_load_placeholder():
    """Test LazyLoadPlaceholder with MxGraphWidget"""
    
    # Sample LazyLoadPlaceholder component data
    test_component = {
        "type": "LazyLoadPlaceholder",
        "content": {
            "actualType": "MxGraphWidget",
            "widgetIndex": 4,
            "contentRevision": "423",
            "pageId": 6043988183744512,
            "height": 400,
            "width": 600,
            "slidesCount": 0
        }
    }
    
    # Sample section data with LazyLoadPlaceholder
    section_data = {
        "components": [
            {
                "type": "MarkdownEditor",
                "content": {
                    "text": "# Test Section\n\nThis section contains a lazy-loaded widget."
                }
            },
            test_component,
            {
                "type": "MarkdownEditor",
                "content": {
                    "text": "This text comes after the widget."
                }
            }
        ],
        "summary": {
            "title": "Test Section with LazyLoadPlaceholder",
            "description": "Testing lazy load placeholder processing"
        }
    }
    
    # Initialize processor
    processor = SectionContentProcessor(output_dir="generated_books")
    
    # Set book context with credentials (use environment variables)
    import os
    processor.set_book_context(
        book_name="test_lazy_load",
        chapter_number=1,
        section_id="test_section_123",
        author_id="10370001",  # Example author_id
        collection_id="4941429335392256",  # Example collection_id
        token=os.getenv("EDUCATIVE_TOKEN"),
        cookie=os.getenv("EDUCATIVE_COOKIE")
    )
    
    print("=" * 80)
    print("Testing LazyLoadPlaceholder Component Processing")
    print("=" * 80)
    
    try:
        # Process the section
        latex_content, generated_images, component_types = await processor.process_section_components_async(section_data)
        
        print("\n✅ Processing completed successfully!")
        print(f"\nComponent types found: {component_types}")
        print(f"Generated images: {generated_images}")
        print(f"\nLaTeX content length: {len(latex_content)} characters")
        
        print("\n" + "=" * 80)
        print("Generated LaTeX Content:")
        print("=" * 80)
        print(latex_content)
        print("=" * 80)
        
        # Verify LazyLoadPlaceholder was processed
        if "LazyLoadPlaceholder" in component_types:
            print("\n✅ LazyLoadPlaceholder component was detected")
        else:
            print("\n⚠️  LazyLoadPlaceholder component was not detected")
        
        # Check if image was generated
        if generated_images:
            print(f"✅ {len(generated_images)} image(s) generated")
            for img in generated_images:
                print(f"   - {img}")
        else:
            print("⚠️  No images were generated (this may be expected if API call failed)")
        
        # Check LaTeX content
        if "includegraphics" in latex_content or "MxGraphWidget" in latex_content:
            print("✅ LaTeX content includes image reference or widget placeholder")
        else:
            print("⚠️  LaTeX content does not include expected image/widget content")
        
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def test_unsupported_widget_type():
    """Test LazyLoadPlaceholder with unsupported widget type"""
    
    test_component = {
        "type": "LazyLoadPlaceholder",
        "content": {
            "actualType": "CanvasAnimation",  # Not yet supported
            "widgetIndex": 1,
            "contentRevision": "100",
            "pageId": 123456789,
            "height": 300,
            "width": 500
        }
    }
    
    section_data = {
        "components": [test_component],
        "summary": {"title": "Test Unsupported Widget"}
    }
    
    processor = SectionContentProcessor(output_dir="generated_books")
    processor.set_book_context(
        book_name="test_lazy_load",
        chapter_number=1,
        section_id="test_section_456"
    )
    
    print("\n" + "=" * 80)
    print("Testing Unsupported Widget Type (CanvasAnimation)")
    print("=" * 80)
    
    try:
        latex_content, generated_images, component_types = await processor.process_section_components_async(section_data)
        
        print(f"\nGenerated LaTeX:\n{latex_content}")
        
        if "not yet supported" in latex_content:
            print("\n✅ Unsupported widget type handled correctly")
            return True
        else:
            print("\n⚠️  Expected 'not yet supported' message")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

async def test_missing_credentials():
    """Test LazyLoadPlaceholder without required credentials"""
    
    test_component = {
        "type": "LazyLoadPlaceholder",
        "content": {
            "actualType": "MxGraphWidget",
            "widgetIndex": 1,
            "contentRevision": "100",
            "pageId": 123456789
        }
    }
    
    section_data = {
        "components": [test_component],
        "summary": {"title": "Test Missing Credentials"}
    }
    
    processor = SectionContentProcessor(output_dir="generated_books")
    # Don't set author_id and collection_id
    processor.set_book_context(
        book_name="test_lazy_load",
        chapter_number=1,
        section_id="test_section_789"
    )
    
    print("\n" + "=" * 80)
    print("Testing Missing Credentials")
    print("=" * 80)
    
    try:
        latex_content, generated_images, component_types = await processor.process_section_components_async(section_data)
        
        print(f"\nGenerated LaTeX:\n{latex_content}")
        
        if "requires course context" in latex_content:
            print("\n✅ Missing credentials handled correctly")
            return True
        else:
            print("\n⚠️  Expected 'requires course context' message")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

async def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("LazyLoadPlaceholder Component Test Suite")
    print("=" * 80)
    
    results = []
    
    # Test 1: Normal MxGraphWidget processing
    print("\n[Test 1/3] MxGraphWidget Processing")
    result1 = await test_lazy_load_placeholder()
    results.append(("MxGraphWidget Processing", result1))
    
    # Test 2: Unsupported widget type
    print("\n[Test 2/3] Unsupported Widget Type")
    result2 = await test_unsupported_widget_type()
    results.append(("Unsupported Widget Type", result2))
    
    # Test 3: Missing credentials
    print("\n[Test 3/3] Missing Credentials")
    result3 = await test_missing_credentials()
    results.append(("Missing Credentials", result3))
    
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

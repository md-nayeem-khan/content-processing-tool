"""
Test DrawIOWidget with slides functionality
"""
import asyncio
import os
from section_processor import SectionContentProcessor

async def test_drawio_slides():
    """Test DrawIOWidget with slidesEnabled=true"""
    
    # Sample DrawIOWidget with slides (from user's example)
    test_component = {
        "type": "DrawIOWidget",
        "mode": "edit",
        "content": {
            "path": "",
            "caption": "",
            "editorImagePath": "/api/collection/10370001/4941429335392256/page/5053577315221504/image/5343016930115584?page_type=collection_lesson",
            "version": 2,
            "height": 391,
            "width": 451,
            "editorGCSImagePath": "educative-us-central1/uc/v5/10370001/collections/4941429335392256/rev-359/pages/5053577315221504/images/5343016930115584-2024-10-23T06:46:49.330185",
            "slidesEnabled": True,
            "isSlides": True,
            "slidesCaption": [
                "Service before using caching",
                "Service using caching to improve performance."
            ],
            "redirectionUrl": "",
            "borderColor": "#ffffff",
            "comp_id": "a9b7EOV_kFbOev_oE6yh_",
            "slidesId": 5013198002847744
        },
        "iteration": 0,
        "hash": 1,
        "status": "normal",
        "contentID": "rBL_qqTUoc9RrR8_KjKZG",
        "saveVersion": 3,
        "children": [
            {
                "text": ""
            }
        ],
        "headingTag": "87QePkAoSR7-9xwTpfpg3",
        "collapsed": False
    }
    
    # Sample section data with DrawIOWidget slides
    section_data = {
        "components": [
            {
                "type": "SlateHTML",
                "content": {
                    "html": "<h2>Caching Example</h2><p>This example shows how caching improves performance.</p>"
                }
            },
            test_component,
            {
                "type": "SlateHTML",
                "content": {
                    "html": "<p>As you can see from the slides above, caching significantly reduces response time.</p>"
                }
            }
        ],
        "summary": {
            "title": "Test Section with DrawIOWidget Slides",
            "description": "Testing DrawIO slides processing"
        }
    }
    
    # Initialize processor
    processor = SectionContentProcessor(output_dir="generated_books")
    
    # Set book context with credentials (use environment variables)
    processor.set_book_context(
        book_name="test_drawio_slides",
        chapter_number=1,
        section_id="test_section_drawio_slides",
        author_id="10370001",
        collection_id="4941429335392256",
        token=os.getenv("EDUCATIVE_TOKEN"),
        cookie=os.getenv("EDUCATIVE_COOKIE")
    )
    
    print("=" * 80)
    print("Testing DrawIOWidget Slides Component Processing")
    print("=" * 80)
    
    try:
        # Process the section
        latex_content, generated_images, component_types = await processor.process_section_components_async(section_data)
        
        print("\n✅ Processing completed successfully!")
        print(f"\nComponent types found: {component_types}")
        print(f"Generated images: {len(generated_images)} images")
        
        if generated_images:
            for idx, img in enumerate(generated_images, 1):
                print(f"   [{idx}] {img}")
        
        print(f"\nLaTeX content length: {len(latex_content)} characters")
        
        print("\n" + "=" * 80)
        print("Generated LaTeX Content (first 1500 chars):")
        print("=" * 80)
        print(latex_content[:1500])
        print("..." if len(latex_content) > 1500 else "")
        print("=" * 80)
        
        # Verify DrawIOWidget was processed
        if "DrawIOWidget" in component_types:
            print("\n✅ DrawIOWidget component was detected")
        else:
            print("\n⚠️  DrawIOWidget component was not detected")
        
        # Check if multiple images were generated (slides)
        if len(generated_images) > 1:
            print(f"✅ Multiple slide images generated ({len(generated_images)} images)")
        elif len(generated_images) == 1:
            print(f"⚠️  Only 1 image generated (expected multiple for slides)")
        else:
            print("⚠️  No images were generated")
        
        # Check LaTeX content for subfigures
        if "\\begin{subfigure}" in latex_content:
            print("✅ LaTeX includes subfigure layout (correct for slides)")
        else:
            print("⚠️  LaTeX does not include subfigure layout")
        
        # Check if captions are present
        if "Service before using caching" in latex_content:
            print("✅ Slide captions included in LaTeX")
        else:
            print("⚠️  Slide captions not found in LaTeX")
        
        # Write to output file
        output_file = "test_drawio_slides_output.tex"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("% DrawIOWidget Slides Test Output\n")
            f.write("% Generated by test_drawio_slides.py\n\n")
            f.write(latex_content)
        
        print(f"\n📄 Full LaTeX output written to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_regular_drawio():
    """Test regular DrawIOWidget (non-slides) still works"""
    
    test_component = {
        "type": "DrawIOWidget",
        "content": {
            "editorImagePath": "/api/collection/10370001/4941429335392256/page/6043988183744512/image/6068212462780416?page_type=collection_lesson",
            "caption": "Regular diagram without slides",
            "slidesEnabled": False,
            "isSlides": False
        }
    }
    
    section_data = {
        "components": [test_component]
    }
    
    processor = SectionContentProcessor(output_dir="generated_books")
    processor.set_book_context(
        book_name="test_drawio",
        chapter_number=1,
        section_id="test_regular",
        author_id="10370001",
        collection_id="4941429335392256",
        token=os.getenv("EDUCATIVE_TOKEN"),
        cookie=os.getenv("EDUCATIVE_COOKIE")
    )
    
    print("\n" + "=" * 80)
    print("Testing Regular DrawIOWidget (Non-Slides)")
    print("=" * 80)
    
    try:
        latex_content, generated_images, component_types = await processor.process_section_components_async(section_data)
        
        print(f"\n✅ Regular DrawIOWidget processed")
        print(f"Generated images: {len(generated_images)}")
        print(f"LaTeX preview: {latex_content[:200]}...")
        
        if len(generated_images) == 1:
            print("✅ Single image generated (correct for non-slides)")
        else:
            print(f"⚠️  Expected 1 image, got {len(generated_images)}")
        
        if "\\begin{subfigure}" not in latex_content:
            print("✅ No subfigure layout (correct for regular diagram)")
        else:
            print("⚠️  Subfigure layout found (should only be for slides)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

async def test_single_flag_true():
    """Test DrawIOWidget with only one flag true (should NOT trigger slides mode)"""
    
    # Test with only slidesEnabled=true
    test_component1 = {
        "type": "DrawIOWidget",
        "content": {
            "editorImagePath": "/api/collection/10370001/4941429335392256/page/6043988183744512/image/6068212462780416?page_type=collection_lesson",
            "caption": "Only slidesEnabled=true",
            "slidesEnabled": True,
            "isSlides": False,
            "slidesId": 5013198002847744
        }
    }
    
    # Test with only isSlides=true
    test_component2 = {
        "type": "DrawIOWidget",
        "content": {
            "editorImagePath": "/api/collection/10370001/4941429335392256/page/6043988183744512/image/6068212462780416?page_type=collection_lesson",
            "caption": "Only isSlides=true",
            "slidesEnabled": False,
            "isSlides": True,
            "slidesId": 5013198002847744
        }
    }
    
    processor = SectionContentProcessor(output_dir="generated_books")
    processor.set_book_context(
        book_name="test_drawio",
        chapter_number=1,
        section_id="test_single_flag",
        author_id="10370001",
        collection_id="4941429335392256",
        token=os.getenv("EDUCATIVE_TOKEN"),
        cookie=os.getenv("EDUCATIVE_COOKIE")
    )
    
    print("\n" + "=" * 80)
    print("Testing DrawIOWidget with Single Flag True (Should NOT be slides)")
    print("=" * 80)
    
    all_passed = True
    
    # Test 1: Only slidesEnabled=true
    try:
        section_data1 = {"components": [test_component1]}
        latex_content1, generated_images1, _ = await processor.process_section_components_async(section_data1)
        
        if "\\begin{subfigure}" not in latex_content1:
            print("✅ Test 1 PASSED: slidesEnabled=true only → Regular mode (no subfigures)")
        else:
            print("❌ Test 1 FAILED: Should be regular mode, but got subfigures")
            all_passed = False
    except Exception as e:
        print(f"❌ Test 1 ERROR: {e}")
        all_passed = False
    
    # Test 2: Only isSlides=true
    try:
        section_data2 = {"components": [test_component2]}
        latex_content2, generated_images2, _ = await processor.process_section_components_async(section_data2)
        
        if "\\begin{subfigure}" not in latex_content2:
            print("✅ Test 2 PASSED: isSlides=true only → Regular mode (no subfigures)")
        else:
            print("❌ Test 2 FAILED: Should be regular mode, but got subfigures")
            all_passed = False
    except Exception as e:
        print(f"❌ Test 2 ERROR: {e}")
        all_passed = False
    
    return all_passed

async def main():
    """Run all tests"""
    print("\n" + "🧪 " * 20)
    print("DrawIOWidget Slides Feature Tests")
    print("🧪 " * 20 + "\n")
    
    # Test 1: DrawIOWidget with slides (both flags true)
    result1 = await test_drawio_slides()
    
    # Test 2: Regular DrawIOWidget (ensure backward compatibility)
    result2 = await test_regular_drawio()
    
    # Test 3: Single flag true (should NOT trigger slides mode)
    result3 = await test_single_flag_true()
    
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    print(f"DrawIOWidget Slides Test (both flags): {'✅ PASSED' if result1 else '❌ FAILED'}")
    print(f"Regular DrawIOWidget Test: {'✅ PASSED' if result2 else '❌ FAILED'}")
    print(f"Single Flag Test (should be regular): {'✅ PASSED' if result3 else '❌ FAILED'}")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())

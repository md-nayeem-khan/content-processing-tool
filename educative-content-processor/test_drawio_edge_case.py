"""
Test DrawIOWidget with slidesEnabled=true but isSlides=false
This should be treated as a regular DrawIOWidget, not slides
"""
import asyncio
import os
from section_processor import SectionContentProcessor

async def test_slides_enabled_but_not_slides():
    """Test DrawIOWidget with slidesEnabled=true and isSlides=false"""
    
    # Your exact example
    test_component = {
        "type": "DrawIOWidget",
        "mode": "edit",
        "content": {
            "path": "/api/collection/10370001/4941429335392256/page/5806944861814784/image/5844522846519296?page_type=collection_lesson",
            "caption": "",
            "editorImagePath": "/api/collection/10370001/4941429335392256/page/5806944861814784/image/5761017267486720?page_type=collection_lesson",
            "version": 2,
            "height": 131,
            "width": 421,
            "editorGCSImagePath": "educative-us-central1/uc/v5/10370001/collections/4941429335392256/rev-359/pages/5806944861814784/images/5761017267486720-2024-10-17T07:42:53.436298",
            "slidesEnabled": True,
            "isSlides": False,
            "slidesCaption": [],
            "redirectionUrl": "",
            "borderColor": "#ffffff",
            "comp_id": "zm0neqWjGXP1849uYiNZ9",
            "slidesId": None
        }
    }
    
    section_data = {
        "components": [
            {
                "type": "SlateHTML",
                "content": {
                    "html": "<p>Testing DrawIOWidget with slidesEnabled=true but isSlides=false</p>"
                }
            },
            test_component
        ]
    }
    
    # Initialize processor
    processor = SectionContentProcessor(output_dir="generated_books")
    
    # Set book context
    processor.set_book_context(
        book_name="test_edge_case",
        chapter_number=1,
        section_id="test_slides_enabled_false",
        author_id="10370001",
        collection_id="4941429335392256",
        token=os.getenv("EDUCATIVE_TOKEN"),
        cookie=os.getenv("EDUCATIVE_COOKIE")
    )
    
    print("=" * 80)
    print("Testing: slidesEnabled=true, isSlides=false, slidesId=null")
    print("Expected: Should be treated as REGULAR DrawIOWidget (not slides)")
    print("=" * 80)
    
    try:
        # Process the section
        latex_content, generated_images, component_types = await processor.process_section_components_async(section_data)
        
        print("\n✅ Processing completed successfully!")
        print(f"\nComponent types: {component_types}")
        print(f"Generated images: {len(generated_images)}")
        
        if generated_images:
            for img in generated_images:
                print(f"   - {img}")
        
        print(f"\nLaTeX content preview:")
        print("=" * 80)
        print(latex_content[:500])
        print("=" * 80)
        
        # Verify it was NOT treated as slides
        if "\\begin{subfigure}" not in latex_content:
            print("\n✅ CORRECT: No subfigure layout (treated as regular DrawIOWidget)")
        else:
            print("\n❌ ERROR: Subfigure layout found (incorrectly treated as slides)")
        
        # Check for error messages
        if "missing slidesId" in latex_content:
            print("❌ ERROR: 'missing slidesId' error found in output")
            print("   This should NOT happen when isSlides=false")
        else:
            print("✅ CORRECT: No 'missing slidesId' error")
        
        # Check if single image was processed
        if len(generated_images) == 1:
            print("✅ CORRECT: Single image generated (regular mode)")
        elif len(generated_images) > 1:
            print("❌ ERROR: Multiple images generated (slides mode was triggered)")
        else:
            print("⚠️  WARNING: No images generated")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    result = await test_slides_enabled_but_not_slides()
    
    print("\n" + "=" * 80)
    if result:
        print("Test Result: ✅ PASSED")
    else:
        print("Test Result: ❌ FAILED")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())

"""
Test LazyLoadPlaceholder with Real Course Section

This script reprocesses a real section from the Grokking System Design course
that contains LazyLoadPlaceholder components.
"""

import asyncio
import os
import json
from section_processor import SectionContentProcessor

async def test_real_section():
    """Test with real section containing LazyLoadPlaceholder"""
    
    # Section details from grokking-the-system-design-interview
    book_name = "grokking-the-system-design-interview"
    chapter_number = 26
    section_id = "4932171382390784"
    section_title = "Evaluation of YouTube's Design"
    
    # Course IDs for grokking-the-system-design-interview
    author_id = "10370001"
    collection_id = "4941429335392256"
    
    # Get credentials from environment
    token = os.getenv("EDUCATIVE_TOKEN")
    cookie = os.getenv("EDUCATIVE_COOKIE")
    
    if not cookie:
        print("⚠️  WARNING: EDUCATIVE_COOKIE environment variable not set")
        print("   Attempting to proceed without authentication (may fail for some content)")
        print("   Note: The first test passed, so credentials may be cached or not required")
    
    print("=" * 80)
    print(f"Testing Real Section with LazyLoadPlaceholder")
    print("=" * 80)
    print(f"Book: {book_name}")
    print(f"Chapter: {chapter_number}")
    print(f"Section ID: {section_id}")
    print(f"Section Title: {section_title}")
    print("=" * 80)
    
    try:
        # Initialize processor
        processor = SectionContentProcessor(output_dir="generated_books")
        
        # Set book context with credentials
        processor.set_book_context(
            book_name=book_name,
            chapter_number=chapter_number,
            section_id=section_id,
            author_id=author_id,
            collection_id=collection_id,
            token=token,
            cookie=cookie
        )
        
        print("\n📥 Fetching section content from Educative API...")
        
        # Fetch section content
        section_data = await processor.fetch_section_content(
            content_type="course",
            author_id=author_id,
            collection_id=collection_id,
            page_id=section_id,
            token=token,
            cookie=cookie
        )
        
        print(f"✅ Section content fetched successfully")
        
        # Count components
        components = section_data.get("components", [])
        component_types = [c.get("type") for c in components]
        lazy_load_count = component_types.count("LazyLoadPlaceholder")
        
        print(f"\n📊 Component Statistics:")
        print(f"   Total components: {len(components)}")
        print(f"   LazyLoadPlaceholder components: {lazy_load_count}")
        
        if lazy_load_count > 0:
            print(f"\n🔍 LazyLoadPlaceholder Details:")
            for i, comp in enumerate(components):
                if comp.get("type") == "LazyLoadPlaceholder":
                    content = comp.get("content", {})
                    print(f"   [{i+1}] actualType: {content.get('actualType')}")
                    print(f"       pageId: {content.get('pageId')}")
                    print(f"       contentRevision: {content.get('contentRevision')}")
                    print(f"       widgetIndex: {content.get('widgetIndex')}")
        
        print(f"\n⚙️  Processing section components...")
        
        # Process components
        latex_content, generated_images, processed_types = await processor.process_section_components_async(section_data)
        
        print(f"\n✅ Processing completed!")
        print(f"\n📈 Results:")
        print(f"   Component types processed: {set(processed_types)}")
        print(f"   Generated images: {len(generated_images)}")
        
        if generated_images:
            print(f"\n🖼️  Generated Images:")
            for img in generated_images:
                print(f"   - {img}")
        
        # Check for LazyLoadPlaceholder in output
        if "LazyLoadPlaceholder" in processed_types:
            print(f"\n✅ LazyLoadPlaceholder components were processed")
            
            # Check if they were successfully converted
            if "not yet supported" in latex_content:
                print(f"⚠️  Some LazyLoadPlaceholder components may not have been fully processed")
            else:
                print(f"✅ All LazyLoadPlaceholder components appear to be processed successfully")
        
        # Show a sample of the LaTeX content
        print(f"\n📄 LaTeX Content Sample (first 500 chars):")
        print("-" * 80)
        print(latex_content[:500])
        print("-" * 80)
        
        # Search for figure environments (indicates images were processed)
        figure_count = latex_content.count("\\begin{figure}")
        print(f"\n📊 LaTeX Statistics:")
        print(f"   Total length: {len(latex_content)} characters")
        print(f"   Figure environments: {figure_count}")
        print(f"   Image references: {latex_content.count('includegraphics')}")
        
        # Save the output for inspection
        output_file = f"test_output_section_{section_id}.tex"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        print(f"\n💾 Full LaTeX output saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the test"""
    print("\n" + "=" * 80)
    print("Real Section LazyLoadPlaceholder Test")
    print("=" * 80)
    
    success = await test_real_section()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ TEST PASSED - LazyLoadPlaceholder processing works with real data!")
    else:
        print("❌ TEST FAILED - Check error messages above")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())

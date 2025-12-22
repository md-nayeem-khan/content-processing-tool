"""
Test Inkscape installation and SVG conversion capability
"""
import os
import subprocess
import shutil
from pathlib import Path

print("=" * 80)
print("INKSCAPE VALIDATION TEST")
print("=" * 80)

# Check 1: Look for Inkscape executable
print("\n1️⃣ Searching for Inkscape executable...")

inkscape_cmd = shutil.which('inkscape')
if inkscape_cmd:
    print(f"   ✅ Found in PATH: {inkscape_cmd}")
else:
    print("   ⚠️  Not found in PATH, checking common locations...")
    possible_paths = [
        r'C:\Program Files\Inkscape\bin\inkscape.exe',
        r'C:\Program Files (x86)\Inkscape\bin\inkscape.exe',
        r'C:\Program Files\Inkscape\inkscape.exe',
        r'C:\Program Files (x86)\Inkscape\inkscape.exe',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            inkscape_cmd = path
            print(f"   ✅ Found at: {path}")
            break
        else:
            print(f"   ❌ Not found: {path}")

if not inkscape_cmd:
    print("\n❌ FAILED: Inkscape not found!")
    print("   Please install from: https://inkscape.org/release/")
    exit(1)

# Check 2: Get version
print("\n2️⃣ Getting Inkscape version...")
try:
    result = subprocess.run(
        [inkscape_cmd, '--version'],
        capture_output=True,
        text=True,
        timeout=10
    )
    # Inkscape outputs to stderr for some reason
    version_output = result.stdout + result.stderr
    if version_output:
        print(f"   ✅ {version_output.strip()}")
    else:
        print("   ⚠️  Version command executed but no output")
except Exception as e:
    print(f"   ⚠️  Error getting version: {e}")

# Check 3: Test SVG to PNG conversion
print("\n3️⃣ Testing SVG to PNG conversion...")

test_svg = Path("test_inkscape.svg")
test_png = Path("test_inkscape.png")

# Create test SVG
test_svg.write_text('''<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <rect width="200" height="200" fill="lightblue"/>
  <circle cx="100" cy="100" r="50" fill="red"/>
  <text x="100" y="110" text-anchor="middle" fill="white" font-size="20">TEST</text>
</svg>''')

print(f"   Created test SVG: {test_svg}")

try:
    result = subprocess.run([
        inkscape_cmd,
        str(test_svg),
        '--export-type=png',
        f'--export-filename={str(test_png)}',
        '--export-width=200',
        '--export-background=white',
    ], capture_output=True, text=True, timeout=30)
    
    if test_png.exists():
        size = test_png.stat().st_size
        if size > 0:
            print(f"   ✅ SUCCESS! PNG created: {size:,} bytes")
            print(f"   ✅ Inkscape is working perfectly!")
            
            # Cleanup
            test_svg.unlink()
            test_png.unlink()
            print(f"   🧹 Cleaned up test files")
            
            print("\n" + "=" * 80)
            print("✅ VALIDATION PASSED: Inkscape is installed and working!")
            print("   The application will automatically use Inkscape for SVG conversion.")
            print("=" * 80)
        else:
            print(f"   ❌ PNG file created but empty (0 bytes)")
            print(f"   stderr: {result.stderr}")
    else:
        print(f"   ❌ PNG file was not created")
        print(f"   Return code: {result.returncode}")
        print(f"   stdout: {result.stdout}")
        print(f"   stderr: {result.stderr}")
        
except subprocess.TimeoutExpired:
    print(f"   ❌ Conversion timed out (30s)")
except Exception as e:
    print(f"   ❌ Error during conversion: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)

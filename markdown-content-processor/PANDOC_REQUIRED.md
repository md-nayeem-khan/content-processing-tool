# Pandoc Installation Guide

## ⚠️ IMPORTANT: Pandoc is REQUIRED

This application **requires** Pandoc to be installed on your system to convert markdown content to LaTeX. The application will not start without it.

## Why Pandoc is Required

Pandoc is a powerful document converter that provides high-quality markdown to LaTeX conversion with support for:
- Complex markdown syntax
- Code blocks with syntax highlighting
- Tables
- Mathematical equations
- Citations and references
- And much more

## Installation Instructions

### Windows

1. **Download the installer:**
   - Visit: https://pandoc.org/installing.html
   - Download the latest Windows installer (.msi file)

2. **Run the installer:**
   - Double-click the downloaded .msi file
   - Follow the installation wizard
   - Pandoc will be automatically added to your PATH

3. **Verify installation:**
   ```bash
   pandoc --version
   ```

### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install pandoc
```

### Linux (Fedora/RHEL)

```bash
sudo dnf install pandoc
```

### macOS

Using Homebrew:
```bash
brew install pandoc
```

Or download the installer from: https://pandoc.org/installing.html

## Verifying Installation

After installing Pandoc, verify it's working:

```bash
# Check Pandoc version
pandoc --version

# Test conversion
echo "# Test" | pandoc -f markdown -t latex
```

Expected output should include:
```
pandoc 2.x.x
Compiled with...
```

## Python Package (Already Included)

The `pypandoc` Python package is already included in `requirements.txt` and provides the Python interface to Pandoc. However, **you still need to install Pandoc itself** as described above.

## Troubleshooting

### Error: "Pandoc is not installed or not found in PATH"

**Cause:** Pandoc is not installed or not in your system PATH.

**Solution:**
1. Install Pandoc using the instructions above
2. Restart your terminal/command prompt
3. Verify installation with `pandoc --version`
4. Try starting the application again

### Error: "pypandoc is not installed"

**Cause:** The pypandoc Python package is missing.

**Solution:**
```bash
pip install pypandoc
```

### Pandoc installed but still getting errors

**Solution:**
1. Ensure Pandoc is in your PATH:
   - Windows: Check `Environment Variables` → `System Variables` → `Path`
   - Linux/Mac: Add to `~/.bashrc` or `~/.zshrc`: `export PATH=$PATH:/usr/local/bin`
2. Restart your terminal
3. Try again

## Alternative: Download Pandoc via pypandoc (Not Recommended)

If you cannot install Pandoc system-wide, pypandoc can download a local copy:

```python
import pypandoc
pypandoc.download_pandoc()
```

However, this is **not recommended** as it requires additional configuration and may not work reliably.

## Need Help?

- Official Pandoc Documentation: https://pandoc.org/
- Pandoc Installation Guide: https://pandoc.org/installing.html
- pypandoc Documentation: https://github.com/NicklasTegner/pypandoc

## Starting the Application

Once Pandoc is installed, start the application:

```bash
python main.py
```

You should see:
```
============================================================
🔍 Validating Requirements...
============================================================
✅ Pandoc found: version 2.x.x

============================================================
🚀 Starting Markdown Content Processor
============================================================
```

If you see the green checkmark (✅), you're ready to go!

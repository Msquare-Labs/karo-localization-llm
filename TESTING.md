# Local Testing Guide

## Quick Test

I've created a simple test script for you. Here's how to use it:

### 1. Make sure you have uv installed and synced
```bash
uv sync
```

### 2. Run the test script
```bash
./test_local.sh <path-to-your-xcstrings-folder> <your-gemini-api-key>
```

**Example:**
```bash
./test_local.sh ./Tasks AIzaSyD...your-api-key-here
```

### What the script does:
1. ✅ Validates your folder exists and contains `.xcstrings` files
2. 📋 Detects missing translations
3. 🤖 Calls Gemini AI to translate them
4. 📝 Applies translations to your `.xcstrings` files
5. 🌐 Adds regional variants (en-AU, pt-BR, etc.)
6. 🧹 Cleans up temporary files

### Alternative: Manual Testing

If you prefer to run each step manually:

```bash
# Step 1: Detect missing translations
uv run python "enforce_100%_translation.py" --folder ./YourFolder --languages "ar,de,es,fr"

# Step 2: Translate (you'll see llm_translation_task_*.json files created)
uv run python translate_with_llm.py --api-key "YOUR_API_KEY"

# Step 3: Apply translations
uv run python apply_translations.py --folder ./YourFolder

# Step 4: Add regional variants
uv run python add_regional_variants.py --folder ./YourFolder

# Cleanup
rm llm_translation_task_*.json
```

## What to provide:

1. **Path to your .xcstrings folder** - The folder containing your `.xcstrings` files (e.g., `./Tasks`, `./Resources/Localizations`)

2. **Gemini API Key** - Your Google Gemini API key

## Expected Output:

The script will:
- Show you how many `.xcstrings` files were found
- Tell you how many strings need translation
- Process each batch with Gemini
- Apply the translations
- Add regional variants
- Clean up temporary files

Your `.xcstrings` files will be updated in place with the new translations!

#!/bin/bash
# Simple test script to verify the localization workflow
# Usage: ./test_local.sh <path-to-xcstrings-folder> <gemini-api-key>

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

if [ "$#" -ne 2 ]; then
    echo -e "${RED}Usage: $0 <path-to-xcstrings-folder> <gemini-api-key>${NC}"
    echo ""
    echo "Example:"
    echo "  $0 ./Tasks YOUR_GEMINI_API_KEY"
    exit 1
fi

FOLDER_PATH="$1"
GEMINI_API_KEY="$2"
LANGUAGES="ar,de,es,fr,ja,nl,pt,zh-Hans,zh-Hant,it,ko,sv,hi,pl,tr,ru"

echo -e "${BLUE}🧪 Testing LLM-Powered Localization Workflow${NC}"
echo "================================================"
echo "Folder: $FOLDER_PATH"
echo "Languages: $LANGUAGES"
echo ""

# Check if folder exists
if [ ! -d "$FOLDER_PATH" ]; then
    echo -e "${RED}❌ Error: Folder '$FOLDER_PATH' does not exist${NC}"
    exit 1
fi

# Check for .xcstrings files
XCSTRINGS_COUNT=$(find "$FOLDER_PATH" -name "*.xcstrings" | wc -l | tr -d ' ')
if [ "$XCSTRINGS_COUNT" -eq 0 ]; then
    echo -e "${RED}❌ Error: No .xcstrings files found in '$FOLDER_PATH'${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Found $XCSTRINGS_COUNT .xcstrings file(s)${NC}"
echo ""

# Step 1: Detect missing translations
echo -e "${BLUE}📋 Step 1: Detecting missing translations...${NC}"
python3 "enforce_100%_translation.py" --folder "$FOLDER_PATH" --languages "$LANGUAGES"
# Check if translation files were created
TASK_FILES=$(ls llm_translation_task_*.json 2>/dev/null | wc -l | tr -d ' ')
if [ "$TASK_FILES" -eq 0 ]; then
    echo -e "${GREEN}✅ All translations are complete! No work needed.${NC}"
    exit 0
fi

echo -e "${GREEN}✅ Found $TASK_FILES translation task(s) to process${NC}"
echo ""

# Step 2: Translate with Gemini
echo -e "${BLUE}🤖 Step 2: Translating with Gemini AI...${NC}"
python3 translate_with_llm.py --api-key "$GEMINI_API_KEY"
echo ""

# Step 3: Apply translations
echo -e "${BLUE}📝 Step 3: Applying translations...${NC}"
python3 apply_translations.py --folder "$FOLDER_PATH"
echo ""

# Step 4: Add regional variants
echo -e "${BLUE}🌐 Step 4: Adding regional variants...${NC}"
python3 add_regional_variants.py --folder "$FOLDER_PATH"
echo ""

# Cleanup
echo -e "${BLUE}🧹 Cleaning up temporary files...${NC}"
rm -f llm_translation_task_*.json

echo ""
echo "================================================"
echo -e "${GREEN}🎉 Localization workflow completed successfully!${NC}"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Review the updated .xcstrings files in: $FOLDER_PATH"
echo "2. Check the translations for accuracy"
echo "3. Commit the changes to your repository"

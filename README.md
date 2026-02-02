# 🌍 LLM-Powered Localization GitHub Action

Automatically translate `.xcstrings` localization files using Google Gemini AI. This GitHub Action detects missing translations, uses AI to generate them, and creates a pull request with the results.

## ✨ Features

- 🤖 **AI-Powered Translation**: Uses Google Gemini (`gemini-3-flash-preview`) for high-quality translations
- 🌐 **Multi-Language Support**: Supports 16 languages out of the box
- 🔄 **Regional Variants**: Automatically adds regional variants (en-AU, pt-BR, es-419, etc.)
- 📝 **Plural Forms**: Handles complex plural forms correctly
- 🔀 **Pull Request Workflow**: Creates PRs for easy review before merging
- ⚡ **Zero Configuration**: Works with sensible defaults

## 📋 Prerequisites

- Repository with `.xcstrings` localization files (Xcode String Catalogs)
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

## 🚀 Quick Start

### 1. Add Gemini API Key to Secrets

1. Go to your repository **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `GEMINI_API_KEY`
4. Value: Your Gemini API key

### 2. Create Workflow File

Create `.github/workflows/localization.yml`:

```yaml
name: Auto-Translate Localizations

on:
  workflow_dispatch:
    inputs:
      source-folder:
        description: 'Path to folder containing .xcstrings files'
        required: true
        default: 'Resources/Localizations'

jobs:
  translate:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Run localization
        uses: YOUR-USERNAME/karo-localization-llm@v1
        with:
          gemini-api-key: ${{ secrets.GEMINI_API_KEY }}
          source-folder: ${{ inputs.source-folder }}
```

### 3. Run the Workflow

1. Go to **Actions** tab in your repository
2. Select **Auto-Translate Localizations**
3. Click **Run workflow**
4. Enter the path to your `.xcstrings` folder
5. Click **Run workflow**

The action will create a pull request with the translations!

## 🌐 Supported Languages

The action translates to the following languages by default:

- Arabic (ar)
- German (de)
- Spanish (es)
- French (fr)
- Japanese (ja)
- Dutch (nl)
- Portuguese (pt)
- Chinese Simplified (zh-Hans)
- Chinese Traditional (zh-Hant)
- Italian (it)
- Korean (ko)
- Swedish (sv)
- Hindi (hi)
- Polish (pl)
- Turkish (tr)
- Russian (ru)

### Regional Variants

The action also adds these regional variants automatically:

- English: en-AU, en-IN, en-GB
- Spanish: es-419 (Latin America)
- Portuguese: pt-BR, pt-PT
- French: fr-CA

## 📖 How It Works

1. **Analyze**: Scans `.xcstrings` files for missing translations
2. **Generate**: Creates translation tasks and sends them to Gemini AI
3. **Apply**: Applies AI-generated translations back to `.xcstrings` files
4. **Enhance**: Adds regional language variants
5. **Review**: Creates a pull request for human review

## 🔧 Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `gemini-api-key` | ✅ Yes | - | Google Gemini API key |
| `source-folder` | ✅ Yes | - | Path to folder containing `.xcstrings` files |

## 📤 Outputs

| Output | Description |
|--------|-------------|
| `translations-count` | Number of lines changed |
| `pr-number` | Pull request number created |

## 🎯 Example Usage

### Basic Usage

```yaml
- uses: YOUR-USERNAME/karo-localization-llm@v1
  with:
    gemini-api-key: ${{ secrets.GEMINI_API_KEY }}
    source-folder: 'MyApp/Resources/Localizations'
```

### With Output Capture

```yaml
- name: Translate localizations
  id: translate
  uses: YOUR-USERNAME/karo-localization-llm@v1
  with:
    gemini-api-key: ${{ secrets.GEMINI_API_KEY }}
    source-folder: 'Resources/Localizations'

- name: Comment on PR
  run: |
    echo "Translated ${{ steps.translate.outputs.translations-count }} lines"
    echo "PR #${{ steps.translate.outputs.pr-number }} created"
```

## ⚠️ Important Notes

- **Review Translations**: AI-generated translations should always be reviewed by native speakers
- **API Costs**: Google Gemini API usage may incur costs depending on your usage
- **Rate Limits**: The action includes retry logic and rate limiting handling
- **Fail-Fast**: If any translation fails, the entire workflow fails to ensure consistency

## 🛠️ Development

### Local Testing

This project uses `uv` for dependency management. To test the scripts locally:

```bash
# Install dependencies with uv
uv sync

# Step 1: Find missing translations
uv run python enforce_100%_translation.py --folder ./Tasks --languages "ar,de,es,fr"

# Step 2: Translate with Gemini
export GEMINI_API_KEY="your-api-key"
uv run python translate_with_llm.py --api-key "$GEMINI_API_KEY"

# Step 3: Apply translations
uv run python apply_translations.py --folder ./Tasks

# Step 4: Add regional variants
uv run python add_regional_variants.py --folder ./Tasks
```

Alternatively, using pip:

```bash
# Install dependencies
pip install -r requirements.txt

# Then run the same commands without 'uv run'
python enforce_100%_translation.py --folder ./Tasks --languages "ar,de,es,fr"
# ... etc
```

## 📄 License

MIT License - feel free to use this in your projects!

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 💬 Support

If you encounter any issues, please [open an issue](https://github.com/YOUR-USERNAME/karo-localization-llm/issues) on GitHub.

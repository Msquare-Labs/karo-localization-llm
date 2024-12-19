import os
import json
import copy


def estimate_tokens(text):
    # Rough estimate: 1 token per 4 characters
    return len(text) // 4 + 1


def is_translation_missing(translation):
    if not translation:
        return True
    if isinstance(translation, dict):
        if 'stringUnit' in translation:
            # Check for empty value or needs_review state
            return (translation['stringUnit'].get('value', '') == '' or 
                   translation['stringUnit'].get('state') == 'needs_review')
        elif 'variations' in translation:
            return all(is_translation_missing(var) for var in translation['variations'].get('plural', {}).values())
    return False


def check_translations(folder_path, languages):
    missing_translations = {}
    file_structures = {}

    for filename in os.listdir(folder_path):
        if filename.endswith('.xcstrings'):
            file_path = os.path.join(folder_path, filename)

            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            file_structures[filename] = data

            for string_key, string_data in data.get('strings', {}).items():
                en_value = string_key
                if isinstance(string_data, dict) and 'localizations' in string_data:
                    en_localization = string_data['localizations'].get('en', {})
                    if isinstance(en_localization, dict):
                        if 'stringUnit' in en_localization:
                            en_value = en_localization['stringUnit'].get('value') or string_key
                        elif 'variations' in en_localization:
                            en_value = {
                                form: variation['stringUnit'].get('value', string_key)
                                for form, variation in en_localization['variations'].get('plural', {}).items()
                            }
                    elif isinstance(en_localization, str):
                        en_value = en_localization

                missing_langs = [
                    lang for lang in languages
                    if lang not in string_data.get('localizations', {})
                    or is_translation_missing(string_data['localizations'].get(lang))
                ]

                if missing_langs:
                    if filename not in missing_translations:
                        missing_translations[filename] = {}
                    missing_translations[filename][string_key] = {
                        "en": en_value,
                        "missing_langs": missing_langs
                    }

    return missing_translations, file_structures


def create_llm_schemas(missing_translations, languages, max_tokens=4000):
    llm_schemas = []
    current_schema = {
        "instructions": "Please provide translations for the missing languages. Use the English version as a reference. For plural forms, provide appropriate translations for each form if applicable.",
        "translations": {}
    }
    current_tokens = estimate_tokens(json.dumps(current_schema["instructions"]))

    for filename, strings in missing_translations.items():
        for string_key, data in strings.items():
            new_entry = {
                "en": data["en"],
                "missing_translations": {lang: "" for lang in data["missing_langs"]}
            }
            new_entry_tokens = estimate_tokens(json.dumps(new_entry)) * (
                        len(languages) + 1)  # Estimating tokens for all languages

            if current_tokens + new_entry_tokens > max_tokens:
                llm_schemas.append(current_schema)
                current_schema = {
                    "instructions": "Please provide translations for the missing languages. Use the English version as a reference. For plural forms, provide appropriate translations for each form if applicable.",
                    "translations": {}
                }
                current_tokens = estimate_tokens(json.dumps(current_schema["instructions"]))

            current_schema["translations"][f"{filename}:{string_key}"] = new_entry
            current_tokens += new_entry_tokens

    if current_schema["translations"]:
        llm_schemas.append(current_schema)

    return llm_schemas


def save_llm_schemas(llm_schemas):
    for i, schema in enumerate(llm_schemas):
        filename = f'llm_translation_task_{i + 1}.json'
        with open(filename, 'w', encoding='utf-8') as outfile:
            json.dump(schema, outfile, indent=2, ensure_ascii=False)
        print(f"Created {filename} for LLM processing")


# Main execution
folder_path = 'Frameworks'
languages_to_check = [
    'ar', 'de', 'es', 'fr', 'ja', 'nl', 'pt', 'zh-Hans', 'zh-Hant',
    'it', 'ko', 'sv', 'hi', 'pl', 'tr'
]

# Check for missing translations
missing_translations, file_structures = check_translations(folder_path, languages_to_check)

# Create schemas for LLM, split into files of approximately 4000 tokens each
llm_schemas = create_llm_schemas(missing_translations, languages_to_check, max_tokens=6000)

# Save the LLM schemas to files
save_llm_schemas(llm_schemas)

print(f"Created {len(llm_schemas)} files for LLM processing")
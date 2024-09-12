import os
import json
import copy


def estimate_tokens(text):
    # Rough estimate: 1 token per 4 characters
    return len(text) // 4 + 1


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
                        en_value = en_localization.get('stringUnit', {}).get('value') or en_localization.get('value',
                                                                                                             string_key)
                    elif isinstance(en_localization, str):
                        en_value = en_localization

                missing_langs = [lang for lang in languages if lang not in string_data.get('localizations', {})]

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
        "instructions": "Please provide translations for the missing languages. Use the English version as a reference.",
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
                    "instructions": "Please provide translations for the missing languages. Use the English version as a reference.",
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


def update_original_files(file_structures, llm_translations, folder_path):
    for key, translations in llm_translations["translations"].items():
        filename, string_key = key.split(':', 1)
        file_data = file_structures[filename]
        if isinstance(file_data["strings"][string_key], dict) and "localizations" in file_data["strings"][string_key]:
            for lang, translation in translations["missing_translations"].items():
                if translation:  # Only update if a translation was provided
                    file_data["strings"][string_key]["localizations"][lang] = {
                        "stringUnit": {
                            "state": "translated",
                            "value": translation
                        }
                    }
        else:
            file_data["strings"][string_key] = {
                "localizations": {
                    lang: {
                        "stringUnit": {
                            "state": "translated",
                            "value": translation if translation else string_key
                        }
                    } for lang, translation in translations["missing_translations"].items()
                }
            }
            file_data["strings"][string_key]["localizations"]["en"] = {
                "stringUnit": {
                    "state": "translated",
                    "value": translations["en"]
                }
            }

    for filename, data in file_structures.items():
        output_path = os.path.join(folder_path, filename)
        with open(output_path, 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile, indent=2, ensure_ascii=False)
        print(f"Updated {filename} with new translations")


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
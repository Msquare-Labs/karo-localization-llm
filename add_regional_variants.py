import json
import os


def copy_translations(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    language_variants = {
        "en": [
            ("en-AU", "English (Australia)"),
            ("en-IN", "English (India)"),
            ("en-GB", "English (United Kingdom)")
        ],
        "es": [
            ("es-419", "Spanish (Latin America)")
        ],
        "pt": [
            ("pt-BR", "Portuguese (Brazil)"),
            ("pt-PT", "Portuguese (Portugal)")
        ],
        "fr": [
            ("fr-CA", "French (Canada)")
        ]
    }

    for key, value in data['strings'].items():
        localizations = value['localizations']

        for base_lang, variants in language_variants.items():
            if base_lang in localizations:
                base_translation = localizations[base_lang]

                for code, name in variants:
                    if 'variations' in base_translation:
                        # Handle plural variations
                        localizations[code] = {
                            "variations": {
                                "plural": {
                                    plural_key: {
                                        "stringUnit": plural_value["stringUnit"].copy()
                                    }
                                    for plural_key, plural_value in base_translation["variations"]["plural"].items()
                                }
                            }
                        }
                    elif 'stringUnit' in base_translation:
                        # Handle regular translations
                        localizations[code] = {
                            "stringUnit": base_translation["stringUnit"].copy()
                        }

    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def process_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.xcstrings'):
            file_path = os.path.join(folder_path, filename)
            print(f"Processing file: {file_path}")
            copy_translations(file_path)


# Main execution
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Add regional variants to .xcstrings files')
    parser.add_argument('--folder', required=True, help='Path to folder containing .xcstrings files')
    
    args = parser.parse_args()
    
    folder_path = args.folder
    
    print(f"Adding regional variants to files in: {folder_path}")
    
    # Validate folder exists
    if not os.path.exists(folder_path):
        print(f"❌ Error: Folder '{folder_path}' does not exist")
        exit(1)
    
    if not os.path.isdir(folder_path):
        print(f"❌ Error: '{folder_path}' is not a directory")
        exit(1)
    
    process_folder(folder_path)
    print("✅ Regional variants added successfully")
import json
import os
import glob

def update_xcstrings_with_translations(xcstrings_folder):
    # Get all llm_translation_task_*.json files in the current directory
    translation_files = glob.glob('llm_translation_task_*.json')

    # Keep track of modified .xcstrings files
    modified_xcstrings = {}

    for translation_file in translation_files:
        print(f"Processing {translation_file}...")

        # Load the translations
        with open(translation_file, 'r', encoding='utf-8') as f:
            file_content = json.load(f)

        # Check if the file uses the new format
        if 'translations' in file_content:
            translations = file_content['translations']
        else:
            translations = file_content

        # Iterate through each translation entry
        for key, translations_data in translations.items():
            # Split the key to get the filename and the string key
            filename, string_key = key.split(':', 1)
            xcstrings_path = os.path.join(xcstrings_folder, filename)

            # Load the .xcstrings file if not already loaded
            if filename not in modified_xcstrings:
                with open(xcstrings_path, 'r', encoding='utf-8') as f:
                    modified_xcstrings[filename] = json.load(f)

            # Update the translations in the .xcstrings data
            if string_key in modified_xcstrings[filename]['strings']:
                if 'localizations' not in modified_xcstrings[filename]['strings'][string_key]:
                    modified_xcstrings[filename]['strings'][string_key]['localizations'] = {}

                # Handle both original and new format
                if 'missing_translations' in translations_data:
                    for lang, translation in translations_data['missing_translations'].items():
                        # Check if source has variations structure
                        source_entry = modified_xcstrings[filename]['strings'][string_key]['localizations'].get('en', {})
                        if 'variations' in source_entry:
                            # Mirror the English structure with variations
                            modified_xcstrings[filename]['strings'][string_key]['localizations'][lang] = {
                                "variations": {
                                    "plural": {
                                        "one": {
                                            "stringUnit": {
                                                "state": "translated",
                                                "value": translation["one"]
                                            }
                                        },
                                        "other": {
                                            "stringUnit": {
                                                "state": "translated",
                                                "value": translation["other"]
                                            }
                                        }
                                    }
                                }
                            }
                        else:
                            # Regular translation without variations
                            modified_xcstrings[filename]['strings'][string_key]['localizations'][lang] = {
                                "stringUnit": {
                                    "state": "translated",
                                    "value": translation
                                }
                            }
                else:
                    for lang, translation in translations_data.items():
                        if lang != 'en':  # Skip English as it's not a translation
                            # Check if source has variations structure
                            source_entry = modified_xcstrings[filename]['strings'][string_key]['localizations'].get('en', {})
                            if 'variations' in source_entry:
                                # Mirror the English structure with variations
                                modified_xcstrings[filename]['strings'][string_key]['localizations'][lang] = {
                                    "variations": {
                                        "plural": {
                                            "one": {
                                                "stringUnit": {
                                                    "state": "translated",
                                                    "value": translation["one"]
                                                }
                                            },
                                            "other": {
                                                "stringUnit": {
                                                    "state": "translated",
                                                    "value": translation["other"]
                                                }
                                            }
                                        }
                                    }
                                }
                            else:
                                # Regular translation without variations
                                modified_xcstrings[filename]['strings'][string_key]['localizations'][lang] = {
                                    "stringUnit": {
                                        "state": "translated",
                                        "value": translation
                                    }
                                }

            print(f"Updated translations for '{string_key}' in {filename}")

    # Save all modified .xcstrings files
    for filename, xcstrings_data in modified_xcstrings.items():
        xcstrings_path = os.path.join(xcstrings_folder, filename)
        with open(xcstrings_path, 'w', encoding='utf-8') as f:
            json.dump(xcstrings_data, f, ensure_ascii=False, indent=2)
        print(f"Saved updated {filename}")

    print("All translations have been updated.")

# Main execution
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Apply LLM translations to .xcstrings files')
    parser.add_argument('--folder', required=True, help='Path to folder containing .xcstrings files')
    
    args = parser.parse_args()
    
    xcstrings_folder = args.folder
    
    print(f"Applying translations to files in: {xcstrings_folder}")
    
    # Validate folder exists
    if not os.path.exists(xcstrings_folder):
        print(f"❌ Error: Folder '{xcstrings_folder}' does not exist")
        exit(1)
    
    if not os.path.isdir(xcstrings_folder):
        print(f"❌ Error: '{xcstrings_folder}' is not a directory")
        exit(1)
    
    update_xcstrings_with_translations(xcstrings_folder)
#!/usr/bin/env python3
"""
Test script to verify the localization workflow end-to-end.
"""

import os
import sys
import json
import shutil
import subprocess
import tempfile

def run_command(cmd, cwd=None):
    """Run a command and return output."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout

def test_workflow():
    """Test the complete localization workflow."""
    print("🧪 Testing LLM-Powered Localization Workflow")
    print("=" * 50)
    
    # Get the project root directory (parent of tests/)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Change to project root
    original_dir = os.getcwd()
    os.chdir(project_root)
    
    try:
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = os.path.join(tmpdir, "test_xcstrings")
            shutil.copytree("tests/sample_xcstrings", test_dir)
            
            print(f"\n📁 Test directory: {test_dir}")
            
            # Step 1: Test enforce_100%_translation.py
            print("\n1️⃣ Testing enforce_100%_translation.py...")
            run_command([
                "python3", "enforce_100%_translation.py",
                "--folder", test_dir,
                "--languages", "ar,de,es,fr"
            ])
            
            # Check if translation task files were created
            task_files = [f for f in os.listdir(".") if f.startswith("llm_translation_task_")]
            if not task_files:
                print("❌ No translation task files created")
                sys.exit(1)
            print(f"✅ Created {len(task_files)} translation task file(s)")
            
            # Step 2: Verify task file structure
            print("\n2️⃣ Verifying task file structure...")
            with open(task_files[0], 'r') as f:
                task_data = json.load(f)
            
            if 'instructions' not in task_data or 'translations' not in task_data:
                print("❌ Task file has incorrect structure")
                sys.exit(1)
            print(f"✅ Task file structure is valid")
            print(f"   Found {len(task_data['translations'])} strings to translate")
            
            # Step 3: Mock LLM translation (simulate what Gemini would do)
            print("\n3️⃣ Simulating LLM translation...")
            for key, value in task_data['translations'].items():
                # Simple mock translation (just add language code prefix)
                for lang in value['missing_translations'].keys():
                    if isinstance(value['en'], dict):
                        # Handle plural forms
                        task_data['translations'][key]['missing_translations'][lang] = {
                            'one': f"[{lang}] {value['en']['one']}",
                            'other': f"[{lang}] {value['en']['other']}"
                        }
                    else:
                        # Handle simple strings
                        task_data['translations'][key]['missing_translations'][lang] = f"[{lang}] {value['en']}"
            
            # Save mock translations
            with open(task_files[0], 'w') as f:
                json.dump(task_data, f, indent=2, ensure_ascii=False)
            print("✅ Mock translations generated")
            
            # Step 4: Test apply_translations.py
            print("\n4️⃣ Testing apply_translations.py...")
            run_command([
                "python3", "apply_translations.py",
                "--folder", test_dir
            ])
            print("✅ Translations applied")
            
            # Step 5: Verify translations were applied
            print("\n5️⃣ Verifying translations were applied...")
            with open(os.path.join(test_dir, "Localizable.xcstrings"), 'r') as f:
                updated_data = json.load(f)
            
            # Check if translations were added
            sample_string = updated_data['strings']['Hello, World!']
            if 'ar' not in sample_string['localizations']:
                print("❌ Translations were not applied")
                sys.exit(1)
            print("✅ Translations successfully applied to .xcstrings file")
            
            # Step 6: Test add_regional_variants.py
            print("\n6️⃣ Testing add_regional_variants.py...")
            run_command([
                "python3", "add_regional_variants.py",
                "--folder", test_dir
            ])
            print("✅ Regional variants added")
            
            # Step 7: Verify regional variants
            print("\n7️⃣ Verifying regional variants...")
            with open(os.path.join(test_dir, "Localizable.xcstrings"), 'r') as f:
                final_data = json.load(f)
            
            sample_string = final_data['strings']['Hello, World!']
            if 'en-AU' not in sample_string['localizations']:
                print("❌ Regional variants were not added")
                sys.exit(1)
            print("✅ Regional variants successfully added")
            
            # Cleanup
            print("\n🧹 Cleaning up...")
            for task_file in task_files:
                os.remove(task_file)
            
            print("\n" + "=" * 50)
            print("🎉 All tests passed!")
            print("=" * 50)
    
    finally:
        # Restore original directory
        os.chdir(original_dir)

if __name__ == '__main__':
    try:
        test_workflow()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

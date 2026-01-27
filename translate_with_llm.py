#!/usr/bin/env python3
"""
Translate missing localization strings using Google Gemini AI.
Reads llm_translation_task_*.json files and populates translations.
"""

import json
import glob
import os
import sys
import time
import argparse
from google import genai
from google.genai import types


def translate_batch(client, translation_data, batch_number, total_batches):
    """
    Translate a single batch of strings using Gemini.
    
    Args:
        client: Configured Gemini client
        translation_data: Dictionary containing instructions and translations
        batch_number: Current batch number (for logging)
        total_batches: Total number of batches
    
    Returns:
        Dictionary with completed translations
    """
    print(f"  Processing batch {batch_number}/{total_batches}...")
    
    # Create the prompt
    prompt = f"""{translation_data['instructions']}

Please translate the following strings. Return ONLY a valid JSON object with the same structure, where each "missing_translations" object is filled with the appropriate translations.

For plural forms (when "en" is an object with "one" and "other" keys), provide translations for both forms in the target language's plural rules.

Input:
{json.dumps(translation_data['translations'], indent=2, ensure_ascii=False)}

Return only the JSON object with completed translations, no additional text or explanation."""

    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # Call Gemini API using new SDK
            response = client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    top_p=0.95,
                    top_k=40,
                )
            )
            
            # Extract and parse the response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                # Find the actual JSON content
                lines = response_text.split('\n')
                json_lines = []
                in_code_block = False
                
                for line in lines:
                    if line.startswith('```'):
                        in_code_block = not in_code_block
                        continue
                    if in_code_block or not line.startswith('```'):
                        json_lines.append(line)
                
                response_text = '\n'.join(json_lines).strip()
            
            # Parse JSON response
            translated_data = json.loads(response_text)
            
            # Validate the response has the expected structure
            if not isinstance(translated_data, dict):
                raise ValueError("Response is not a dictionary")
            
            print(f"  ✅ Batch {batch_number}/{total_batches} completed")
            return translated_data
            
        except json.JSONDecodeError as e:
            print(f"  ⚠️  JSON parsing error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"  ❌ Failed to parse response after {max_retries} attempts")
                print(f"  Response was: {response_text[:200]}...")
                raise
                
        except Exception as e:
            print(f"  ⚠️  API error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                print(f"  ❌ Failed after {max_retries} attempts")
                raise


def main():
    parser = argparse.ArgumentParser(description='Translate localization strings using Google Gemini AI')
    parser.add_argument('--api-key', required=True, help='Google Gemini API key')
    parser.add_argument('--model', default='gemini-2.0-flash-exp', help='Gemini model to use (default: gemini-2.0-flash-exp)')
    
    args = parser.parse_args()
    
    # Configure Gemini client with new SDK
    print("🤖 Configuring Gemini AI...")
    client = genai.Client(api_key=args.api_key)
    print(f"✅ Using model: {args.model}")
    
    # Find all translation task files
    translation_files = sorted(glob.glob('llm_translation_task_*.json'))
    
    if not translation_files:
        print("❌ No translation task files found (llm_translation_task_*.json)")
        sys.exit(1)
    
    print(f"\n📋 Found {len(translation_files)} translation task file(s)")
    
    total_batches = len(translation_files)
    
    # Process each file
    for i, filename in enumerate(translation_files, 1):
        print(f"\n🔄 Processing {filename}...")
        
        try:
            # Load the translation task
            with open(filename, 'r', encoding='utf-8') as f:
                task_data = json.load(f)
            
            # Translate the batch
            translated_data = translate_batch(client, task_data, i, total_batches)
            
            # Update the file with translations
            task_data['translations'] = translated_data
            
            # Save the updated file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(task_data, f, indent=2, ensure_ascii=False)
            
            print(f"  💾 Saved translations to {filename}")
            
            # Small delay between batches to avoid rate limiting
            if i < total_batches:
                time.sleep(1)
                
        except Exception as e:
            print(f"\n❌ Error processing {filename}: {e}")
            print("Translation workflow failed.")
            sys.exit(1)
    
    print(f"\n✅ Successfully translated all {total_batches} batch(es)!")


if __name__ == '__main__':
    main()

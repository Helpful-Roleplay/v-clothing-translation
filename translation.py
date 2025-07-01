from deep_translator import GoogleTranslator
from deep_translator.exceptions import TranslationNotFound
import json
import os

def ensure_output_dir(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

def load_json(file_path):
    print(f"Loading JSON file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            print(f"JSON file {os.path.basename(file_path)} loaded successfully")
            return data
    except Exception as e:
        print(f"Error loading {os.path.basename(file_path)}: {str(e)}")
        return None

def save_json(data, file_path):
    print(f"Saving translated JSON to: {file_path}")
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"JSON file {os.path.basename(file_path)} saved successfully")
    except Exception as e:
        print(f"Error saving {os.path.basename(file_path)}: {str(e)}")

def translate_json(data, log_file):
    translator = GoogleTranslator(source='en', target='sv')
    print("Starting translation to Swedish...")
    
    def recursive_translate(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "Localized" and isinstance(value, str) and value != "NULL":
                    try:
                        original = value
                        translated = translator.translate(value)
                        print(f"Translating: '{original}' -> '{translated}'")
                        obj[key] = translated
                    except TranslationNotFound as e:
                        print(f"Translation failed for '{value}' in {os.path.basename(log_file)}: {str(e)}")
                        with open(log_file, 'a', encoding='utf-8') as f:
                            f.write(f"Failed to translate '{value}' in {os.path.basename(log_file)}: {str(e)}\n")
                        obj[key] = value
                elif key == "Localized" and value == "NULL":
                    print(f"Skipping translation for 'NULL' in Localized field")
                elif isinstance(value, dict):
                    recursive_translate(value)
    
    recursive_translate(data)
    print("Translation completed")
    return data

def main(input_dir, output_dir):
    print("Starting JSON translation process")
    ensure_output_dir(output_dir)
    log_file = os.path.join(output_dir, "translation_errors.log")
    print(f"Logging translation errors to: {log_file}")
    
    json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
    print(f"Found {len(json_files)} JSON files to process")
    
    for json_file in json_files:
        input_path = os.path.join(input_dir, json_file)
        output_path = os.path.join(output_dir, json_file)
        
        print(f"\nProcessing file: {json_file}")
        data = load_json(input_path)
        if data is None:
            print(f"Skipping {json_file} due to load error")
            continue
        translated_data = translate_json(data, log_file)
        save_json(translated_data, output_path)
    
    print("All JSON files processed successfully")

if __name__ == "__main__":
    input_dir = "v-clothingnames"
    output_dir = "output"
    main(input_dir, output_dir)
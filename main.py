import os
import json
import sys
import pytesseract
from PIL import Image
import ollama


OLLAMA_MODEL = "llama3"
CHAT_DIR = "saved_chats"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def ensure_chat_dir():
    if not os.path.exists(CHAT_DIR):
        os.makedirs(CHAT_DIR)

def extract_text_from_images(image_paths):
    full_text = ""
    print("Starting OCR processing...")
    
    for path in image_paths:
        clean_path = path.strip()
        if os.path.exists(clean_path):
            try:
                print(f"Processing: {clean_path}")
                img = Image.open(clean_path)
                text = pytesseract.image_to_string(img)
                full_text += f"\n--- CONTENT FROM {os.path.basename(clean_path)} ---\n{text}\n"
            except Exception as e:
                print(f"Error processing {clean_path}: {e}")
        else:
            print(f"File not found: {clean_path}")
            
    return full_text

def save_chat(filename, history):
    ensure_chat_dir()
    filepath = os.path.join(CHAT_DIR, filename)
    if not filepath.endswith(".json"):
        filepath += ".json"
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4)
        print(f"Chat saved successfully to {filepath}")
    except Exception as e:
        print(f"Error saving chat: {e}")

def load_chat_file(filename):
    filepath = os.path.join(CHAT_DIR, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading chat: {e}")
        return None

def chat_session(history):
    print("\n--- CHAT SESSION STARTED ---")
    print("Type 'save' to save the chat.")
    print("Type 'exit' to return to menu.")
    
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() == 'exit':
            break
        
        if user_input.lower() == 'save':
            filename = input("Enter filename to save: ")
            save_chat(filename, history)
            continue

        # Append user message
        history.append({'role': 'user', 'content': user_input})
        
        print("AI is thinking...")
        try:
            response_stream = ollama.chat(model=OLLAMA_MODEL, messages=history, stream=True)
            
            print("AI: ", end="", flush=True)
            full_response = ""
            
            for chunk in response_stream:
                content = chunk['message']['content']
                print(content, end="", flush=True)
                full_response += content
            
            print() # Newline after response
            
            # Append AI response to history
            history.append({'role': 'assistant', 'content': full_response})
            
        except Exception as e:
            print(f"Error communicating with Ollama: {e}")

def create_new_session():
    print("Enter image paths separated by comma (e.g., img1.png, /path/to/img2.jpg):")
    raw_input = input("> ")
    paths = raw_input.split(',')
    
    scanned_text = extract_text_from_images(paths)
    
    if not scanned_text.strip():
        print("No text extracted. Aborting session.")
        input("Press Enter to continue...")
        return

    print("Text extracted successfully.")
    
    system_prompt = (
        "You are a helpful assistant. "
        "I will provide you with raw text extracted from scanned documents. "
        "Your goal is to answer questions strictly based on this context. "
        "Here is the document content:\n\n" + scanned_text
    )
    
    history = [{'role': 'system', 'content': system_prompt}]
    chat_session(history)

def load_existing_session():
    ensure_chat_dir()
    files = [f for f in os.listdir(CHAT_DIR) if f.endswith(".json")]
    
    if not files:
        print("No saved chats found.")
        input("Press Enter to continue...")
        return

    print("Available chats:")
    for i, f in enumerate(files):
        print(f"{i + 1}. {f}")
    
    try:
        choice = int(input("Select a number: ")) - 1
        if 0 <= choice < len(files):
            history = load_chat_file(files[choice])
            if history:
                chat_session(history)
        else:
            print("Invalid selection.")
    except ValueError:
        print("Invalid input.")

def main():
    while True:
        clear_screen()
        print("=== AI DOCUMENT ASSISTANT ===")
        print(f"Model: {OLLAMA_MODEL}")
        print("1. New Session (Scan Images)")
        print("2. Load Saved Session")
        print("3. Exit")
        
        choice = input("Select an option: ")
        
        if choice == '1':
            create_new_session()
        elif choice == '2':
            load_existing_session()
        elif choice == '3':
            print("Exiting...")
            sys.exit()
        else:
            print("Invalid choice. Try again.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
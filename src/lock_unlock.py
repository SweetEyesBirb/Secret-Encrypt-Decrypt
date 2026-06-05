import json
import sys
import questionary
from cryptography.fernet import InvalidToken

from src.utils.utils import ask_for_path_and_validate, ask_for_key_and_validate
from src.scrambler import _resolve_fernet


# ══════════════════════════════════════════════════════════════════════════════
# Core lock/unlock functions
# ══════════════════════════════════════════════════════════════════════════════

def lock_data_to_json(input_txt: str, output_locked_file: str, 
                      fkey: str | None = None, key_file: str | None = None) -> None:
    """
    Lock a text file by encrypting it with Fernet and storing as JSON.
    
    Args:
        input_txt: Path to the input text file
        output_locked_file: Path to the output locked file
        fkey: Inline Fernet key (raw or passphrase)
        key_file: Path to a file containing the Fernet key
    """
    try:
        # Resolve the Fernet cipher
        cipher = _resolve_fernet(fkey=fkey, key_file=key_file)
        
        # Read the entire raw text file exactly as it is (newlines intact)
        with open(input_txt, "r", encoding="utf-8") as file:
            raw_text = file.read()

        # Structure it into a clean JSON layout
        data_payload = {
            "file_type": "secure_hash_storage",
            "content": raw_text
        }
        json_string = json.dumps(data_payload, indent=4)

        # Encrypt the structured JSON string
        encrypted_bytes = cipher.encrypt(json_string.encode('utf-8'))

        # Write the encrypted blob to your output file
        with open(output_locked_file, "wb") as file:
            file.write(encrypted_bytes)

        print(f"✓ Success! Data locked in '{output_locked_file}'")
        print(f"  Keep your key secure!")

    except (ValueError, FileNotFoundError, RuntimeError) as exc:
        print(f"✗ Error: {exc}")


def unlock_data_from_json(locked_file: str, output_txt: str, 
                         fkey: str | None = None, key_file: str | None = None) -> None:
    """
    Unlock a JSON-encrypted file and restore the original text.
    
    Args:
        locked_file: Path to the locked file
        output_txt: Path to the output text file
        fkey: Inline Fernet key (raw or passphrase)
        key_file: Path to a file containing the Fernet key
    """
    try:
        # Resolve the Fernet cipher
        cipher = _resolve_fernet(fkey=fkey, key_file=key_file)

        # Read the encrypted locked file
        with open(locked_file, "rb") as file:
            encrypted_content = file.read()

        # Decrypt the content back to a string
        try:
            decrypted_bytes = cipher.decrypt(encrypted_content)
            decoded_json = json.loads(decrypted_bytes.decode('utf-8'))
        except InvalidToken:
            print("✗ Decryption failed. The key might be wrong or the file is corrupted.")
            return

        # Extract the raw text content and write it back out to a .txt file
        raw_text = decoded_json["content"]
        with open(output_txt, "w", encoding="utf-8") as file:
            file.write(raw_text)

        print(f"✓ Success! Restored file saved to '{output_txt}' with original layout.")

    except (ValueError, FileNotFoundError, RuntimeError) as exc:
        print(f"✗ Error: {exc}")


# ══════════════════════════════════════════════════════════════════════════════
# Key input helper
# ══════════════════════════════════════════════════════════════════════════════

def _get_fernet_key_from_user(locking=True) -> tuple[str | None, str | None]:
    """
    Prompt user to provide Fernet key either inline or from file.
    
    Returns:
        Tuple of (fkey, key_file) where one will be set and the other None
    """
    key_source = questionary.select(
        message="How would you like to provide the Fernet key?",
        choices=[
            "Enter key inline",
            "Load from file"
        ],
        pointer="->"
    ).ask()

    if key_source == "Enter key inline":
        return ask_for_key_and_validate(locking=locking)
    else:
        try:
            key_file = ask_for_path_and_validate("Enter the path to your Fernet key file")
            return (None, key_file)
        except KeyboardInterrupt:
            return


# ══════════════════════════════════════════════════════════════════════════════
# Interactive menu
# ══════════════════════════════════════════════════════════════════════════════

def lock_unlock_menu_workflow() -> None:
    """Main menu workflow for lock/unlock operations."""
    
    choices = ["Lock file", "Unlock file"]

    user_selection = questionary.select(
        message="Select an operation:",
        choices=choices,
        pointer="->",
    ).ask()

    print(f"\nSelected: {user_selection}")

    if user_selection == "Lock file":
        try:
            input_path: str = ask_for_path_and_validate(message="Enter the path to the file to lock")
        except KeyboardInterrupt:
            sys.exit()

        default_out = input_path.strip(".txt") + "_locked.enc"
        output_path = questionary.text(
            message="Enter output file path (locked file)",
            default=default_out,
            validate=lambda text: len(text) > 0 or "Path cannot be empty"
        ).ask()

        fkey, key_file = _get_fernet_key_from_user()
        
        lock_data_to_json(input_txt=input_path, output_locked_file=output_path, 
                         fkey=fkey, key_file=key_file)

    elif user_selection == "Unlock file":
        try:
            locked_path = ask_for_path_and_validate(message="Enter the path to the locked file")
        except KeyboardInterrupt:
            sys.exit()

        def_out = locked_path.strip(".enc").strip("_locked") + "_restored.txt"
        output_path = questionary.text(
            message="Enter output file path (restored file)",
            default=def_out,
            validate=lambda text: len(text) > 0 or "Path cannot be empty"
        ).ask()

        fkey, key_file = _get_fernet_key_from_user(locking=False)
        
        unlock_data_from_json(locked_file=locked_path, output_txt=output_path, 
                             fkey=fkey, key_file=key_file)



if __name__ == "__main__":
    lock_unlock_menu_workflow()
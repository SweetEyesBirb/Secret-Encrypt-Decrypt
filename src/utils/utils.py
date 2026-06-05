import os
import questionary
from datetime import datetime


def check_if_file_exists(input_file: str):
    print(input_file)
    return os.path.exists(input_file)

def ask_for_path_and_validate(message: str):
    
    file_exists = False
    
    while not file_exists:
        input_path: str = questionary.text(
            message= message,
        ).ask()

        input_path = input_path.strip().strip("\"")

        if check_if_file_exists(input_path):
            file_exists = True
            break
        else:
            print(f"File {input_path} does not exist")
    
    return input_path


def ask_for_key_and_validate(locking=True):
    
    if locking:
        pass_match = False

        while not pass_match:
            key_input = questionary.password(
                    message="Enter your Fernet key or passphrase",
                    validate=lambda text: len(text) > 0 or "Key cannot be empty"
                ).ask()
            key_input_confirm = questionary.password(
                message="Enter your Fernet key or passphrase again",
                validate=lambda text: len(text) > 0 or "Key cannot be empty"
            ).ask()

            if key_input == key_input_confirm:
                pass_match = True
                break
            else:
                print("Keys did not match")
            
        return (key_input, None)
    
    else:
        key_input = questionary.password(
                    message="Enter your Fernet key or passphrase",
                    validate=lambda text: len(text) > 0 or "Key cannot be empty"
                ).ask()
        
        return (key_input, None)


def get_current_time():
    now = datetime.now()
    time = now.strftime("%H_%M_%S")
    return time
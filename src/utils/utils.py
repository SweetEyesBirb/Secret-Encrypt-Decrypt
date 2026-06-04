import os
import questionary

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
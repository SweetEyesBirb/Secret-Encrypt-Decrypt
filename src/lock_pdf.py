import sys
import questionary
from pypdf import PdfReader, PdfWriter

from src.utils.utils import ask_for_path_and_validate

def read_lock_save_pdf(pdf_path, output_path, password):

    try:
        reader = PdfReader(pdf_path)

        # Clone reader into the writer object
        writer = PdfWriter(clone_from=reader)

        # Encrypt the writer with a password (uses strong AES-256 encryption)
        writer.encrypt(password)

        with open(output_path, "wb") as f:
            writer.write(f)
    
        print("PDF successfully locked!")

    except Exception as e:
        print(f"Aww Snap! {e}")



def pdf_menu_workflow():

    choices = ["Lock PDF"]

    user_selection = questionary.select(
        message="Select an option:",
        choices= choices,
        pointer= "->",
    ).ask()

    print(f"Selected {user_selection}")

    if user_selection == "Lock PDF":

        try:
            input_path = ask_for_path_and_validate(message= "Insert the path to the PDF to be locked")

        except KeyboardInterrupt:
            sys.exit()
        
        try:
            pass_match = False

            while not pass_match:
                password = questionary.password(
                    message= "Type your secure password",
                ).ask()

                re_password = questionary.password(
                    message= "Re-type your password",
                ).ask()

                if password == re_password:
                    pass_match = True
                    break
                else:
                    print("passwords dont match")

        except KeyboardInterrupt:
            sys.exit()

        output_path: str = input_path.strip(".pdf") + "_locked.pdf"

        read_lock_save_pdf(pdf_path=input_path, output_path=output_path, password=password)


if __name__ == "__main__":
    pdf_menu_workflow()
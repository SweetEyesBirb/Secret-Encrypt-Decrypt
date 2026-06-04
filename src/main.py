import questionary

from scrambler import _interactive
from lock_pdf import pdf_menu_workflow
from conversion import run_pdf_to_text_menu_workflow, run_text_to_pdf_menu_workflow


def main():

    options = ["encrypt-decrypt", "txt to PDF", "lock PDF", "PDF to txt"]

    selected_option = questionary.select(
        message= "Select an option",
        choices= options,
        pointer= "->"
    ).ask()

    if selected_option == "encrypt-decrypt":
        _interactive()
    elif selected_option == "txt to PDF":
        run_text_to_pdf_menu_workflow()
    elif selected_option == "lock PDF":
        pdf_menu_workflow()
    elif selected_option == "PDF to txt":
        run_pdf_to_text_menu_workflow()


if __name__ == "__main__":
    main()
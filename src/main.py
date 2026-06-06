import questionary

from src.tui.scrambler_menu import scrambler_menu
from src.lock_pdf import pdf_menu_workflow
from src.conversion import run_pdf_to_text_menu_workflow, run_text_to_pdf_menu_workflow
from src.lock_unlock import lock_unlock_menu_workflow


def main():

    options = ["encrypt-decrypt", "lock-unlock file", "txt to PDF", "lock PDF", "PDF to txt"]

    go_again = True

    while go_again:
        selected_option = questionary.select(
            message="Select an option",
            choices=options,
            pointer="->"
        ).ask()

        if selected_option == "encrypt-decrypt":
            scrambler_menu()
        elif selected_option == "lock-unlock file":
            lock_unlock_menu_workflow()
        elif selected_option == "txt to PDF":
            run_text_to_pdf_menu_workflow()
        elif selected_option == "lock PDF":
            pdf_menu_workflow()
        elif selected_option == "PDF to txt":
            run_pdf_to_text_menu_workflow()

        go_again = questionary.confirm(
            message="Would you like to perform another operation?"
        ).ask()

        if not go_again:
            break


if __name__ == "__main__":
    main()
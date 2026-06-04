from fpdf import FPDF
from pypdf import PdfReader
from fpdf.enums import XPos, YPos 

from src.utils.utils import ask_for_path_and_validate


def text_to_pdf(input_txt: str, output_pdf: str):
    # Initialize the PDF canvas
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    
    pdf.set_font("Helvetica", size=12)
    
    output_pdf = output_pdf if ".pdf" in output_pdf else output_pdf + ".pdf"
    
    try:
        # Read the text file and write it to the PDF canvas
        with open(input_txt, "r", encoding="utf-8") as file:
            for line in file:
                # cell parameters: width (0 spans page), height, text, line-break
                pdf.cell(0, 8, text=line.strip(), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
        pdf.output(output_pdf)

        print(f"Document saved succesfully at: {output_pdf}")
    
    except Exception as e:
        print(f"Something went wrong: {e}")


def pdf_to_text(input_pdf: str, output_txt: str):

    reader = PdfReader(input_pdf)

    output_txt = output_txt if ".txt" in output_txt else output_txt + ".txt"
    
    try:
        with open(output_txt, "w", encoding="utf-8") as file:
            for page_num, page in enumerate(reader.pages):
                
                text = page.extract_text()
                
                # Optional: Add a clear visual page boundary indicator
                # file.write(f"--- Page {page_num + 1} ---\n")
                file.write(text)
                # file.write("\n\n")

            print("PDF successfully converted to txt")
    
    except Exception as e:
        print(f"Something went wrong: {e}")


def run_text_to_pdf_menu_workflow():

    input_path = ask_for_path_and_validate("Enter the path to the txt file")
    output_path = input_path.strip(".txt")
    text_to_pdf(input_txt=input_path, output_pdf=output_path)

def run_pdf_to_text_menu_workflow():
    input_path = ask_for_path_and_validate("Enter the path to the PDF file")
    output_path = input_path.strip(".pdf")
    pdf_to_text(input_pdf=input_path, output_txt=output_path)


if __name__ == "__main__":
    # run_text_to_pdf_menu_workflow()
    run_pdf_to_text_menu_workflow()


import re
import json
from fpdf import FPDF
from pypdf import PdfReader
from fpdf.enums import XPos, YPos 

from src.utils.utils import ask_for_path_and_validate, get_current_time


def text_to_pdf(input_txt: str, output_pdf: str):
    # Initialize the PDF canvas
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    
    # use monospaced for hashes
    pdf.set_font("Courier", size=10)
    
    time = get_current_time()
    output_pdf = output_pdf.rstrip(".pdf") if ".pdf" in output_pdf else output_pdf
    output_pdf = output_pdf + f"_{time}" + ".pdf"
    
    try:
        # Read the text file and write it to the PDF canvas
        with open(input_txt, "r", encoding="utf-8") as file:
            full_text = file.read()
            # To make this work for converting back to text, need to add an extra new line character to those already there. Then, when converting back, you can safely remove any single new line char (added during txt to pdf converison)
            json_data = {
                "text_from_txt": full_text
            }
            with open("txt_to_json.json", "w", encoding="utf-8") as json_file:
                json.dump(json_data, json_file, indent=4, ensure_ascii=False)
            pdf.multi_cell(0, 5, text=full_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
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
                
                text = page.extract_text(extraction_mode="layout")
                file.write(text)
                file.write("\n\n")

            print("PDF successfully converted to txt")
    
    except Exception as e:
        print(f"Something went wrong: {e}")


def pdf_to_text_reassemble(input_pdf, output_txt: str):
    
    reader = PdfReader(input_pdf)
    
    time = get_current_time()

    output_txt = output_txt.strip(".txt") if ".txt" in output_txt else output_txt
    output_txt = output_txt + f"_{time}"  + ".txt"
    
    full_extracted_text = ""
    
    try:
        for page in reader.pages:
            full_extracted_text += page.extract_text(extraction_mode="layout")
            print(full_extracted_text)
            
        # 2. Regex logic: Match a newline '\n' ONLY if it is:
        #    - NOT preceded by another newline (?<!\n)
        #    - NOT followed by another newline (?!\n)
        single_newline_pattern = r'(?<!\n)\n(?!\n)'
        # This matches a single newline and cleans up any spaces immediately around it
        # single_newline_pattern = r'(?<!\n) *\n *(?!\n)'
        
        # Replace the single newline with an empty string to reassemble the hash
        cleaned_text = re.sub(single_newline_pattern, '', full_extracted_text)
        print()
        print(f"Cleaned Text:\n{cleaned_text}")
        
        # 3. Save the completely reassembled text file
        with open(output_txt, "w", encoding="utf-8") as file:
            file.write(cleaned_text)
        
        print("File saved succesfully")

    except Exception as e:
        print(f"Something went wrong: {e}")


def extract_pdf_to_json(input_pdf, output_json):
    reader = PdfReader(input_pdf)
    full_text = ""
    
    for page in reader.pages:
        full_text += page.extract_text(extraction_mode="layout")

    # 2. Count your structural elements using regex
    all_newlines = re.findall(r'\n', full_text)
    single_newlines = re.findall(r'(?<!\n)\n(?!\n)', full_text)
    double_newlines = re.findall(r'\n\n', full_text)
    
    single_newline_pattern = r'(?<!\n)\n(?!\n)'
    # This matches a single newline and cleans up any spaces immediately around it
    # single_newline_pattern = r'(?<!\n) *\n *(?!\n)'
    
    # Replace the single newline with an empty string to reassemble the hash
    cleaned_text = re.sub(single_newline_pattern, '', full_text)

    json_data = {
        "metadata": {
            "total_pages": len(reader.pages),
            "total_character_count": len(full_text),
            "newline_metrics": {
                "total_newline_characters": len(all_newlines),
                "isolated_single_newlines_to_remove": len(single_newlines),
                "double_newlines_to_preserve": len(double_newlines)
            }
        },
        "raw_extracted_text": full_text,
        "cleaned_text": cleaned_text
    }
    
    with open(output_json, "w", encoding="utf-8") as json_file:
        json.dump(json_data, json_file, indent=4, ensure_ascii=False)


def run_text_to_pdf_menu_workflow():

    input_path = ask_for_path_and_validate("Enter the path to the txt file")
    output_path = input_path.strip(".txt")
    text_to_pdf(input_txt=input_path, output_pdf=output_path)

def run_pdf_to_text_menu_workflow():
    input_path = ask_for_path_and_validate("Enter the path to the PDF file")
    output_path = input_path.strip(".pdf")
    pdf_to_text_reassemble(input_pdf=input_path, output_txt=output_path)


if __name__ == "__main__":
    run_text_to_pdf_menu_workflow()
    # run_pdf_to_text_menu_workflow()


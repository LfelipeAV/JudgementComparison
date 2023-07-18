import PyPDF2
import re
import csv
import gensim
import tkinter as tk
from gensim import corpora, models
from typing import List
from tkinter import filedialog, messagebox
import nltk
nltk.download('punkt')
from nltk.tokenize import word_tokenize

# Import necessary modules

def extract_text_from_pdf(pdf_file: str) -> str:
    with open(pdf_file, 'rb') as pdf:  # Open the PDF file in binary mode
        reader = PyPDF2.PdfReader(pdf, strict=False)  # Create a PdfReader object
        text_content = ''
        for page in reader.pages:  # Iterate over each page in the PDF
            content = page.extract_text()  # Extract the text content from the page
            text_content += content
        return text_content

def find_articles(text_content: str) -> List[str]:
    patterns = [
        r"article\s+\d+\s+of[\w\s]+?(?=(?:\n\s*and\s+|\n\s*or\s+)?article\s+\d+\s+of|$)",  # Pattern to match "article and article"
        r"article\s+([\w\W]*?(?=(article?\s+\d+)|$))",  # Pattern to match "article" followed by a number
        r"principle[\w\s]+\b",  # Pattern to match instances of "principle" followed by any word characters and spaces
        r"EU\s+value of[\w\s]*\b"  # Pattern to match instances of "EU value" followed by any word characters and spaces
    ]

    matches = []
    for pattern in patterns:
        pattern_matches = re.findall(pattern, text_content, re.IGNORECASE)  # Find all matches of the pattern in the text_content
        matches.extend(pattern_matches)

    return [match for match in matches if match]  # Filter out empty matches and return a list of non-empty strings

def run_code():
    pdf_file_paths = [pdf_file1_path.get(), pdf_file2_path.get()]
    if len(pdf_file_paths) == 2:
        paragraphs = []

        for path in pdf_file_paths:
            extracted_text = extract_text_from_pdf(path)  # Extract the text content from the PDF document
            results = find_articles(extracted_text)
            paragraphs.append(results)

        save_results(paragraphs)

def save_results(paragraphs):
    result_csv = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    with open(result_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # Write the header
        writer.writerow(["PDF 1", "PDF 2", "Paragraph"])

        # Write the data
        for i in range(max(len(paragraphs[0]), len(paragraphs[1]))):
            row = [
                paragraphs[0][i] if i < len(paragraphs[0]) else "",
                paragraphs[1][i] if i < len(paragraphs[1]) else "",
            ]
            writer.writerow(row)

    messagebox.showinfo("Results", "Results saved to {}".format(result_csv))

def select_pdf1():
    file_path = filedialog.askopenfilename()
    pdf_file1_path.set(file_path)

def select_pdf2():
    file_path = filedialog.askopenfilename()
    pdf_file2_path.set(file_path)

# Create the GUI window
root = tk.Tk()
root.title("PDF Comparison")
root.geometry("400x200")

pdf_file1_path = tk.StringVar()
pdf_file2_path = tk.StringVar()

pdf1_label = tk.Label(root, text="PDF 1:")  # Label for PDF 1 selection
pdf1_label.pack()

pdf1_button = tk.Button(root, text="Select PDF 1", command=select_pdf1)  # Button to select PDF 1
pdf1_button.pack()

pdf1_path_label = tk.Label(root, textvariable=pdf_file1_path)  # Label to display selected PDF 1 path
pdf1_path_label.pack()

pdf2_label = tk.Label(root, text="PDF 2:")  # Label for PDF 2 selection
pdf2_label.pack()

pdf2_button = tk.Button(root, text="Select PDF 2", command=select_pdf2)  # Button to select PDF 2
pdf2_button.pack()

pdf2_path_label = tk.Label(root, textvariable=pdf_file2_path)  # Label to display selected PDF 2 path
pdf2_path_label.pack()

run_button = tk.Button(root, text="Run", command=run_code)  # Button to run the code
run_button.pack()

root.mainloop()

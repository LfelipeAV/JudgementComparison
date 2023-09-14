import PyPDF2
import re
import csv
import tkinter as tk
from typing import List
from tkinter import filedialog, messagebox
import nltk
import pandas as pd
import xlsxwriter

nltk.download('punkt')
from nltk.tokenize import word_tokenize


def extract_text_from_pdf(pdf_file: str) -> str:
    with open(pdf_file, 'rb') as pdf:
        reader = PyPDF2.PdfReader(pdf, strict=False)
        text_content = ''
        for page in reader.pages:
            content = page.extract_text()
            text_content += content
        return text_content


def find_articles(text_content: str) -> List[str]:
    patterns = [
        (r"article\s+\d+\s+of[\w\s]+?(?=(?:\n\s*and\s+|\n\s*or\s+)?article\s+\d+\s+of|$)", "Article"),
        (r"article\s+([\w\W]*?(?=(article?\s+\d+)|$))", "Article"),
        (r"principle[\w\s]+\b", "Principle"),
        (r"EU\s+value of[\w\s]*\b", "EU Value")
    ]

    matches = []
    for pattern, match_type in patterns:
        pattern_matches = re.findall(pattern, text_content, re.IGNORECASE)
        matches.extend([(match_type, match) for match in pattern_matches])

    return [(match_type, match) for match_type, match in matches if match]


def calculate_similarity(paragraphs1: List[str], paragraphs2: List[str]) -> List[float]:
    similarity_scores = []
    for i, paragraph1 in enumerate(paragraphs1):
        max_similarity = 0
        max_similarity_index = -1
        for j, paragraph2 in enumerate(paragraphs2):
            similarity_score = calculate_word_overlap(paragraph1, paragraph2)
            if similarity_score > max_similarity:
                max_similarity = similarity_score
                max_similarity_index = j

        similarity_scores.append((i, max_similarity, max_similarity_index))

    similarity_scores.sort(key=lambda x: x[1], reverse=True)
    return similarity_scores


def calculate_word_overlap(paragraph1: str, paragraph2: str) -> float:
    words1 = set(word_tokenize(paragraph1.lower()))
    words2 = set(word_tokenize(paragraph2.lower()))

    common_words = words1.intersection(words2)
    similarity_score = len(common_words) / max(len(words1), len(words2))

    return similarity_score


# ... (previous code remains the same)

def save_results(paragraphs, similarity_scores):
    result_excel = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
    writer = pd.ExcelWriter(result_excel, engine='xlsxwriter')
    workbook = writer.book

    # Write the first sheet with paragraphs being compared, match type, and similarity score
    first_sheet_name = "Comparison Results"
    first_sheet = workbook.add_worksheet(first_sheet_name)
    first_sheet.write(0, 0, "Match Type")
    first_sheet.write(0, 1, "Match")
    first_sheet.write(0, 2, "PDF 1 Paragraph")
    first_sheet.write(0, 3, "PDF 2 Paragraph")
    first_sheet.write(0, 4, "Similarity Score")

    for i, (index1, similarity, index2) in enumerate(similarity_scores):
        matches1 = find_articles(paragraphs[0][index1])
        matches2 = find_articles(paragraphs[1][index2])

        match_type1, match1 = matches1[0] if matches1 else ("", "")  # Set default values if no matches found
        match_type2, match2 = matches2[0] if matches2 else ("", "")  # Set default values if no matches found

        first_sheet.write(i + 1, 0, match_type1)
        first_sheet.write(i + 1, 1, str(match1))  # Convert tuple to string
        first_sheet.write(i + 1, 2, paragraphs[0][index1])
        first_sheet.write(i + 1, 3, paragraphs[1][index2])
        first_sheet.write(i + 1, 4, similarity)

    # Write the paragraphs used for comparison sheets
    pdf1_df = pd.DataFrame(paragraphs[0], columns=["PDF 1 Paragraphs in order of appearance"])
    pdf1_df.to_excel(writer, sheet_name="PDF 1 Paragraphs", index=False)

    pdf2_df = pd.DataFrame(paragraphs[1], columns=["PDF 2 Paragraphs in order of appearance"])
    pdf2_df.to_excel(writer, sheet_name="PDF 2 Paragraphs", index=False)

    writer.close()
    messagebox.showinfo("Results", "Results saved to {}".format(result_excel))

def run_code():
    pdf_file_paths = [pdf_file1_path.get(), pdf_file2_path.get()]
    if len(pdf_file_paths) == 2:
        paragraphs = []

        for path in pdf_file_paths:
            extracted_text = extract_text_from_pdf(path)
            results = find_articles(extracted_text)
            paragraphs.append([str(result) for result in results])  # Convert tuples to strings

        if paragraphs:
            similarity_scores = calculate_similarity(paragraphs[0], paragraphs[1])
            save_results(paragraphs, similarity_scores)
def run_code():
    pdf_file_paths = [pdf_file1_path.get(), pdf_file2_path.get()]
    if len(pdf_file_paths) == 2:
        paragraphs = []

        for path in pdf_file_paths:
            extracted_text = extract_text_from_pdf(path)
            results = find_articles(extracted_text)
            paragraphs.append([str(result) for result in results])  # Convert tuples to strings

        if paragraphs:
            similarity_scores = calculate_similarity(paragraphs[0], paragraphs[1])
            save_results(paragraphs, similarity_scores)


def select_pdf1():
    file_path = filedialog.askopenfilename()
    pdf_file1_path.set(file_path)


def select_pdf2():
    file_path = filedialog.askopenfilename()
    pdf_file2_path.set(file_path)


root = tk.Tk()
root.title("PDF Comparison")
root.geometry("400x200")

pdf_file1_path = tk.StringVar()
pdf_file2_path = tk.StringVar()

pdf1_label = tk.Label(root, text="PDF 1:")
pdf1_label.pack()

pdf1_button = tk.Button(root, text="Select PDF 1", command=select_pdf1)
pdf1_button.pack()

pdf1_path_label = tk.Label(root, textvariable=pdf_file1_path)
pdf1_path_label.pack()

pdf2_label = tk.Label(root, text="PDF 2:")
pdf2_label.pack()

pdf2_button = tk.Button(root, text="Select PDF 2", command=select_pdf2)
pdf2_button.pack()

pdf2_path_label = tk.Label(root, textvariable=pdf_file2_path)
pdf2_path_label.pack()

run_button = tk.Button(root, text="Run", command=run_code)
run_button.pack()

root.mainloop()
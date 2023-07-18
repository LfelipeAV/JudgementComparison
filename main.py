import PyPDF2
import re
import csv
import tkinter as tk
from typing import List
from tkinter import filedialog, messagebox
import nltk

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
        r"article\s+\d+\s+of[\w\s]+?(?=(?:\n\s*and\s+|\n\s*or\s+)?article\s+\d+\s+of|$)",
        r"article\s+([\w\W]*?(?=(article?\s+\d+)|$))",
        r"principle[\w\s]+\b",
        r"EU\s+value of[\w\s]*\b"
    ]

    matches = []
    for pattern in patterns:
        pattern_matches = re.findall(pattern, text_content, re.IGNORECASE)
        matches.extend(pattern_matches)

    return [match for match in matches if match]


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


def save_results(paragraphs, similarity_scores):
    result_csv = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    with open(result_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # Write the similarity scores sheet
        writer.writerow(["PDF 1 Paragraph", "PDF 2 Paragraph", "Similarity Score"])
        for i, similarity_score, j in similarity_scores:
            row = [
                paragraphs[0][i] if i < len(paragraphs[0]) else "",
                paragraphs[1][j] if j < len(paragraphs[1]) else "",
                similarity_score,
            ]
            writer.writerow(row)

        # Write the paragraphs used for comparison sheets
        writer.writerow([])  # Add an empty row as separator

        writer.writerow(["PDF 1 Paragraphs Used for Comparison"])
        writer.writerows([(p,) for p in paragraphs[0]])

        writer.writerow([])  # Add an empty row as separator

        writer.writerow(["PDF 2 Paragraphs Used for Comparison"])
        writer.writerows([(p,) for p in paragraphs[1]])

    messagebox.showinfo("Results", "Results saved to {}".format(result_csv))


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
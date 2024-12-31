import os
import re
from PyPDF2 import PdfReader
from word2number import w2n
import pandas as pd
import streamlit as st
import tkinter as tk
from tkinter import filedialog

try:

    def select_folder():
        root = tk.Tk()
        root.withdraw()
        folder_path = filedialog.askdirectory(master=root)
        root.destroy()
        return folder_path

    selected_folder_path = st.session_state.get("folder_path", None)
    folder_select_button = st.button("Select Folder")
    if folder_select_button:
        selected_folder_path = select_folder()
        st.session_state.folder_path = selected_folder_path


    # Folder containing the PDFs
    pdf_folder = f"{selected_folder_path}"
    output_excel = "extracted_data.csv"  # Save as CSV for clarity

    # Initialize a list to store the extracted data
    data_list = []

    # Patterns to extract specific fields
    patterns = {
        "Reference No.": r"Reference No\. & Date\.\s*([\w-]+)",  # Extract Reference No.
        "Other References": r"Other References\s*([\w\d]+)",  # Extract Other References
        "Service Charge": r"Service Charges?.*\s([\d,]+\.\d{2})",  # Extract Service Charges
    }

    # Loop through each PDF file in the folder
    for filename in os.listdir(pdf_folder):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder, filename)
            
            # Open and read the PDF
            reader = PdfReader(pdf_path)
            pdf_text = " ".join(page.extract_text() for page in reader.pages if page.extract_text())
            
            # Extract data for the current PDF
            extracted_data = {}
            for field, pattern in patterns.items():
                match = re.search(pattern, pdf_text)
                extracted_data[field] = match.group(1).strip() if match else None
            
            # Extract "Total (in words)" and convert to numeric value
            total_in_words_match = re.search(r"INR\s*(.*?)\s*Only", pdf_text, re.IGNORECASE)
            if total_in_words_match:
                total_in_words = total_in_words_match.group(1).strip()
                try:
                    extracted_data["Total"] = w2n.word_to_num(total_in_words.lower())
                except ValueError:
                    extracted_data["Total"] = "Conversion Error"

            # Append the extracted data to the list
            data_list.append(extracted_data)

    # Create a DataFrame from the extracted data
    df = pd.DataFrame(data_list)

    st.dataframe(df)

    # Remove the 'File Name' column if it exists

    # Save the DataFrame to an Excel file
    # df.to_csv(output_excel, index=False)
except:
    pass


import os
import re
from PyPDF2 import PdfReader
from word2number import w2n
import pandas as pd
import streamlit as st
import tkinter as tk
from tkinter import filedialog




# Set up tkinter
root = tk.Tk()
root.withdraw()

# Make folder picker dialog appear on top of other windows
root.wm_attributes('-topmost', 1)

# Folder picker button
st.title('Folder Picker')
st.write('Please select a folder:')
clicked = st.button('Folder Picker')
if clicked:
    dirname = st.text_input('Selected folder:', filedialog.askdirectory(master=root))

    # Folder containing the PDFs
    pdf_folder = f"{dirname}"
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


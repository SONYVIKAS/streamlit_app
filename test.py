import os
import re
from PyPDF2 import PdfReader
from word2number import w2n
import pandas as pd
import streamlit as st
from tkinter import Tk, filedialog

# Function to pick a folder using tkinter
def pick_folder():
    root = Tk()
    root.withdraw()  # Hide the root window
    folder_selected = filedialog.askdirectory()
    root.destroy()
    return folder_selected

# Title of the Streamlit App
st.title("PDF Data Extraction Tool")

# Add a button for folder picking
if st.button("Pick a Folder"):
    selected_folder_path = pick_folder()
    st.write(f"Selected Folder: {selected_folder_path}")
else:
    selected_folder_path = None

if selected_folder_path and os.path.isdir(selected_folder_path):
    # Output CSV file name
    output_excel = "extracted_data.csv"

    # Initialize a list to store the extracted data
    data_list = []

    # Patterns to extract specific fields
    patterns = {
        "Reference No.": r"Reference No\. & Date\.\s*([\w-]+)",  # Extract Reference No.
        "Other References": r"Other References\s*([\w\d]+)",  # Extract Other References
        "Service Charge": r"Service Charges?.*\s([\d,]+\.\d{2})",  # Extract Service Charges
    }

    # Loop through each PDF file in the folder
    for filename in os.listdir(selected_folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(selected_folder_path, filename)

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

    # Display the extracted data in Streamlit
    st.dataframe(df)

    # Provide an option to download the data as a CSV
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download Extracted Data as CSV",
        data=csv,
        file_name=output_excel,
        mime="text/csv",
    )
else:
    st.warning("Please pick a folder to proceed.")

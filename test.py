import os
import re
from PyPDF2 import PdfReader
import pandas as pd
import streamlit as st
from word2number import w2n

st.title("PDF Data Extraction Tool")

genre = st.radio(
    "",
    ["visawaale", "Jetsave"],
    index=None,
)
if genre == "visawaale":
# Title of the Streamlit App
    st.title("visawaale")

    # Add a file uploader to select multiple PDF files
    uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        # Initialize a list to store the extracted data
        data_list = []

        # Patterns to extract specific fields
        patterns = {
            "Reference No.": r"Reference No\. & Date\.\s*([\w-]+)",  # Extract Reference No.
            "Other References": r"Other References\s*([\w\d]+)",  # Extract Other References
            "Service Charge": r"Service Charges?.*\s([\d,]+\.\d{2})",  # Extract Service Charges
            "IGST Amount": r"IGST @\d+%.*?([\d,]+\.\d{2})",  # Extract IGST Amount
            "IGST Rate": r"IGST @(\d+%)",  # Extract IGST Rate
            "Country Before Visa": r"([A-Za-z]+)\s*Visa\s*Fee",  # Extract country before "Visa Fees"
        }

        # Loop through each uploaded PDF file
        for uploaded_file in uploaded_files:
            # Read the uploaded file
            reader = PdfReader(uploaded_file)
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
            file_name="extracted_data.csv",
            mime="text/csv",
        )
    else:
        st.warning("Please upload PDF files to proceed.")

elif genre == "Jetsave":
    # Title of the Streamlit App
    st.title("Jetsave")

    # Add a file uploader to allow the user to select PDF files
    uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        # Initialize a list to store the extracted data
        data_list = []

        # Patterns to extract specific fields
        patterns = {
            "Invoice No.": r"Invoice No\s*:\s*DEL\s*([\w/]+)",  # Extract Invoice No.
            "Corporate": r"Ref No\.:\s*([\w/]+)",  # Extract Reference No.
            "Pax Name": r"GURGAON\s*(.*?)\s*Corporate",  # Extract Pax Name
            "Country": r"([A-Za-z]+)*\s+VISA Fee",  # Extract country before "Visa Fee"
            "IGST After": r"SGST\(@9%\)\s*0\.00\s*([\d,]+\.\d{2})",  # Extract value after SGST
            "Net Amount": r"([\d,]+\.\d{2})\s*Net Amount",  # Extract Net Amount
        }
        #  "Value After SGST": r"SGST\s*@\d+%\s*\d+\.\d{2}\s*(\d+\.\d{2})",  # Extract value after SGST

        # Loop through each uploaded PDF file
        for uploaded_file in uploaded_files:
            # Read the uploaded file
            reader = PdfReader(uploaded_file)
            pdf_text = " ".join(page.extract_text() for page in reader.pages if page.extract_text())

            # Extract data for the current PDF
            extracted_data = {}
            for field, pattern in patterns.items():
                match = re.search(pattern, pdf_text, re.DOTALL)  # Enable multiline matching
                extracted_data[field] = match.group(1).strip() if match else None

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
            file_name="extracted_data.csv",
            mime="text/csv",
        )
    else:
        st.warning("Please upload PDF files to proceed.")

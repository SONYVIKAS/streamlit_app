import os
import re
from PyPDF2 import PdfReader
import pandas as pd
import streamlit as st
import pdfplumber
from word2number import w2n

st.title("PDF Data Extraction Tool")

genre = st.radio(
    "",
    ["visawaale", "Jetsave"],
    index=None,
)

if genre == "visawaale":
        # Title of the Streamlit App
    st.title("Visawaale")

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

    # Function to extract text from a PDF
    def extract_text_from_pdf(file):
        with pdfplumber.open(file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
            return text

    # Function to parse the extracted text into structured JSON
    def parse_text_to_dataframe(text):
        lines = text.splitlines()

        # Container for structured data
        invoice_details = {
            "invoice_number": None,
            "corporate": None,
            "date": None,
            "pax_name": None,
            "country": None,
            "total_amount": None,
            "igst": None,
            "cgst": None,
            "sgst": None,
            "net_amount": None
        }

        for i, line in enumerate(lines):
            if "Invoice No" in line:
                invoice_details["invoice_number"] = line.split(":")[-1].strip().replace("DEL", "")
            elif "Date :" in line:
                invoice_details["date"] = line.split(":")[-1].strip()
            elif "Pax Name :" in line:
                invoice_details["pax_name"] = line.split(":")[-1].strip()
            elif "VISA Fee" in line:
                description_parts = line.split()
                invoice_details["country"] = description_parts[0] if len(description_parts) > 0 else None
            elif "Corporate" in line or line.startswith("IN"):
                invoice_details["corporate"] = line.split(":")[-1].strip().split("/")[0].strip()
            elif "Total" in line and line.strip().startswith("Total"):
                invoice_details["total_amount"] = line.split()[-1].strip()
            elif "IGST" in line:
                invoice_details["igst"] = line.split()[-1].strip()
            elif "CGST" in line:
                invoice_details["cgst"] = line.split()[-1].strip()
            elif "SGST" in line:
                invoice_details["sgst"] = line.split()[-1].strip()
            elif "Net Amount" in line:
                invoice_details["net_amount"] = line.split()[-1].strip()

        return invoice_details

    # Multi-file uploader (with a unique key)
    uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True, key="jetsave_uploader")

    if uploaded_files:
        all_invoice_details = []

        # Process each uploaded file
        for uploaded_file in uploaded_files:
            pdf_text = extract_text_from_pdf(uploaded_file)
            invoice_details = parse_text_to_dataframe(pdf_text)

            # Store data from each file
            all_invoice_details.append(invoice_details)

        # Convert all results into a single DataFrame
        combined_invoice_details_df = pd.DataFrame(all_invoice_details)

        # Display combined results
        st.write("All Invoice Details in a Single Table:")
        st.dataframe(combined_invoice_details_df)

        # Option to save as CSV
        st.download_button(
            "Download Invoice Details as CSV",
            combined_invoice_details_df.to_csv(index=False),
            "invoice_details.csv",
            "text/csv"
        )

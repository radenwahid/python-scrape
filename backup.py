import streamlit as st
import pandas as pd
import pdfplumber
import openpyxl
from parse import parse_with_ollama 
from scrape import scrape_website, split_dom_content, clean_body_content, extract_body_content

# Streamlit UI
st.title("Scrape What You Want")
url = st.text_input("Enter Website URL")
uploaded_file = st.file_uploader("Or upload a file (PDF, Excel, HTML, TXT)", type=["pdf", "xlsx", "xls", "html", "txt"])

if st.button("Process Content"):
    if url:
        st.write("Scraping the website...")
        
        result = scrape_website(url)
        body_content = extract_body_content(result)
        cleaned_content = clean_body_content(body_content)
        
        st.session_state.dom_content = cleaned_content
        
        with st.expander("View Dom Content"):
            st.text_area("Dom Content", cleaned_content, height=300)

    elif uploaded_file:
        if uploaded_file.type == "application/pdf":
            st.write("Processing the PDF file...")
            pdf_text = ""
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    pdf_text += page.extract_text()
            
            cleaned_content = clean_body_content(pdf_text)
            st.session_state.dom_content = cleaned_content
            
            with st.expander("View PDF Content"):
                st.text_area("Extracted Content", cleaned_content, height=300)

        elif uploaded_file.type in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
            st.write("Processing the Excel file...")
            df = pd.read_excel(uploaded_file)
            st.write(df)  # Displaying the DataFrame for user review
            st.session_state.dom_content = df.to_string()  # Convert DataFrame to a string for parsing

            with st.expander("View Excel Content"):
                st.text_area("Excel Content as Text", df.to_string(), height=300)

if "dom_content" in st.session_state:
    parse_description = st.text_area("Description you want to parse:")
    
    if st.button("Parse Content"):
        if parse_description:
            st.write("Parsing the content...")
            
            dom_chunks = split_dom_content(st.session_state.dom_content) 
            result = parse_with_ollama(dom_chunks, parse_description)   
            st.write(result)

import streamlit as st
import pandas as pd
import pdfplumber
from parse import parse_with_ollama 
from scrape import scrape_website, split_dom_content, clean_body_content, extract_body_content

# Streamlit UI
st.title("Scrape What You :blue[Want]")
url = st.text_input("Enter Website URL", placeholder="https://google.com")
uploaded_file = st.file_uploader("Or upload a file (PDF, Excel, HTML, TXT)", type=["pdf", "xlsx", "xls", "html", "txt"])



if st.button("Process Content"):
    success = False  # Track success state
    if url:
        try:
            st.write("Scraping the website...")
            result = scrape_website(url)
            body_content = extract_body_content(result)
            cleaned_content = clean_body_content(body_content)
            st.session_state.dom_content = cleaned_content
            success = True
            
            with st.expander("View Web Content"):
                st.text_area("Web Content", cleaned_content, height=300)
        except Exception as e:
            st.error(f"Failed to scrape the website: {e}")

    elif uploaded_file:
        try:
            if uploaded_file.type == "application/pdf":
                st.write("Processing the PDF file...")
                pdf_text = ""
                with pdfplumber.open(uploaded_file) as pdf:
                    for page in pdf.pages:
                        pdf_text += page.extract_text() or ""  # Handle pages with no text
                
                cleaned_content = clean_body_content(pdf_text)
                st.session_state.dom_content = cleaned_content
                success = True
                
                with st.expander("View PDF Content"):
                    st.text_area("Extracted Content", cleaned_content, height=300)

            elif uploaded_file.type in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
                st.write("Processing the Excel file...")
                df = pd.read_excel(uploaded_file, engine="openpyxl" if uploaded_file.name.endswith("xlsx") else None)
                st.write(df)  # Display the DataFrame for user review
                st.session_state.dom_content = df.to_string()  # Convert DataFrame to a string for parsing
                success = True
                
                with st.expander("View Excel Content"):
                    st.text_area("Excel Content as Text", df.to_string(), height=300)
        
        except Exception as e:
            st.error(f"Error reading the uploaded file: {e}")

    # Show toast-like success message
    if success:
        st.success("Content processed successfully!")
    else:
        st.error("Failed to process content. Please check the input.")

if "dom_content" in st.session_state:
    parse_description = st.text_area("Description you want to parse:", placeholder="how I want to be rich")
    
    if st.button("Parse Content"):
        if parse_description:
            st.write("Parsing the content...")
            
            dom_chunks = split_dom_content(st.session_state.dom_content) 
            result = parse_with_ollama(dom_chunks, parse_description)   
            st.write(result)
            st.success("Parsing completed successfully!")

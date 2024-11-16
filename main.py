import streamlit as st
import pandas as pd
import pdfplumber
from parse import parse_with_ollama 
from scrape import scrape_website, split_dom_content, clean_body_content, extract_body_content
import httpx
import time

# Streamlit UI
st.title("Scrape What You :blue[Want]")
url = st.text_input("Enter Website URL", placeholder="https://google.com")
uploaded_file = st.file_uploader("Or upload a file (PDF, Excel, HTML, TXT)", type=["pdf", "xlsx", "xls", "html", "txt"])

# Initialize session state for dom_content and df_display
if 'dom_content' not in st.session_state:
    st.session_state.dom_content = None
if 'df_display' not in st.session_state:
    st.session_state.df_display = None

if st.button("Process Content"):
    # Clear previous session state
    st.session_state.dom_content = None
    st.session_state.df_display = None

    success = False  # Track success state
    if url:
        try:
            st.write("Scraping the website...")
            start_time = time.time()  # Start measuring time
            result = scrape_website(url)
            body_content = extract_body_content(result)
            cleaned_content = clean_body_content(body_content)
            st.session_state.dom_content = cleaned_content  # Save the cleaned content
            elapsed_time = time.time() - start_time  # Measure elapsed time
            st.write(f"Website scraped in {elapsed_time:.2f} seconds.")
            success = True
            
        except httpx.ConnectError as e:
            st.error(f"Failed to connect to the website: {e}")
        except httpx.RequestError as e:
            st.error(f"Request error: {e}")
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
                st.session_state.dom_content = cleaned_content  # Save the cleaned content
                success = True

            elif uploaded_file.type in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
                st.write("Processing the Excel file...")
                df = pd.read_excel(uploaded_file, engine="openpyxl" if uploaded_file.name.endswith("xlsx") else None)
                st.session_state.dom_content = df.to_string()  # Convert DataFrame to a string for parsing
                st.session_state.df_display = df  # Save the DataFrame for displaying
                success = True

        except Exception as e:
            st.error(f"Error reading the uploaded file: {e}")

    # Show toast-like success message
    if success:
        st.success("Content processed successfully!")
    else:
        st.error("Failed to process content. Please check the input.")

# Check if dom_content is available to display
if st.session_state.dom_content is not None:
    with st.expander("View Content", expanded=True):
        st.text_area("Processed Content", st.session_state.dom_content, height=300)

# Display the DataFrame if it exists
if st.session_state.df_display is not None:
    with st.expander("View Excel Content", expanded=True):
        st.dataframe(st.session_state.df_display)  # Display the DataFrame

# Show the parse description area only after processing content
if st.session_state.dom_content is not None:
    parse_description = st.text_area("Description you want to parse:", placeholder="how I want to be rich")
    
    if st.button("Parse Content"):
        if parse_description:
            st.write("Parsing the content...")
            
            dom_chunks = split_dom_content(st.session_state.dom_content) 
            result = parse_with_ollama(dom_chunks, parse_description)   
            st.write(result)
            st.success("Parsing completed successfully!")

import logging
from scrape import scrape_website, extract_body_content, clean_body_content, split_dom_content
from langchain.llms import Ollama
from langchain.agents import initialize_agent
from langchain.agents import AgentType

# Set up logging for better error tracking
logging.basicConfig(level=logging.INFO)

def parse_with_ollama(dom_chunks, parse_description):
    try:
        ollama = Ollama(model="llama2")  # Use the appropriate model
        chain = initialize_agent(
            tools=[], agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION, llm=ollama, verbose=True
        )
        
        # Iterate over DOM chunks and parse them
        results = []
        for chunk in dom_chunks:
            response = chain.invoke({"dom_content": chunk, "parse_description": parse_description})
            results.append(response)
        
        return results
    except Exception as e:
        logging.error(f"Error during parsing with Ollama: {e}")
        return []

def scrape_and_parse(website, parse_description):
    try:
        html_content = scrape_website(website)
        body_content = extract_body_content(html_content)
        cleaned_content = clean_body_content(body_content)
        dom_chunks = split_dom_content(cleaned_content)

        # Parse the chunks with Ollama
        parse_results = parse_with_ollama(dom_chunks, parse_description)
        return parse_results

    except Exception as e:
        logging.error(f"Error during scraping and parsing: {e}")
        return []

if __name__ == "__main__":
    website_url = "https://your-website-to-scrape.com"
    parse_description = "Parse this webpage content and extract meaningful information"
    
    results = scrape_and_parse(website_url, parse_description)
    if results:
        logging.info(f"Parsed results: {results}")
    else:
        logging.error("No results were obtained.")

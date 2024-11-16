from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import time
import httpx

template = (
    "You are tasked with extracting specific information from the following text content: {dom_content}. "
    "Please follow these instructions carefully: \n\n"
    "1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}. "
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
    "3. **Empty Response:** If no information matches the description, return an empty string ('')."
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
)

model = OllamaLLM(model="llama3")

def parse_with_ollama(dom_chunks, parse_description):
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model
    
    parsed_results = []
    
    for i, chunk in enumerate(dom_chunks, start=1):
        try:
            start_time = time.time()  # Start measuring time
            response = chain.invoke({"dom_content": chunk, "parse_description": parse_description})
            elapsed_time = time.time() - start_time  # Measure elapsed time
            print(f"Parsed batch {i} of {len(dom_chunks)} in {elapsed_time:.2f} seconds")
            parsed_results.append(response)
            
        except httpx.RequestError as e:
            print(f"Request error while processing batch {i}: {e}")
            parsed_results.append("")

        except Exception as e:
            print(f"Unexpected error while processing batch {i}: {e}")
            parsed_results.append("")
        
    return "\n".join(parsed_results)

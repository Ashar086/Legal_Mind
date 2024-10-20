'''import streamlit as st
import json
import base64
from together import Together

# Setup for the 3rd party AI/ML API
api_key = "<3fbfe25109b647efb7bf2f45bd667163>"  # Replace with your actual API key
base_url = "https://api.aimlapi.com/chat"

client = Together(base_url=base_url, api_key=api_key)

def call_ai_api(prompt, max_tokens=1000):
    """
    Function to call the AI API.
    """
    try:
        response = client.chat.completions.create(
    model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",  # Using Llama-3 model
            messages=[
                {
                    "role": "user",
                    "content": prompt  # Directly use the prompt string
                }
            ],
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"An error occurred while calling the API: {str(e)}")
        return None

def analyze_contract(file_content):
    # Encode the file content as base64
    encoded_content = base64.b64encode(file_content).decode('utf-8')
    
    prompt = f"""Analyze the following contract document and provide a detailed breakdown of its clauses, including their titles, content, risk level, and a brief explanation for each. The document content is base64 encoded below:

{encoded_content}

Decode the content and analyze it. Format your response as a JSON object with a 'clauses' key containing an array of clause objects. Each clause object should have 'title', 'content', 'risk_level', and 'explanation' keys.
"""

    # Call AI API to analyze the contract
    response = call_ai_api(prompt, max_tokens=2000)
    
    # Parse the JSON response
    if response:
        try:
            analysis_result = json.loads(response)
            return analysis_result
        except json.JSONDecodeError:
            st.error("Failed to parse the API response as JSON.")
            return {"clauses": []}
    else:
        return {"clauses": []}

def generate_response(prompt):
    return call_ai_api(prompt, max_tokens=1000)

st.title("Contract Negotiation Assistant")

uploaded_file = st.file_uploader("Upload your contract document", type=["txt", "pdf", "docx"])

if uploaded_file is not None:
    file_content = uploaded_file.read()
    
    st.write("Analyzing contract...")
    analysis_result = analyze_contract(file_content)
    
    st.write("Contract Analysis Results:")
    
    clauses = analysis_result.get("clauses", [])
    clause_decisions = {}
    
    for i, clause in enumerate(clauses):
        st.subheader(f"Clause {i+1}: {clause['title']}")
        st.write(clause['content'])
        st.write(f"Risk Level: {clause['risk_level']}")
        st.write(f"Explanation: {clause['explanation']}")
        
        decision = st.radio(f"Decision for Clause {i+1}", ["Accept", "Negotiate", "Reject"], key=f"decision_{i}")
        clause_decisions[i] = decision
        
        if decision == "Negotiate":
            negotiation_points = st.text_area(f"Enter negotiation points for Clause {i+1}", key=f"negotiation_{i}")
            clause_decisions[f"{i}_points"] = negotiation_points

    if st.button("Generate Response"):
        st.write("Generating response...")
        
        prompt = """As a professional contract negotiator, draft a courteous email response to the contract drafter based on the following decisions:

"""
        
        for i, clause in enumerate(clauses):
            decision = clause_decisions[i]
            prompt += f"Clause {i+1} ({clause['title']}): {decision}\n"
            if decision == "Negotiate":
                prompt += f"Negotiation points: {clause_decisions.get(f'{i}_points', 'No specific points provided.')}\n"
            prompt += "\n"
        
        prompt += "Please draft a professional and polite email response addressing these points and suggesting next steps for the negotiation process."
        
        response = generate_response(prompt)
        
        st.subheader("Generated Response:")
        st.write(response)
        
        if st.button("Save Response"):
            # Implement saving functionality here
            st.write("Response saved successfully!")

else:
    st.write("Please upload a contract to begin the analysis.")



'''


import streamlit as st
import json
import fitz  # PyMuPDF
import docx  # python-docx
import os
import re
import openai

api_key = '3fbfe25109b647efb7bf2f45bd667163'
openai.api_key = api_key
openai.api_base = "https://api.aimlapi.com"

def call_ai_api(prompt, max_tokens=1000):
    """
    Function to call the 3rd party Llama API.
    """
    try:
        response = openai.ChatCompletion.create(
            model="meta-llama/Llama-3.2-3B-Instruct-Turbo",  # Using Llama-3.2 model
            messages=[
                {
                    "role": "user",
                    "content": prompt  # Directly use the prompt string
                }
            ],
            max_tokens=max_tokens,
        )
        return response.choices[0].message["content"]
    except Exception as e:
        print(f"An error occurred while calling the API: {str(e)}")
        return None

def extract_json(text):
    """
    Try to extract JSON data from a text string using a regular expression.
    """
    json_match = re.search(r'{.*}', text, re.DOTALL)
    if json_match:
        return json_match.group(0)
    return None

def chunk_text(text, max_chunk_size=3000):
    """
    Split the text into chunks based on a maximum size.
    """
    chunks = []
    words = text.split()
    current_chunk = []
    
    for word in words:
        current_chunk.append(word)
        if len(' '.join(current_chunk)) > max_chunk_size:
            chunks.append(' '.join(current_chunk[:-1]))
            current_chunk = [word]
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
        
    return chunks

def extract_text_from_pdf(file_content):
    """
    Extract text from a PDF file using PyMuPDF.
    """
    pdf_document = fitz.open(stream=file_content, filetype="pdf")
    text = ""
    for page in pdf_document:
        text += page.get_text()
    return text

def extract_text_from_docx(file_content):
    """
    Extract text from a DOCX file using python-docx.
    """
    doc = docx.Document(file_content)
    text = []
    for para in doc.paragraphs:
        text.append(para.text)
    return "\n".join(text)

def analyze_contract(file_content, file_type):
    # Extract the text based on the file type
    if file_type == "pdf":
        decoded_content = extract_text_from_pdf(file_content)
    elif file_type == "docx":
        decoded_content = extract_text_from_docx(file_content)
    else:
        decoded_content = file_content.decode('utf-8')  # Assuming it's a text file

    # Chunk the contract content
    chunks = chunk_text(decoded_content, max_chunk_size=3000)  # Adjust the size as needed
    analysis_results = {"clauses": []}
    
    for chunk in chunks:
        prompt = f"""Analyze the following contract section and provide a detailed breakdown of its clauses, including their titles, content, risk level, and a brief explanation for each. The document content is as follows:
{chunk}
Format your response as a JSON object with a 'clauses' key containing an array of clause objects. Each clause object should have 'title', 'content', 'risk_level', and 'explanation' keys. Do not include any extra text, only the JSON output.
"""
        # Call AI API to analyze each chunk
        response = call_ai_api(prompt, max_tokens=2000)
        
        # Parse the JSON response
        if response:
            
            # Try to extract JSON from the response
            json_data = extract_json(response)
            if json_data:
                try:
                    analysis_result = json.loads(json_data)
                    if "clauses" in analysis_result:
                        analysis_results["clauses"].extend(analysis_result["clauses"])
                    else:
                        st.warning("The API response did not include any clauses.")
                except json.JSONDecodeError:
                    pass
            else:
                st.error("The response did not contain any recognizable JSON.")
    
    return analysis_results

st.title("Contract Negotiation Assistant")

uploaded_file = st.file_uploader("Upload your contract document", type=["txt", "pdf", "docx"])

if uploaded_file is not None:
    file_content = uploaded_file.read()
    file_type = uploaded_file.type.split('/')[1]  # Get file type (e.g., pdf, docx)

    st.write("Analyzing contract...")
    analysis_result = analyze_contract(file_content, file_type)
    
    if analysis_result and analysis_result.get("clauses"):
        clauses = analysis_result.get("clauses", [])
        clause_decisions = {}
        
        for i, clause in enumerate(clauses):
            st.subheader(f"Clause {i + 1}: {clause['title']}")
            st.write(clause['content'])
            st.write(f"Risk Level: {clause['risk_level']}")
            st.write(f"Explanation: {clause['explanation']}")
            
            decision = st.radio(f"Decision for Clause {i + 1}", ["Accept", "Negotiate", "Reject"], key=f"decision_{i}")
            clause_decisions[i] = decision
            
            if decision == "Negotiate":
                negotiation_points = st.text_area(f"Enter negotiation points for Clause {i + 1}", key=f"negotiation_{i}")
                clause_decisions[f"{i}_points"] = negotiation_points  # Save negotiation points

        # Finalize Contract button
        if st.button("Finalize Contract"):
            prompt = """As a professional contract negotiator, draft a courteous email response to the contract drafter based on the following decisions:\n\n"""
            
            for i, clause in enumerate(clauses):
                decision = clause_decisions[i]
                prompt += f"Clause {i + 1} ({clause['title']}): {decision}\n"
                if decision == "Negotiate":
                    prompt += f"Negotiation points: {clause_decisions.get(f'{i}_points', 'No specific points provided.')}\n"
                prompt += "\n"
            
            prompt += "Please draft a professional and polite email response addressing these points and suggesting next steps for the negotiation process."
            
            response = call_ai_api(prompt)
            
            st.subheader("Generated Response:")
            st.write(response)
            
            if st.button("Save Response"):
                # Implement saving functionality here
                st.write("Response saved successfully!")

    else:
        st.write("No clauses found in the contract analysis. Please try again.")
else:
    st.write("Please upload a contract to begin the analysis.")


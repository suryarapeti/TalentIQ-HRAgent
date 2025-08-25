from typing import List
import os
import json
import pandas as pd
from dotenv import load_dotenv
import secrets
import string
import PyPDF2
import json
from groq import AsyncGroq

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
if groq_api_key:
    client = AsyncGroq(api_key=groq_api_key)
else:
    client = None
    print("WARNING: GROQ_API_KEY not found in environment variables!")

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file using PyPDF2."""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
            return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF {file_path}: {e}")
        return ""



async def analyze_resume_with_llm(resume_text, job_description):
    """
    Uses Groq API to analyze a resume against a job description.
    Returns a structured JSON object with name, email, score, and summary.
    """
    if not client:
        print("Error: Groq client not initialized")
        return None
    
    prompt = f"""
    Analyze the following resume based on the provided job description.
    Extract the candidate's name and email.
    Score the candidate from 0 to 100 on how well they fit the job description.
    Provide a brief summary (2-3 sentences) of their qualifications and why they are a good fit.

    Return the result as a single, valid JSON object with exactly the keys: "name", "email", "score", and "summary".

    Job Description:
    ---
    {job_description}
    ---

    Resume:
    ---
    {resume_text}
    ---

    JSON Output:
    """
    try:
        response = await client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are an expert HR analyst that only responds with valid JSON containing exactly the keys: name, email, score, and summary."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
        )
        result_text = response.choices[0].message.content
        
        start = result_text.find('{')
        end = result_text.rfind('}') + 1
        if start == -1 or end == 0:
            print(f"Error: No valid JSON found in response: {result_text}")
            return None
        
        json_str = result_text[start:end]
        result = json.loads(json_str)
        
        required_keys = {"name", "email", "score", "summary"}
        if not all(key in result for key in required_keys) or set(result.keys()) != required_keys:
            print(f"Error: Invalid JSON structure. Got keys: {list(result.keys())}, expected: {list(required_keys)}")
            return None
        
        if not isinstance(result["score"], (int, float)) or not 0 <= result["score"] <= 100:
            print(f"Error: Invalid score value: {result.get('score')}")
            return None
        
        for key in ["name", "email", "summary"]:
            if not isinstance(result[key], str):
                print(f"Error: Invalid {key} type: {type(result[key])}")
                return None
        
        return result
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}, Response: {result_text}")
        return None
    except Exception as e:
        print(f"Error analyzing with LLM: {e}")
        return None
    
def generate_random_link(base_url="https://meet.google.com/"):
    random_str = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
    return f"{base_url}{random_str}"


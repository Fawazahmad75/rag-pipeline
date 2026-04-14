import os
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.1-8b-instant"

def generate_answer(query, context_chunks):
    context = "\n\n".join(context_chunks)
    prompt = prompt = f"""You are a helpful assistant. Answer the question based only on the context below.
If the answer is not in the context, say "I don't have enough information."
At the end of your answer, always add a line that says:
"Source used: [quote the specific sentence from the context you relied on most]"

Context:
{context}

Question: {query}
Answer:"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(GROQ_URL, headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']
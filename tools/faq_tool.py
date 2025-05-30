# tools/faq_tool.py
"""
FAQ lookup tool for Ava.
• FAQ_TOOL: function schema for the LLM
• lookup_faq(query) -> str : real HTTP call to RAG endpoint
"""
import openai

client = openai.OpenAI()  # Use existing OpenAI client configuration
MODEL = "gpt-4o"  # Use the same model as the main application

import requests

FAQ_TOOL = {
    "type": "function",
    "function": {
        "name": "lookup_faq",
        "description": "Ask the RAGBOT FAQ API and return the answer.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The prospect's FAQ question"
                }
            },
            "required": ["query"]
        }
    }
}

def is_faq_question(query: str) -> bool:
    """Determine if the question is an FAQ type"""
    print(f"Checking if question is FAQ type: '{query}'")
    
    # Use simple prompt engineering to let the LLM make the determination
    prompt = f"""
    Determine if the following user question is a frequently asked question (FAQ) about apartment leasing.
    Common questions typically involve: location, pricing, amenities, application process, policies, etc.
    Examples of FAQ questions:
    - What are the available units?
    - How much is the rent?
    - What amenities are included?
    - How many pets may I have?

    User question: "{query}"
    
    Please answer only with "true" or "false".
    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=10     # Only need a short answer
        )
        
        answer = response.choices[0].message.content.strip().lower()
        result = "true" in answer  # Check if "true" is in the response
        print(f"LLM determination result: {answer} -> {result}")
        return result
    except Exception as e:
        print(f"LLM determination error: {e}")
        return False  # Default to False in case of error

_ENDPOINT = "http://3.16.255.36:8000/rag"

def lookup_faq(query: str) -> str:
    """Call RAG endpoint and return plain-text answer."""
    print("lookup_faq")
    try:
        resp = requests.post(
            _ENDPOINT,
            json={"query": query},
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("answer", "Sorry, I couldn't find an answer.")
    except Exception as exc:
        return f"Sorry, there was an error fetching that answer ({exc})."

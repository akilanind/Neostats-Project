import sys
import os

# Ensure the parent directory is in the path so we can import config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config.config import GROQ_API_KEY, GROQ_MODEL

SYSTEM_PROMPTS: dict[str, str] = {
    "concise": (
        "You are CitizenHelp, a helpful Indian government scheme assistant. "
        "Answer in 2-3 simple sentences. Be direct and clear. "
        "If eligibility info is available, lead with a yes/no. "
        "If the user asks something completely unrelated to Indian government "
        "schemes, welfare programs, or public benefits, politely respond with: "
        "'I'm CitizenHelp, designed specifically to help you with Indian government "
        "schemes and benefits. Could you ask me about a specific scheme instead?' "
        "Do not answer off-topic questions."
    ),
    "detailed": (
        "You are CitizenHelp, a helpful Indian government scheme assistant. "
        "Give thorough, well-structured responses with the following sections: "
        "Scheme Overview, Eligibility Criteria, Benefits, How to Apply, "
        "Required Documents, and Official Portal. "
        "Use simple English mixed with common Hindi terms where helpful "
        "(e.g., 'ration card', 'Aadhar'). "
        "Always cite which document or search result you used. "
        "If the user asks something completely unrelated to Indian government "
        "schemes, welfare programs, or public benefits, politely respond with: "
        "'I'm CitizenHelp, designed specifically to help you with Indian government "
        "schemes and benefits. Could you ask me about a specific scheme instead?' "
        "Do not answer off-topic questions."
    ),
}

def get_llm_response(messages: list[dict], mode: str = "concise") -> str:
    """
    Sends a chat conversation to Groq and returns the generated response.
    """
    try:
        from groq import Groq

        if not GROQ_API_KEY:
            return (
                "The Groq API key is not configured. Please set the 'GROQ_API_KEY' "
                "in your .env file and restart the application."
            )

        client = Groq(api_key=GROQ_API_KEY)

        system_prompt = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["concise"])

        # Inject the system prompt at the beginning
        full_messages = [{"role": "system", "content": system_prompt}] + messages

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=full_messages,
            temperature=0.4,
            max_tokens=2048,
            top_p=0.9,
        )

        return response.choices[0].message.content

    except ImportError:
        error_msg = "The 'groq' package is not installed. Please run: pip install groq"
        print(f"[llm.py] {error_msg}")
        return error_msg

    except Exception as e:
        error_msg = f"Sorry, I encountered an error while connecting to the AI service: {e}"
        print(f"[llm.py] API call failed: {e}")
        return error_msg

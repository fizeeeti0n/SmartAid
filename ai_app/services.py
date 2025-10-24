# ai_app/services.py

import os
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class GeminiAIService:
    def __init__(self):
        if not GEMINI_API_KEY:
            # This is the line that raises an error if the key is missing/blank.
            raise ValueError("GEMINI_API_KEY not found in environment variables.")


class GeminiAIService:
    """Service class for interacting with the Google Gemini API."""

    def __init__(self):
        """Initializes the Gemini client."""
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")

        # Initialize the client
        try:
            self.client = genai.Client(api_key=GEMINI_API_KEY)
            self.model = 'gemini-2.5-flash'  # A fast, versatile model
        except Exception as e:
            print(f"Error initializing Gemini client: {e}")
            raise

    def get_ai_chat_response(self, prompt: str) -> str:
        """Sends a message to the AI and returns the text response."""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=dict(
                    temperature=0.7,
                ),
            )
            return response.text
        except APIError as e:
            print(f"Gemini API Error (Chat): {e}")
            return "Sorry, I ran into an issue communicating with the AI service."
        except Exception as e:
            print(f"General Error (Chat): {e}")
            return "An unexpected error occurred."

    def get_mood_suggestion(self, mood_code: str, notes: str = "") -> str:
        """Analyzes a mood and provides a personalized suggestion."""
        prompt = (
            f"The user has logged their mood as '{mood_code}'. "
            f"{f'They also added notes: "{notes}"' if notes else ''}. "
            "Based on this mood, provide a short (2-3 sentence), empathetic, and actionable "
            "suggestion related to productivity or wellness. For example, if 'stressed', suggest a 5-minute break. "
            "If 'joyful', suggest planning the next task while feeling motivated. "
            "Your response should be only the suggestion text."
        )
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=dict(
                    temperature=0.8,
                ),
            )
            return response.text
        except APIError as e:
            print(f"Gemini API Error (Mood): {e}")
            return "Could not generate AI suggestion due to an API error."
        except Exception as e:
            print(f"General Error (Mood): {e}")
            return "An unexpected error occurred."

    def process_document(self, text_content: str, title: str) -> dict:
        """Summarizes a document and generates flashcards from the text."""

        # Use a structured output format for the most reliable parsing
        system_instruction = (
            "You are a study aid AI. Your task is to process the provided text. "
            "First, generate a concise summary (around 3-4 paragraphs) of the key points. "
            "Second, generate a minimum of 5 and a maximum of 10 detailed flashcards "
            "from the most important concepts. The output MUST be a valid JSON object."
        )

        json_schema = {
            "type": "object",
            "properties": {
                "summary": {"type": "string", "description": "The concise 3-4 paragraph summary of the text."},
                "flashcards": {
                    "type": "array",
                    "description": "A list of 5-10 detailed flashcards.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string", "description": "The flashcard question."},
                            "answer": {"type": "string", "description": "The detailed flashcard answer."}
                        },
                        "required": ["question", "answer"]
                    }
                }
            },
            "required": ["summary", "flashcards"]
        }

        user_prompt = f"Please process the following document titled '{title}'. Document text: \n\n{text_content}"

        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-pro',  # Use a more capable model for complex summarization/card generation
                contents=user_prompt,
                config=dict(
                    temperature=0.3,
                    response_mime_type="application/json",
                    response_schema=json_schema
                ),
            )

            # The response.text is a JSON string matching the schema
            return {"title": title, **response.json()}

        except APIError as e:
            print(f"Gemini API Error (Document Processing): {e}")
            return {"error": "API communication failed during document processing."}
        except Exception as e:
            print(f"General Error (Document Processing): {e}")
            return {"error": "An internal error occurred during processing."}
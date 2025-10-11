

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from google import genai
from google.genai import types
import json
from pypdf import PdfReader
import io
import os

# Initialize the Gemini Client
# It will automatically pick up the GEMINI_API_KEY environment variable.
try:
    client = genai.Client()
except Exception as e:
    # Handle case where API key is not set
    print(f"Gemini client initialization failed: {e}")
    client = None


@login_required
def study_tools_view(request):
    """Renders the main study tools page."""
    return render(request, 'study_tools.html')


def extract_text_from_pdf(pdf_file):
    """Extracts text content from an uploaded PDF file."""
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None


@login_required
def create_flashcards(request):
    if request.method != 'POST':
        return HttpResponseBadRequest(json.dumps({'error': 'Only POST method is allowed.'}),
                                      content_type='application/json')

    if client is None:
        return JsonResponse({'error': 'Gemini API is not configured on the server.'}, status=500)

    # 1. Handle the File Upload
    if 'pdf_file' not in request.FILES:
        return JsonResponse({'error': 'No PDF file was uploaded.'}, status=400)

    pdf_file = request.FILES['pdf_file']

    # Basic validation (matching frontend)
    if pdf_file.size > 10 * 1024 * 1024:
        return JsonResponse({'error': 'File size exceeds 10MB limit.'}, status=400)

    # 2. Extract Text from PDF
    pdf_content = io.BytesIO(pdf_file.read())
    extracted_text = extract_text_from_pdf(pdf_content)

    if not extracted_text or len(extracted_text.strip()) < 50:
        return JsonResponse({'error': 'Could not extract enough readable text from the PDF.'}, status=400)

    # Limit the text length to avoid excessive token usage
    MAX_TEXT_LENGTH = 15000
    truncated_text = extracted_text[:MAX_TEXT_LENGTH]

    # 3. Define the Structured Output Schema
    # This tells Gemini to return a specific JSON structure.
    flashcard_schema = types.Schema(
        type=types.Type.ARRAY,
        description="A list of flashcards generated from the text.",
        items=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "term": types.Schema(type=types.Type.STRING, description="The key concept or term."),
                "definition": types.Schema(type=types.Type.STRING,
                                           description="The detailed definition or explanation."),
            },
            required=["term", "definition"],
        ),
    )

    # 4. Construct the Prompt and Call the Gemini API
    prompt = f"""
    Analyze the following study material. Based on the key concepts and facts, generate a set of 10 to 15 concise flashcards. 
    The output must be a JSON array that strictly adheres to the provided schema.

    STUDY MATERIAL:
    ---
    {truncated_text}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=flashcard_schema,
            ),
        )

        # 5. Parse the Response
        # The response.text is a JSON string conforming to flashcard_schema
        cards_data = json.loads(response.text)

        # Validation: Ensure it's a list (array)
        if not isinstance(cards_data, list):
            raise ValueError("Gemini returned an invalid JSON structure (not a list).")

        return JsonResponse({'status': 'success', 'cards': cards_data})

    except Exception as e:
        print(f"Gemini API or processing error: {e}")
        return JsonResponse({'error': f'An AI generation error occurred: {str(e)}'}, status=500)
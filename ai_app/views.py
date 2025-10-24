# ai_app/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from .models import MoodLog
from .serializers import MoodLogSerializer, MoodLogFetchSerializer

from .serializers import (
    ChatRequestSerializer, ChatResponseSerializer,
    MoodRequestSerializer, MoodResponseSerializer,
    StudyToolResponseSerializer
)
from .services import GeminiAIService
from .utils import extract_text_from_pdf


class AIChatView(APIView):
    """API endpoint for AI Assistant chat interaction."""

    @swagger_auto_schema(request_body=ChatRequestSerializer, responses={200: ChatResponseSerializer})
    def post(self, request):
        """Handles POST request to get a response from the AI assistant."""
        serializer = ChatRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                ai_service = GeminiAIService()
                user_message = serializer.validated_data['message']

                # Contextual prompt for the assistant
                system_prompt = (
                    "You are SmartAid, a supportive and actionable productivity and wellness companion. "
                    "Keep your responses concise and focused on planning, tracking, or brainstorming. "
                    f"User message: {user_message}"
                )

                ai_response = ai_service.get_ai_chat_response(system_prompt)

                response_serializer = ChatResponseSerializer({'response': ai_response})
                return Response(response_serializer.data, status=status.HTTP_200_OK)

            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({"error": "An error occurred while fetching AI response."},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------------------------------------------------------

class MoodLogView(APIView):
    """API endpoint for logging mood and receiving AI suggestions."""

    @swagger_auto_schema(request_body=MoodRequestSerializer, responses={200: MoodResponseSerializer})
    def post(self, request):
        """Handles POST request to log a mood and get a tailored AI suggestion."""
        # NOTE: In a real app, you would save this mood entry to a Django model here.

        serializer = MoodRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                ai_service = GeminiAIService()
                mood_code = serializer.validated_data['mood']
                notes = serializer.validated_data.get('notes', '')

                # Get suggestion from AI
                suggestion = ai_service.get_mood_suggestion(mood_code, notes)

                response_data = {
                    'mood': mood_code,
                    'ai_suggestion': suggestion,
                }

                response_serializer = MoodResponseSerializer(response_data)
                return Response(response_serializer.data, status=status.HTTP_200_OK)

            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({"error": "An error occurred while processing mood log."},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------------------------------------------------------

class StudyToolsView(APIView):
    """API endpoint for Study Tools: PDF upload, text extraction, summary, and flashcard generation."""

    # We use manual handling instead of request_body for file upload in swagger
    def post(self, request, format=None):
        """Handles POST request for file upload and processing."""

        if 'pdf_file' not in request.FILES:
            return Response({"error": "No PDF file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        pdf_file = request.FILES['pdf_file']
        title = pdf_file.name

        # 1. Extract Text from PDF
        text_content = extract_text_from_pdf(pdf_file)

        if not text_content:
            return Response(
                {"error": "Could not extract text from the PDF file. Check if it's a valid text-based PDF."},
                status=status.HTTP_400_BAD_REQUEST)

        # 2. Process Document via AI
        try:
            ai_service = GeminiAIService()
            processed_data = ai_service.process_document(text_content, title)

            if 'error' in processed_data:
                return Response({"error": processed_data['error']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 3. Serialize and return structured response
            response_serializer = StudyToolResponseSerializer(processed_data)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": "An error occurred during AI document processing."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    class MoodLogView(APIView):
        """Handles logging and fetching user mood data."""

        # @swagger_auto_schema for POST (logging the mood)
        @swagger_auto_schema(
            request_body=MoodLogSerializer,
            responses={200: MoodLogSerializer}
        )
        def post(self, request):
            serializer = MoodLogSerializer(data=request.data)
            if serializer.is_valid():
                mood = serializer.validated_data['mood']
                notes = serializer.validated_data.get('notes', '')

                # Instantiate service and get AI suggestion
                try:
                    ai_service = GeminiAIService()
                    ai_suggestion = ai_service.get_mood_suggestion(mood, notes)
                except Exception as e:
                    # Catch API errors (like the 503) or client initialization errors
                    print(f"Error during AI suggestion: {e}")
                    # Provide a fallback suggestion for the user in the database
                    ai_suggestion = "AI suggestion unavailable due to a temporary service error."

                # Save the new entry to the database
                MoodLog.objects.create(
                    mood=mood,
                    notes=notes,
                    ai_suggestion=ai_suggestion
                )

                # Return the newly created data to the frontend
                return Response({
                    'mood': mood,
                    'ai_suggestion': ai_suggestion
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # New GET method to fetch the latest mood for page load
        @swagger_auto_schema(
            responses={200: MoodLogFetchSerializer(many=True)}
        )
        def get(self, request):
            # Fetch the latest 5 moods
            latest_logs = MoodLog.objects.all()[:5]
            # Use the MoodLogFetchSerializer to format the output
            serializer = MoodLogFetchSerializer(latest_logs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
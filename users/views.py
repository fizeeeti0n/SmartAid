import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
# Import built-in functions with aliases to prevent shadowing
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db import IntegrityError  # Added for robustness
from .models import UserProfile
from .models import Task, MoodEntry
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from .models import Resource


# --- General Views ---

@login_required(login_url='login')
def index(request):
    """Renders the main index/dashboard page, requiring login."""
    # Template path fixed to 'index.html'
    return render(request, 'index.html')


def peer_connect(request):
    """Renders the peer connection page."""
    return render(request, 'peer_connect.html')


def study_tools(request):
    """Renders the study tools page."""
    return render(request, 'study_tools.html')


def resource_library(request):
    """Renders the resource library page."""
    return render(request, 'resource_library.html')


# --- Authentication Views ---

def login(request):
    """Handles user login."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            # Redirect to the new index/dashboard view
            return redirect('index')

            # Failed login path
        messages.error(request, "Invalid username or password.")

    else:
        # GET request: show empty form
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


def signup(request):
    """Handles new user registration."""
    if request.method == 'POST':
        # NOTE: Using a custom UserCreationForm is recommended over raw POST data
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            try:
                # Basic check for existing username is handled by create_user, but you might want to wrap in transaction
                if User.objects.filter(username=username).exists():
                    messages.error(request, "Username already taken.")
                else:
                    user = User.objects.create_user(username=username, password=password)
                    UserProfile.objects.create(user=user)
                    messages.success(request, "Registration successful! Please log in.")
                    return redirect('login')
            except Exception as e:
                messages.error(request, f"Registration failed: {e}")
        else:
            messages.error(request, "Please fill out all fields.")

    # GET or failed POST request
    return render(request, 'signup.html')


def logout(request):
    """Logs out the current user."""
    auth_logout(request)
    messages.info(request, "You have been logged out.")
    # Redirect to the main index page (which will then redirect to login if not authenticated)
    return redirect('index')


@login_required
def profile(request):
    """
    Renders the user profile page and handles form submissions (POST)
    for updating User and UserProfile data, including image upload.
    """

    # 1. Ensure the UserProfile object exists for the current user.
    try:
        # Access the user profile object using the lowercase model name
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        # Create a profile if one doesn't exist
        user_profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        # 2. Handle Built-in User Model fields (First Name, Last Name, Email)
        try:
            request.user.first_name = request.POST.get('first_name', '').strip()
            request.user.last_name = request.POST.get('last_name', '').strip()

            email = request.POST.get('email', '').strip()
            if email:
                request.user.email = email

            # --- DEBUGGING AID ---
            print(
                f"DEBUG: Saving User Data -> First:'{request.user.first_name}', Last:'{request.user.last_name}', Email:'{request.user.email}'")
            # ---------------------

            request.user.save()

        except Exception as e:
            messages.error(request, f"Error updating user details: {e}")

        # 3. Handle Custom UserProfile Model fields (Profile Pic, About Me)

        user_profile.about_me = request.POST.get('about_me', '').strip()

        # Check for file upload (must match name="profile_pic" in the HTML)
        if 'profile_pic' in request.FILES:
            user_profile.profile_pic = request.FILES['profile_pic']

        try:
            user_profile.save()
            messages.success(request, "Profile updated successfully!")

        except IntegrityError as e:
            messages.error(request, "An unexpected database error occurred.")

        # FIX: Redirect to 'user_profile' to match the name in users/urls.py
        return redirect('index')

    # GET request: Render the page with current data
    context = {
        'user': request.user,
    }
    return render(request, 'user_profile.html', context)


# Helper function to convert Task object to dictionary
def task_to_dict(task):
    return {
        'id': task.id,
        'title': task.title,
        'is_completed': task.is_completed,
        # Convert datetime to string for JSON serialization
        'due_date': task.due_date.isoformat() if task.due_date else None,
        'created_at': task.created_at.isoformat(),
        # Simple status for UI colors
        'status_color': 'green-500' if task.is_completed else (
            'red-500' if task.due_date and task.due_date.date() <= models.DateField().today() else 'blue-500')
    }


# --- Main Dashboard View (Renders index.html) ---
@login_required
def dashboard_view(request):
    """Renders the main productivity dashboard."""
    tasks = Task.objects.filter(user=request.user)
    mood_history = MoodEntry.objects.filter(user=request.user).order_by('-logged_at')[:5]

    context = {
        'tasks': [task_to_dict(task) for task in tasks],
        'mood_history': mood_history,
        'mood_choices': MoodEntry.MOOD_CHOICES,
    }
    # Note: The frontend JS will fetch the initial data using the API endpoints
    # For initial rendering, we pass some data, but the JS handles dynamic updates.
    return render(request, 'index.html', context)


# -----------------------------------------------------------------
# 🗣️ 1. AI Assistant (Placeholder for Gemini API integration)
# -----------------------------------------------------------------
@require_http_methods(["POST"])
@login_required
def ai_planner(request):
    """Handles chat messages and returns an AI response."""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    if not user_message:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)

    # --- Placeholder AI Logic ---
    if 'task' in user_message.lower():
        response_text = "I see you're planning a task! Remember to use the Task Tracker on the right to manage your to-do list efficiently. Would you like me to analyze your current tasks?"
    elif 'mood' in user_message.lower():
        response_text = "I'm here to support your well-being. Logging your mood helps track your emotional patterns. How about a quick breathing exercise?"
    else:
        # Generic professional response
        response_text = f"That's a thoughtful question. As your AI planner, I can help you break down complex projects, offer study tips, or provide motivational support based on your query: '{user_message}'."
    # ---------------------------

    return JsonResponse({'response': response_text})


# -----------------------------------------------------------------
# ✅ 3. Task Tracker API Endpoints
# -----------------------------------------------------------------
@require_http_methods(["POST"])
@login_required
def add_task(request):
    """Adds a new task."""
    try:
        data = json.loads(request.body)
        title = data.get('title')
        due_date_str = data.get('due_date')  # Due date can be None
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    if not title:
        return JsonResponse({'error': 'Task title is required'}, status=400)

    task = Task.objects.create(
        user=request.user,
        title=title,
        due_date=due_date_str  # Assumes format that can be parsed by DB (e.g., ISO 8601)
    )
    return JsonResponse(task_to_dict(task))


@require_http_methods(["POST"])
@login_required
def update_task_completion(request, task_id):
    """Toggles the completion status of a task."""
    try:
        data = json.loads(request.body)
        is_completed = data.get('is_completed')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    try:
        task = Task.objects.get(id=task_id, user=request.user)
        task.is_completed = is_completed
        task.save()
        return JsonResponse(task_to_dict(task))
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)


@require_http_methods(["DELETE"])
@login_required
def delete_task(request, task_id):
    """Deletes a task."""
    try:
        task = Task.objects.get(id=task_id, user=request.user)
        task.delete()
        return JsonResponse({'success': True, 'id': task_id})
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)


# -----------------------------------------------------------------
# 💭 2. Mood Tracker API Endpoints
# -----------------------------------------------------------------
@require_http_methods(["POST"])
@login_required
def save_mood(request):
    """Saves a new mood entry."""
    try:
        data = json.loads(request.body)
        mood = data.get('mood')
        notes = data.get('notes')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    if not mood or mood not in [c[0] for c in MoodEntry.MOOD_CHOICES]:
        return JsonResponse({'error': 'Invalid mood selection'}, status=400)

    # Simple AI feedback based on mood
    ai_feedback_map = {
        'joy': "That's wonderful! Keep the momentum going. What made today great?",
        'calm': "A sense of peace is great. Let's aim to maintain this balance.",
        'neutral': "It's okay to feel neutral. Perhaps a simple change of scene could boost your energy?",
        'tired': "Rest is productive. Schedule a break and prioritize essential tasks only.",
        'stressed': "Take a deep breath. Try breaking down your biggest task into smaller, manageable steps.",
        'sad': "I'm sorry to hear that. Remember to be kind to yourself. A small accomplishment can help shift your perspective."
    }

    mood_entry = MoodEntry.objects.create(
        user=request.user,
        mood=mood,
        notes=notes
    )

    return JsonResponse({
        'success': True,
        'mood': mood_entry.get_mood_display(),
        'ai_feedback': ai_feedback_map.get(mood, "Keep tracking your feelings!"),
    })


@require_http_methods(["GET"])
@login_required
def get_mood_data(request):
    """Retrieves the last 5 mood entries."""
    mood_entries = MoodEntry.objects.filter(user=request.user).order_by('-logged_at')[:5]

    data = [{
        'mood_display': entry.get_mood_display(),
        'mood_code': entry.mood,
        'logged_at': entry.logged_at.strftime('%b %d, %I:%M %p')
    } for entry in mood_entries]

    # Get the latest entry for the main display
    latest_mood = data[0] if data else None

    # Simple AI feedback based on the latest mood
    ai_feedback_map = {
        'joy': "You've been in a great mood lately! Let's keep that positive energy flowing.",
        'stressed': "Your recent mood history suggests high stress. Remember to allocate time for self-care this week.",
        'tired': "Recent logs show fatigue. Ensure you're getting adequate rest and hydration.",
    }

    latest_mood_code = latest_mood['mood_code'] if latest_mood else 'neutral'

    # Provide a simple aggregated suggestion based on the latest or overall trend (simple implementation)
    ai_suggestion = ai_feedback_map.get(latest_mood_code,
                                        "Continue logging your mood to help me understand your well-being better.")

    return JsonResponse({
        'latest_mood': latest_mood,
        'history': data,
        'ai_suggestion': ai_suggestion
    })


# --- 1. View to Render the Resource Library Page ---
def resource_library(request):
    # Fetch ALL saved resources from the database
    resources = Resource.objects.all().order_by('-created_at')

    # Filter them for display in the tabs
    pdfs = resources.filter(resource_type='PDF')
    flashcards = resources.filter(resource_type='FLASHCARD')
    videos = resources.filter(resource_type='VIDEO')

    context = {
        'pdfs': pdfs,
        'flashcards': flashcards,
        'videos': videos,
    }
    return render(request, 'resource_library.html', context)


# --- 2. View to Handle Document/PDF Upload ---
def upload_document(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        uploaded_file = request.FILES.get('pdf_file')

        if uploaded_file and title:
            # SAVE the file and its details to the database model
            Resource.objects.create(
                title=title,
                description=f"Uploaded via Study Tools on {uploaded_file.name}",
                resource_type='PDF',
                file=uploaded_file  # Django handles saving the file to MEDIA_ROOT
            )

            # Optional: Add a success message here

        return redirect('resource_library')
    return HttpResponse(status=405)  # Method Not Allowed


# --- 3. View to Handle Flashcard Saving (Example) ---
def save_flashcard(request):
    if request.method == 'POST':
        deck_name = request.POST.get('deck_name')
        card_count = request.POST.get('card_count')

        if deck_name:
            Resource.objects.create(
                title=f"Flashcard Deck: {deck_name}",
                description=f"Generated Deck with {card_count} cards.",
                resource_type='FLASHCARD',
            )

        return redirect('resource_library')
    return HttpResponse(status=405)


# --- 4. View to Handle Video Link Saving ---
def save_video(request):
    if request.method == 'POST':
        topic = request.POST.get('topic')
        url = request.POST.get('url')

        if topic and url:
            Resource.objects.create(
                title=f"Video: {topic}",
                description="Saved external video link.",
                resource_type='VIDEO',
                url=url
            )

        return redirect('resource_library')
    return HttpResponse(status=405)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.utils import timezone
from dateutil import parser
from .models import StudyGroup, GroupMembership, GroupMessage
from .forms import StudyGroupForm
from django.db.models import Count
import json


@login_required
def peer_connect_view(request):
    form = StudyGroupForm()

    if request.method == 'POST':
        form = StudyGroupForm(request.POST)
        if form.is_valid():
            new_group = form.save(commit=False)
            new_group.created_by = request.user
            new_group.save()
            GroupMembership.objects.create(group=new_group, user=request.user)
            messages.success(request, f'Group "{new_group.name}" created and you are automatically joined!')
            return redirect('pc:peer_connect')

    my_groups = StudyGroup.objects.filter(
        members__user=request.user
    ).annotate(
        member_count=Count('members')
    ).order_by('name')

    my_group_ids = my_groups.values_list('id', flat=True)

    other_groups = StudyGroup.objects.exclude(
        id__in=my_group_ids
    ).annotate(
        member_count=Count('members')
    ).order_by('name')

    context = {
        'form': form,
        'my_groups': my_groups,
        'other_groups': other_groups,
    }
    return render(request, 'peer_connect.html', context)


@login_required
def join_group(request, group_id):
    group = get_object_or_404(StudyGroup, id=group_id)

    if request.method != 'POST':
        messages.error(request, "Invalid method for joining a group.")
        return redirect('pc:peer_connect')

    try:
        if GroupMembership.objects.filter(group=group, user=request.user).exists():
            messages.info(request, f"You are already a member of {group.name}.")
        else:
            GroupMembership.objects.create(group=group, user=request.user)
            messages.success(request, f"Successfully joined the group: {group.name}!")
    except Exception as e:
        messages.error(request, f"Could not join group: {e}")

    return redirect('pc:peer_connect')


@login_required
def leave_group(request, group_id):
    group = get_object_or_404(StudyGroup, id=group_id)

    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)

    try:
        membership = GroupMembership.objects.filter(group=group, user=request.user).first()

        if membership:
            membership.delete()
            return JsonResponse({'status': 'success', 'message': f'You have left the group "{group.name}". Redirecting...'}, status=200)
        else:
            return JsonResponse({'error': 'You are not currently a member of this group.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'An unexpected error occurred: {e}'}, status=500)




@login_required
def delete_group(request, group_id):
    group = get_object_or_404(StudyGroup, id=group_id)

    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)

    if group.created_by != request.user:
        return JsonResponse({'error': 'You do not have permission to delete this group.'}, status=403)

    try:
        group_name = group.name
        group.delete()
        return JsonResponse({'status': 'success', 'message': f'Group "{group_name}" deleted successfully. Redirecting...'}, status=200)
    except Exception as e:
        return JsonResponse({'error': f'An unexpected error occurred: {e}'}, status=500)


@login_required
def chat_room(request, group_id):
    group = get_object_or_404(StudyGroup, id=group_id)

    if not GroupMembership.objects.filter(group=group, user=request.user).exists():
        messages.error(request, f"You must join the group '{group.name}' to view the chat.")
        return redirect('pc:peer_connect')

    is_creator = (group.created_by == request.user)

    context = {
        'group': group,
        'user': request.user,
        'is_creator': is_creator,
    }
    return render(request, 'chat_room.html', context)


@login_required
def send_message(request, group_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

    group = get_object_or_404(StudyGroup, id=group_id)

    if not GroupMembership.objects.filter(group=group, user=request.user).exists():
        return JsonResponse({'error': 'Permission denied. Not a group member.'}, status=403)

    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()

        if not content:
            return JsonResponse({'error': 'Message content cannot be empty.'}, status=400)

        GroupMessage.objects.create(
            group=group,
            user=request.user,
            content=content,
            timestamp=timezone.now()
        )
        return JsonResponse({'status': 'ok'}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def fetch_messages(request, group_id):
    group = get_object_or_404(StudyGroup, id=group_id)

    if not GroupMembership.objects.filter(group=group, user=request.user).exists():
        # Returns 403, which the JavaScript handles by redirecting.
        return JsonResponse({'error': 'Permission denied. Not a group member.'}, status=403)

    try:
        last_timestamp_str = request.GET.get('last_timestamp')
        messages_query = GroupMessage.objects.filter(group=group)

        if last_timestamp_str:
            try:
                # 1. Use dateutil.parser.isoparse for reliable parsing of the ISO string from JavaScript.
                last_timestamp = parser.isoparse(last_timestamp_str)

                # 2. Ensure the timestamp is timezone-aware, which is mandatory for comparisons in Django.
                if timezone.is_naive(last_timestamp):
                    # Make it aware using the default Django timezone setting (or UTC if that's your standard).
                    last_timestamp = timezone.make_aware(last_timestamp, timezone.get_default_timezone())

                # Filter for messages *newer* than the last one received
                messages_query = messages_query.filter(timestamp__gt=last_timestamp).order_by(
                    'timestamp').select_related('user')

                # If polling is working, this query usually returns only the new messages.

            except (ValueError, TypeError) as e:
                # If timestamp parsing fails, log it and treat it as a fresh load to prevent crash.
                print(f"Timestamp parsing failed: {e}. Defaulting to initial load.")
                # Fall through to the initial load logic below.
                messages_query = GroupMessage.objects.filter(group=group).order_by('-timestamp').select_related('user')[
                    :50]
                messages_query = messages_query[::-1]  # Reverse to display oldest first

        else:
            # Initial load logic (when 'last_timestamp' is not present)
            messages_query = messages_query.order_by('-timestamp').select_related('user')[:50]
            messages_query = messages_query[::-1]  # Reverse for chronological display

        final_messages = messages_query

        new_messages = [
            {
                'id': msg.id,
                'user_id': msg.user.id,
                'username': msg.user.username,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat(),
            }
            for msg in final_messages
        ]

        return JsonResponse({'messages': new_messages})

    except Exception as e:
        # Catch-all for any other critical crash
        print(f"CRITICAL FETCH MESSAGES ERROR: {e}")
        return JsonResponse({'error': f'A critical server error occurred: {type(e).__name__}: {str(e)}'}, status=500)
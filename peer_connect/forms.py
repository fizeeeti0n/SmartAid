from django import forms
from .models import StudyGroup, GroupMessage

# Form for creating a new study group
class StudyGroupForm(forms.ModelForm):
    class Meta:
        model = StudyGroup
        fields = ['name', 'description']

        # Adding Tailwind classes for styling (matching the template structure)
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Group Name (e.g., Calculus II Study)',
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-green-500 focus:border-green-500 transition shadow-sm',
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Describe your group’s focus and goals...',
                'rows': 4,
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-green-500 focus:border-green-500 transition shadow-sm resize-none',
            }),
        }

# Form for sending a message (Unused by AJAX view, but good for completeness/admin)
class GroupMessageForm(forms.ModelForm):
    class Meta:
        model = GroupMessage
        fields = ['content']

        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': 'Type your message...',
                'rows': 1,
                'class': 'w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 transition shadow-sm resize-none',
            }),
        }

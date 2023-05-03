from django import forms
from .models import Task

class TaskForm(forms.ModelForm):

    priority = forms.ChoiceField(choices=[('', 'Choose a priority')] + list(Task.PRIORITY_CHOICES), required=False)

    class Meta:
        model = Task
        fields = ['title', 'description', 'category', 'frequency', 'priority', 'completion_goal', 'completion_count']

        labels = {
            'title': 'Task Title',
            'description': 'Task Description',
            'category': 'Task Category',
            'frequency': 'Task Frequency',
            'priority': 'Task Priority',
            'completion_goal': 'Completion Goal',
            'completion_count': 'Completion Count',
        }

        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter task title'}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter task description'}),
            'category': forms.Select(choices=[('', 'Choose a category')] + list(Task.CATEGORY_CHOICES)),
            'frequency': forms.Select(choices=Task.FREQUENCY_CHOICES),
            'priority': forms.Select(choices=[('', 'Choose a priority')] + list(Task.PRIORITY_CHOICES)),
            'completion_goal': forms.NumberInput(attrs={'min': 1, 'required': False}),
        }
from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    priority = forms.ChoiceField(choices=[('', 'Choose a priority')] + list(Task.PRIORITY_CHOICES), required=False)
    completion_count = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}), required=False)
    completion_goal = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'value': 1}), required=True)

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
            'completion_goal': forms.NumberInput(attrs={'class': 'form-control'}),
            'completion_count': forms.NumberInput(attrs={'class': 'form-control'}),
        }

        help_texts = {
            'completion_count': 'This field is required for weekly and monthly tasks.',
            'completion_goal': 'This field is required for weekly and monthly tasks.',
        }
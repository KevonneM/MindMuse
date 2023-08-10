from django import forms
from .models import Task, Passion, PassionActivity, Quote

class TaskForm(forms.ModelForm):
    title = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'placeholder': 'Enter task title'}))
    priority = forms.ChoiceField(choices=[('', 'Choose a priority')] + list(Task.PRIORITY_CHOICES), required=False)

    class Meta:
        model = Task
        fields = ['title', 'description', 'category', 'frequency', 'priority']

        labels = {
            'title': 'Task Title',
            'description': 'Task Description',
            'category': 'Task Category',
            'frequency': 'Task Frequency',
            'priority': 'Task Priority',
        }

        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter task title'}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter task description'}),
            'category': forms.Select(choices=[('', 'Choose a category')] + list(Task.CATEGORY_CHOICES)),
            'frequency': forms.Select(choices=Task.FREQUENCY_CHOICES),
            'priority': forms.Select(choices=[('', 'Choose a priority')] + list(Task.PRIORITY_CHOICES)),
        }

class PassionForm(forms.ModelForm):
    class Meta:
        model = Passion
        fields = ['name', 'category', 'description']

    new_category_name = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_category_name'].widget.attrs.update({
            'placeholder': 'New category name'
        })

hour_choices = [(i, f"{i} hours") for i in range(0, 25)]
minute_choices = [(i, f"{i} minutes") for i in range(0, 61, 5)]

class PassionActivityForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    hour = forms.ChoiceField(choices=hour_choices, widget=forms.Select(attrs={'class': 'scrollable-dropdown'}))
    minute = forms.ChoiceField(choices=minute_choices, widget=forms.Select(attrs={'class': 'scrollable-dropdown'}))

    class Meta:
        model = PassionActivity
        fields = ['date', 'duration']

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['quote', 'author']
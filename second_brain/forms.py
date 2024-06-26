from django import forms
from .models import Task, Passion, PassionActivity, Quote, Event
from  datetime import timedelta

class EventForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    start_time = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))
    end_time = forms.TimeField(widget=forms.TimeInput(format='%H:%M'))

    class Meta:
        model = Event
        fields = ['title', 'description', 'start_date', 'start_time', 'end_date', 'end_time']

        labels = {
            'title': 'Event Title',
            'description': 'Event Description',
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'start_time': 'Start Time',
            'end_time': 'End Time',
        }

        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter event title'}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter event description'}),
        }

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
        fields = ['name', 'category', 'description', 'color']

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
        fields = ['date', 'hour', 'minute']

    def clean(self):
        cleaned_data = super().clean()

        hour = int(cleaned_data.get("hour"))
        minute = int(cleaned_data.get("minute"))

        cleaned_data["duration"] = timedelta(hours=hour, minutes=minute)

        return cleaned_data

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['quote', 'author']
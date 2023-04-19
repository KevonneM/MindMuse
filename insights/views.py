from django.shortcuts import render

# Create your views here.

def insights(request):
    context = {'url_name': 'insights:insights'}
    return render(request, 'insights.html', context)
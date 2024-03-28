from django.shortcuts import get_object_or_404
from .models import SecondBrainColorSelection

def color_context(request):
    if not request.user.is_authenticated:
        return{'color_data': {
            'background-color' : '#2D2350',
            'navbar-color' : '#452475',
            'button-color' : '#7638C2',
            'tab-color' : '#A78EEF',
            'dropdown-color' : '#452475',
            'logo-greeting-color' : '#FFFFFF',
            'card-header-color' : '#673AB7',
            'card-interior-color' : '#58349D',
            'card-header-text-color' : '#D3D3D3',
            'button-text-color' : '#FFFFFF',
            'tab-text-color' : '#D3D3D3',
            'dropdown-text-color' : '#D3D3D3',
            'small-text-color' : '#D3D3D3',
        }}

    color_selection = get_object_or_404(SecondBrainColorSelection, user=request.user)

    if color_selection:

        color_data = {
            'background-color': color_selection.background_color,
                'navbar-color': color_selection.navigation_bar_color,
                'button-color': color_selection.button_color,
                'tab-color': color_selection.tab_color,
                'dropdown-color': color_selection.dropdown_color,
                'logo-greeting-color': color_selection.logo_and_greeting_color,
                'card-header-color': color_selection.card_header_color,
                'card-interior-color': color_selection.card_interior_color,
                'card-header-text-color': color_selection.title_text,
                'button-text-color': color_selection.button_text,
                'tab-text-color': color_selection.tab_text,
                'dropdown-text-color': color_selection.dropdown_text,
                'small-text-color': color_selection.text_color,
        }
    else:
        color_data = {
            'background-color' : '#2D2350',
            'navbar-color' : '#452475',
            'button-color' : '#7638C2',
            'tab-color' : '#A78EEF',
            'dropdown-color' : '#452475',
            'logo-greeting-color' : '#FFFFFF',
            'card-header-color' : '#673AB7',
            'card-interior-color' : '#58349D',
            'card-header-text-color' : '#D3D3D3',
            'button-text-color' : '#FFFFFF',
            'tab-text-color' : '#D3D3D3',
            'dropdown-text-color' : '#D3D3D3',
            'small-text-color' : '#D3D3D3',
        }

    return {'color_data': color_data}
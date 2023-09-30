from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .models import Payment, CustomUser
import hashlib
import hmac
import json
from django.db import IntegrityError

# Create your views here.

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        email = request.POST.get('email', None).lower()
        payment_email = request.POST.get('paymentEmail', None)
        order_id = request.POST.get('orderID', None)

        payment = None

        if order_id and order_id.strip() != '':
            try:
                payment = Payment.objects.get(transaction_id=order_id)
            except Payment.DoesNotExist:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'error': 'No payment found for the provided Transaction ID.'})
                else:
                    return JsonResponse({'error': 'No payment found for the provided Transaction ID.'})

        elif payment_email:
            try:
                payment = Payment.objects.get(payment_email=payment_email, user__isnull=True)
            except Payment.DoesNotExist:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'error': 'No payment found for the provided payment email.'})
                else:
                    return JsonResponse({'error': 'No payment found for the provided payment email.'})
        else:
            return JsonResponse({'error': 'No matching payment information provided.'})

        if not payment:
            return JsonResponse({'error': 'No matching payment found. Please provide a valid transaction ID or payment email.'})

        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({'error': 'That e-mail is currently in use.'})

        else:
            if form.is_valid():
                user = form.save()

                payment.user = user
                payment.save()

                login(request, user)

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': 'ok', 'redirect_url': reverse('second_brain:home')})

            else:
                errors = json.loads(form.errors.as_json())
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'errors': errors})

    else:
        form = CustomUserCreationForm()

    if 'HTTP_X_REQUESTED_WITH' in request.META and request.META['HTTP_X_REQUESTED_WITH'] == 'XMLHttpRequest':
        return render(request, 'registration/_signup.html', {'form': form})
    else:
        return render(request, 'registration/signup.html', {'form': form})

def custom_login_view(request):
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'status': 'ok', 'redirect_url': reverse('second_brain:home')})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid credentials'})
        else:
            return redirect('second_brain:home')
    else:
        form = AuthenticationForm()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, 'registration/_login.html', {'form': form})
        else:
            return redirect('second_brain:home')

class CustomPasswordResetView(PasswordResetView):

    ajax_template_name = 'registration/_forgot_password.html'

    def get_template_names(self):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return [self.ajax_template_name]
        return super().get_template_names()
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 302:
            return JsonResponse({"success": "ok"})
        else:
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                form_content = render_to_string(self.ajax_template_name, self.get_context_data())
                return JsonResponse({"success": "fail", "form_content": form_content}, status=400)
            return JsonResponse({"success": "fail"}, status=400)

from decouple import config
WEBHOOK_SECRET = config('WEBHOOK_SECRET')

@csrf_exempt
def lemon_squeezy_webhook(request):
    CustomUser = get_user_model()
    # Get lemonsqueezy signature from request header.
    received_signature = request.META.get('HTTP_X_SIGNATURE', '') 

    # Decode request body
    payload_bytes = request.body
    payload_str = payload_bytes.decode('utf-8')
    payload_json = json.loads(payload_str)

    generated_signature = hmac.new(
        key=WEBHOOK_SECRET.encode(),
        msg=payload_bytes,
        digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(generated_signature, received_signature):
        return HttpResponseBadRequest('Invalid signature')

    event_name = payload_json['meta']['event_name']
    paymentEmail = payload_json['data']['attributes']['user_email']
    customer_id = payload_json['data']['attributes']['customer_id']

    payment, created = Payment.objects.select_for_update().get_or_create(
        transaction_id=customer_id, 
        defaults={'payment_status': False, 'payment_email': paymentEmail}
    )

    payment_status = False

    if event_name in ["order_created", "subscription_created", "subscription_payment_success", "subscription_updated", "subscription_resumed", "subscription_unpaused", "subscription_payment_recovered"]:
        payment_status = True
    elif event_name in ["order_refunded", "subscription_cancelled", "subscription_expired", "subscription_paused", "subscription_payment_failed"]:
        payment_status = False

    payment.payment_status = payment_status
    payment.save()
    
    return JsonResponse({'status': 'success'})

def link_existing_payment(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        payment_email = request.POST.get('payment_email')

        email = request.POST.get('email', None)
        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({'error': 'That e-mail is already in use.'})
        try:
            payment = Payment.objects.get(payment_email=payment_email, user__isnull=True)
            
            if form.is_valid():
                user = form.save()
                payment.user = user
                payment.save()
                login(request, user)
                return JsonResponse({'success': 'Account created and payment linked'})
                
            else:
                errors = json.loads(form.errors.as_json())
                return JsonResponse({'errors': errors})

        except Payment.DoesNotExist:
            return JsonResponse({'error': 'No unlinked payment found'})

    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/link_existing_payment.html', {'form': form})

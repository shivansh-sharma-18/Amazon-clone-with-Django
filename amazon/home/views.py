from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from .models import User
from .forms import SignupForm, LoginForm, ForgotPasswordForm, ResetPasswordForm

import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# ---------- Utility Functions ----------
def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(email, otp):
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")

    if not sender_email or not sender_password:
        print("Missing email credentials.")
        return False

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = email
        msg["Subject"] = "Your OTP Code"
        msg.attach(MIMEText(f"Your OTP is: {otp}", "plain"))
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


# ---------- Views ----------
def index(request):
    user_email = request.session.get('user')
    user = User.objects.filter(email=user_email).first() if user_email else None
    return render(request, 'index.html', {
        'user': user,
        'google_maps_api_key': os.getenv("GOOGLE_MAPS_API_KEY")
    })


def signup(request):
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data['email']
        phone = form.cleaned_data['phone']
        
        # Check if the email or phone already exists
        if User.objects.filter(email=email).exists() or User.objects.filter(phone=phone).exists():
            messages.error(request, "User already registered with this email or phone!")
        else:
            # Create the user object
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data['password'])  # Hash the password
            user.save()  # Save the user instance in the database
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('login')
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        identifier = form.cleaned_data['identifier'].lower()
        password = form.cleaned_data['password']
        user = User.objects.filter(email=identifier).first() or User.objects.filter(phone=identifier).first()
        if user and check_password(password, user.password):
            request.session['user'] = user.email  # Store email in session
            messages.success(request, "Login successful!")
            return redirect('index')
        else:
            messages.error(request, "Invalid credentials!")
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    request.session.pop('user', None)
    messages.info(request, "Logged out successfully!")
    return redirect('index')


def forgot_password(request):
    form = ForgotPasswordForm(request.POST or None)
    request.session.pop('reset_email', None)
    if request.method == "POST" and form.is_valid():
        identifier = form.cleaned_data['identifier'].lower()
        user = User.objects.filter(email=identifier).first() or User.objects.filter(phone=identifier).first()
        if not user:
            messages.error(request, "No account found with this email or phone!")
        else:
            otp = generate_otp()
            request.session['reset_email'] = user.email
            request.session[f'otp_{user.email}'] = otp
            if send_otp_email(user.email, otp):
                messages.info(request, "OTP has been sent to your email.")
                return redirect('reset_password')
            messages.error(request, "Failed to send OTP. Please try again.")
    return render(request, 'forgot_password.html', {'form': form})


def reset_password(request):
    email = request.session.get('reset_email')
    stored_otp = request.session.get(f'otp_{email}')
    form = ResetPasswordForm(request.POST or None)

    if not email:
        messages.error(request, "Session expired. Please request a new OTP.")
        return redirect('forgot_password')

    if request.method == "POST" and form.is_valid():
        otp = form.cleaned_data['otp']
        new_password = form.cleaned_data['new_password']
        if otp != stored_otp:
            messages.error(request, "Invalid OTP!")
        else:
            user = User.objects.filter(email=email).first()
            if user:
                user.password = make_password(new_password)
                user.save()
                request.session.pop('reset_email')
                request.session.pop(f'otp_{email}', None)
                messages.success(request, "Password reset successfully! Please log in.")
                return redirect('login')
    return render(request, 'reset_password.html', {'form': form})


def profile(request):
    if 'user' not in request.session:
        messages.warning(request, "You need to log in to view your profile.")
        return redirect('login')

    user = User.objects.filter(email=request.session['user']).first()
    if not user:
        messages.error(request, "User not found.")
        return redirect('login')
    return render(request, 'profile.html', {'user': user})


# ---------- Cart and Checkout ----------
def cart(request):
    cart_items = request.session.get('cart', [])
    return render(request, 'cart.html', {'cart_items': cart_items})


def checkout(request):
    cart = request.session.get('cart', [])
    total_price = sum(item['price'] * item['quantity'] for item in cart)
    delivery_charges = 0 if total_price >= 500 else 50
    grand_total = total_price + delivery_charges

    if request.method == 'POST':
        return render(request, 'order_confirmation.html', {
            'grand_total': grand_total,
            'delivery_charges': delivery_charges
        })

    return render(request, 'checkout.html', {
        'cart': cart,
        'total_price': total_price,
        'delivery_charges': delivery_charges,
        'grand_total': grand_total
    })


def order_confirmation(request):
    return render(request, 'order_confirmation.html')


# ---------- Product Categories ----------
def clothes(request): return render(request, 'clothes.html')
def health(request): return render(request, 'health.html')
def beauty(request): return render(request, 'beauty.html')
def orders(request): return render(request, 'order.html')
def fashion_trends(request): return render(request, 'fashion_trends.html')
def mobiles(request): return render(request, 'mobiles.html')
def new_arrival_toys(request): return render(request, 'new_arrival_toys.html')
def pet_care(request): return render(request, 'pet_care.html')
def furniture(request): return render(request, 'furniture.html')


# ---------- AI Chatbot ----------
def chatbot(request):
    return render(request, 'chatbot.html')


# @csrf_exempt
# def get_ai_response(request):
#     if request.method == "POST":
#         try:
#             import json
#             data = json.loads(request.body)
#             user_message = data.get('message')
#             model = genai.GenerativeModel('gemini-pro')
#             response = model.generate_content(user_message)
#             return JsonResponse({'response': response.text})
#         except Exception as e:
#             print(f"AI Error: {e}")
#             return JsonResponse({'response': 'An error occurred while processing your request.'})
#     return JsonResponse({'response': 'Invalid request method.'})

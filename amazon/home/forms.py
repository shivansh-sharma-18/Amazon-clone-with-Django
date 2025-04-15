from django import forms
from .models import User
from django.core.validators import RegexValidator, MinLengthValidator
from django.core.exceptions import ValidationError

# -------------------------------
# Signup Form
# -------------------------------
class SignupForm(forms.ModelForm):
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        required=True
    )

    class Meta:
        model = User
        fields = ['name', 'email', 'phone', 'dob', 'gender', 'password']
        widgets = {
            'password': forms.PasswordInput(attrs={'class': 'form-input'}),
            'dob': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)

        # Add phone validation (exactly 10 digits)
        self.fields['phone'].validators.append(
            RegexValidator(
                regex=r'^\d{10}$',
                message="Phone number must be exactly 10 digits."
            )
        )

        # Add password length validation
        self.fields['password'].validators.append(
            MinLengthValidator(
                limit_value=8,
                message="Password must be at least 8 characters."
            )
        )

        # Replace gender field with a dropdown
        self.fields['gender'] = forms.ChoiceField(
            choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
            required=True
        )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        # Ensure passwords match
        if password and confirm and password != confirm:
            self.add_error('confirm_password', "Passwords must match.")

        return cleaned_data


# -------------------------------
# Login Form
# -------------------------------
class LoginForm(forms.Form):
    identifier = forms.CharField(
        label="Email or Phone",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        required=True
    )


# -------------------------------
# Forgot Password Form
# -------------------------------
class ForgotPasswordForm(forms.Form):
    identifier = forms.CharField(
        label="Email or Phone",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )


# -------------------------------
# Reset Password Form
# -------------------------------
class ResetPasswordForm(forms.Form):
    otp = forms.CharField(
        label="OTP",
        validators=[
            RegexValidator(
                regex=r'^\d{6}$',
                message="Enter a valid 6-digit OTP."
            )
        ],
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        validators=[
            MinLengthValidator(
                8,
                message="Password must be at least 8 characters."
            )
        ],
        required=True
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        # Ensure new password and confirm password match
        if new_password != confirm_password:
            self.add_error('confirm_password', "Passwords must match.")
        
        return cleaned_data

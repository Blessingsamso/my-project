from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from app.models import User, UserRole


TAILWIND_INPUT = 'form-control w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-slate-900 shadow-sm transition placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200'
TAILWIND_SELECT = 'form-select w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-slate-900 shadow-sm transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200'


class UserRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=[(UserRole.BUYER, 'Land Buyer'), (UserRole.SELLER, 'Land Seller')],
        widget=forms.Select(attrs={'class': TAILWIND_SELECT}),
        initial=UserRole.BUYER,
        help_text="Select whether you want to buy land or list land for sale"
    )
    email = forms.EmailField(
        required=True,
        error_messages={'required': 'Email address is required.', 'invalid': 'Please enter a valid email address.'},
        widget=forms.EmailInput(attrs={'placeholder': 'name@example.com', 'class': TAILWIND_INPUT})
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '+1 (555) 000-0000', 'class': TAILWIND_INPUT})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'phone')
        error_messages = {
            'username': {
                'required': 'Username is required.',
                'unique': 'A user with that username already exists.',
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = TAILWIND_INPUT

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email address already exists.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('A user with that username already exists.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'The two password fields didn’t match.')
        return cleaned_data


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        error_messages={'required': 'Username or email is required.'},
        widget=forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'Username or Email'})
    )
    password = forms.CharField(
        error_messages={'required': 'Password is required.'},
        widget=forms.PasswordInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'Password'})
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if not username:
            self.add_error('username', 'Username or email is required.')
        if not password:
            self.add_error('password', 'Password is required.')

        if username and password:
            username = username.strip()
            resolved_username = username
            # If user provided an email address instead of username, resolve username
            if '@' in username or not User.objects.filter(username=username).exists():
                user_obj = User.objects.filter(email__iexact=username).first()
                if user_obj:
                    resolved_username = user_obj.username

            self.user_cache = authenticate(self.request, username=resolved_username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    "Invalid username/email or password. Please check your credentials.",
                    code='invalid_login',
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

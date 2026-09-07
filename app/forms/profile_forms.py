from django import forms
from app.models import User, SellerWallet


TAILWIND_INPUT = 'form-control w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-slate-900 shadow-sm transition placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200'
TAILWIND_SELECT = 'form-select w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-slate-900 shadow-sm transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200'


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'profile_picture', 'bio']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
            'last_name': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
            'email': forms.EmailInput(attrs={'class': TAILWIND_INPUT}),
            'phone': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
            'profile_picture': forms.FileInput(attrs={'class': TAILWIND_INPUT}),
            'bio': forms.Textarea(attrs={'class': TAILWIND_INPUT, 'rows': 4}),
        }


class SellerWalletForm(forms.ModelForm):
    label = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'e.g. Ethereum Wallet, Solana Wallet (Optional)'})
    )

    class Meta:
        model = SellerWallet
        fields = ['currency', 'wallet_address', 'label', 'is_default']
        widgets = {
            'currency': forms.Select(attrs={'class': TAILWIND_SELECT, 'id': 'id_wallet_currency'}),
            'wallet_address': forms.TextInput(attrs={'class': TAILWIND_INPUT + ' font-monospace', 'placeholder': '0x... or Solana/BTC address'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'h-4 w-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500'}),
        }

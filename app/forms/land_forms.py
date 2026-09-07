from django import forms
from app.models import LandListing, Transaction, ZoningType, LandImage
from app.utils import get_state_choices, get_lgas_for_state, convert_crypto_to_usd, EXCHANGE_RATES


TAILWIND_INPUT = 'form-control w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-slate-900 shadow-sm transition placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200'
TAILWIND_SELECT = 'form-select w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-slate-900 shadow-sm transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200'


class LandListingForm(forms.ModelForm):
    state = forms.ChoiceField(
        choices=[('', 'Select State / FCT')] + get_state_choices(),
        widget=forms.Select(attrs={'class': TAILWIND_SELECT, 'id': 'id_state'}),
        required=True
    )
    lga = forms.CharField(
        required=False,
        widget=forms.Select(attrs={'class': TAILWIND_SELECT, 'id': 'id_lga'}),
        help_text="Select Local Government Area"
    )
    parcel_id = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'e.g. C of O / Survey No. LA/2026/0942 (Optional)'}),
        help_text="Title document number (C of O, Gazette, Excision, or Survey Plan No.)"
    )
    price_usd = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': TAILWIND_INPUT + ' bg-slate-50',
            'id': 'id_price_usd',
            'readonly': 'readonly',
            'step': '0.01',
            'placeholder': 'Calculated automatically'
        }),
        help_text="Auto-calculated USD/USDT value based on exchange rates"
    )

    class Meta:
        model = LandListing
        fields = [
            'title', 'description', 'state', 'lga', 'location', 'address', 'latitude', 'longitude',
            'crypto_currency', 'price_crypto', 'price_usd', 'size_sqm', 'size_acres',
            'zoning_type', 'parcel_id', 'featured_image'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'e.g. 2 Plots of Commercial Land in Lekki Phase 1, Lagos'}),
            'description': forms.Textarea(attrs={'class': TAILWIND_INPUT, 'rows': 5, 'placeholder': 'Describe property terrain (dry land/fenced), C of O / Survey status, electricity, road access...'}),
            'location': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'e.g. Lekki Phase 1, Off Freedom Way'}),
            'address': forms.Textarea(attrs={'class': TAILWIND_INPUT, 'rows': 2, 'placeholder': 'e.g. Off Freedom Way, Lekki Phase 1, Lagos State'}),
            'latitude': forms.NumberInput(attrs={'class': TAILWIND_INPUT, 'step': '0.000001', 'placeholder': '6.4549'}),
            'longitude': forms.NumberInput(attrs={'class': TAILWIND_INPUT, 'step': '0.000001', 'placeholder': '3.4246'}),
            'crypto_currency': forms.Select(attrs={'class': TAILWIND_SELECT, 'id': 'id_crypto_currency'}),
            'price_crypto': forms.NumberInput(attrs={'class': TAILWIND_INPUT, 'id': 'id_price_crypto', 'step': '0.000001', 'placeholder': 'e.g. 12'}),
            'size_sqm': forms.NumberInput(attrs={'class': TAILWIND_INPUT, 'step': '0.01', 'placeholder': 'e.g. 600 (1 Standard Plot)'}),
            'size_acres': forms.NumberInput(attrs={'class': TAILWIND_INPUT, 'step': '0.01', 'placeholder': 'e.g. 1.0 (Acres / Hectares)'}),
            'zoning_type': forms.Select(attrs={'class': TAILWIND_SELECT}),
            'featured_image': forms.FileInput(attrs={'class': TAILWIND_INPUT}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        state_val = None
        if self.is_bound:
            state_val = self.data.get('state')
        elif self.instance and self.instance.pk:
            state_val = self.instance.state

        if state_val:
            lgas = get_lgas_for_state(state_val)
            self.fields['lga'].widget = forms.Select(
                choices=[('', 'Select LGA')] + [(lga, lga) for lga in lgas],
                attrs={'class': TAILWIND_SELECT, 'id': 'id_lga'}
            )
        else:
            self.fields['lga'].widget = forms.Select(
                choices=[('', 'Select State First')],
                attrs={'class': TAILWIND_SELECT, 'id': 'id_lga'}
            )

    def clean(self):
        cleaned_data = super().clean()
        price_crypto = cleaned_data.get('price_crypto')
        crypto_currency = cleaned_data.get('crypto_currency')

        if price_crypto and crypto_currency:
            cleaned_data['price_usd'] = convert_crypto_to_usd(price_crypto, crypto_currency)
        return cleaned_data


class LandFilterForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search area, keyword, or Title Doc / Survey No...'}))
    state = forms.ChoiceField(
        required=False,
        choices=[('', 'All States')] + get_state_choices(),
        widget=forms.Select(attrs={'class': TAILWIND_SELECT, 'id': 'filter_state'})
    )
    lga = forms.CharField(
        required=False,
        widget=forms.Select(attrs={'class': TAILWIND_SELECT, 'id': 'filter_lga'}),
    )
    zoning = forms.ChoiceField(
        required=False,
        choices=[('', 'All Zoning Categories')] + list(ZoningType.choices),
        widget=forms.Select(attrs={'class': TAILWIND_SELECT})
    )
    crypto_currency = forms.ChoiceField(
        required=False,
        choices=[('', 'All Crypto')] + [('ETH', 'ETH'), ('SOL', 'SOL'), ('BTC', 'BTC'), ('USDT', 'USDT'), ('NGN', 'NGN')],
        widget=forms.Select(attrs={'class': TAILWIND_SELECT})
    )
    min_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'Min USD'}))
    max_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'Max USD'}))
    min_size = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': TAILWIND_INPUT, 'placeholder': 'Min Sqm'}))
    sort = forms.ChoiceField(
        required=False,
        choices=[
            ('-created_at', 'Newest First'),
            ('price_usd', 'Price: Low to High'),
            ('-price_usd', 'Price: High to Low'),
            ('-size_sqm', 'Largest Land Area'),
        ],
        widget=forms.Select(attrs={'class': TAILWIND_SELECT})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        state_val = self.data.get('state') if self.is_bound else None
        if state_val:
            lgas = get_lgas_for_state(state_val)
            self.fields['lga'].widget = forms.Select(
                choices=[('', 'All LGAs')] + [(lga, lga) for lga in lgas],
                attrs={'class': TAILWIND_SELECT, 'id': 'filter_lga'}
            )
        else:
            self.fields['lga'].widget = forms.Select(
                choices=[('', 'All LGAs')],
                attrs={'class': TAILWIND_SELECT, 'id': 'filter_lga'}
            )


class SubmitOfferForm(forms.ModelForm):
    offer_price_usd = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': TAILWIND_INPUT + ' bg-slate-50',
            'id': 'id_offer_price_usd',
            'readonly': 'readonly',
            'step': '0.01',
            'placeholder': 'Calculated automatically'
        }),
        help_text="Auto-calculated USD/USDT valuation"
    )

    class Meta:
        model = Transaction
        fields = ['crypto_currency', 'offer_price_crypto', 'offer_price_usd', 'buyer_wallet_address', 'notes']
        widgets = {
            'crypto_currency': forms.TextInput(attrs={'class': TAILWIND_INPUT + ' bg-slate-50', 'id': 'id_offer_crypto_currency', 'readonly': 'readonly'}),
            'offer_price_crypto': forms.NumberInput(attrs={'class': TAILWIND_INPUT, 'id': 'id_offer_price_crypto', 'step': '0.000001'}),
            'buyer_wallet_address': forms.TextInput(attrs={'class': TAILWIND_INPUT, 'placeholder': '0x... your wallet address'}),
            'notes': forms.Textarea(attrs={'class': TAILWIND_INPUT, 'rows': 3, 'placeholder': 'Optional offer message to land seller or escrow preferences...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        offer_price_crypto = cleaned_data.get('offer_price_crypto')
        crypto_currency = cleaned_data.get('crypto_currency')

        if offer_price_crypto and crypto_currency:
            cleaned_data['offer_price_usd'] = convert_crypto_to_usd(offer_price_crypto, crypto_currency)
        return cleaned_data


class CryptoPaymentTxForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['tx_hash']
        widgets = {
            'tx_hash': forms.TextInput(attrs={'class': TAILWIND_INPUT + ' font-monospace', 'placeholder': '0x... transaction hash from wallet'}),
        }

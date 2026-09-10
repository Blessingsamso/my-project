from django.http import JsonResponse
from decimal import Decimal
from app.utils.exchange_rates import convert_crypto_to_usd, NAIRA_PER_USD

def convert_crypto_to_naira_api(request):
    amount = request.GET.get('amount')
    currency = request.GET.get('currency')
    if not amount or not currency:
        return JsonResponse({'naira_amount': '0.00'})
    
    usd_value = convert_crypto_to_usd(amount, currency)
    naira_value = usd_value * NAIRA_PER_USD
    return JsonResponse({'naira_amount': str(naira_value.quantize(Decimal('0.01')))})

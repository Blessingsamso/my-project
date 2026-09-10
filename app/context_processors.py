from notifications.models.notification import Notification
from app.models import Transaction, SavedListing, UserRole, LandListing
from app.utils import get_all_rates_dict
from app.utils.exchange_rates import NAIRA_PER_USD


def crypto_land_context(request):
    """Context processor to inject crypto rates, unread notifications, and user stats across templates."""
    context = {
        'unread_notifications_count': 0,
        'saved_lands_count': 0,
        'active_offers_count': 0,
        'pending_listings_count': 0,
        'crypto_rates': get_all_rates_dict(),
        'exchange_rates': get_all_rates_dict(),
        'naira_per_usd': NAIRA_PER_USD,
    }

    if request.user.is_authenticated:
        context['unread_notifications_count'] = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
        context['recent_notifications'] = Notification.objects.filter(
            recipient=request.user
        ).order_by('-created_at')[:5]
        
        context['saved_lands_count'] = SavedListing.objects.filter(user=request.user).count()

        if request.user.is_buyer():
            context['active_offers_count'] = Transaction.objects.filter(
                buyer=request.user,
                status__in=['offer_submitted', 'accepted', 'payment_pending', 'escrow_locked']
            ).count()
        elif request.user.is_seller():
            context['active_offers_count'] = Transaction.objects.filter(
                seller=request.user,
                status__in=['offer_submitted', 'payment_pending', 'escrow_locked']
            ).count()
            
        if request.user.is_admin_user():
            context['pending_listings_count'] = LandListing.objects.filter(
                status=LandListing.Status.PENDING
            ).count()

    return context

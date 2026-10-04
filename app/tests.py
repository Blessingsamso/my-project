from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from app.models import User, UserRole, LandListing, ZoningType, Transaction, SavedListing, SellerWallet


class CryptoLandBuyingTests(TestCase):
    def setUp(self):
        # Mock external push notification service to prevent network timeouts during testing
        self.patcher = patch('notifications.notification_services.NotificationService.send_external_push')
        self.mock_push = self.patcher.start()
        self.addCleanup(self.patcher.stop)

        # Create Buyer
        self.buyer = User.objects.create_user(
            username='buyer1',
            email='buyer1@crypto.io',
            password='password123',
            role=UserRole.BUYER,
            first_name='Bob',
            last_name='Buyer',
            crypto_wallet_address='0xBuyer123456789'
        )

        # Create Seller
        self.seller = User.objects.create_user(
            username='seller1',
            email='seller1@crypto.io',
            password='password123',
            role=UserRole.SELLER,
            first_name='Sally',
            last_name='Seller',
            crypto_wallet_address='0xSeller987654321',
            is_verified_seller=True
        )
        SellerWallet.objects.create(
            user=self.seller,
            label='Primary ETH Wallet',
            currency='ETH',
            wallet_address='0xSeller987654321',
            is_default=True
        )

        # Create Admin
        self.admin = User.objects.create_superuser(
            username='admin1',
            email='admin@crypto.io',
            password='password123',
            role=UserRole.ADMIN,
            is_staff=True
        )

        # Create Another User (Unrelated third-party)
        self.other_user = User.objects.create_user(
            username='stranger',
            email='stranger@crypto.io',
            password='password123',
            role=UserRole.BUYER
        )

        # Create Land Listing
        self.land = LandListing.objects.create(
            title='Beachfront Paradise Parcel',
            description='Gorgeous 2-acre plot on white sand beach.',
            location='Malibu, California, USA',
            price_crypto=15.5,
            crypto_currency='ETH',
            price_usd=49600.00,
            size_sqm=8093.00,
            size_acres=2.00,
            zoning_type=ZoningType.RESIDENTIAL,
            parcel_id='CA-MAL-2026-9001',
            deed_verified=True,
            seller=self.seller,
            status=LandListing.Status.AVAILABLE
        )

    def test_land_list_view(self):
        response = self.client.get(reverse('app:land_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Beachfront Paradise Parcel')
        self.assertContains(response, 'ETH')

    def test_land_detail_view(self):
        response = self.client.get(reverse('app:land_detail', kwargs={'slug': self.land.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Beachfront Paradise Parcel')
        self.assertContains(response, 'Malibu, California, USA')

    def test_seller_create_land(self):
        self.client.login(username='seller1', password='password123')
        response = self.client.post(reverse('app:create_land'), {
            'title': 'Highland Ranch Plot',
            'description': '10-acre mountain parcel.',
            'state': 'Adamawa',
            'lga': 'Gombi',
            'location': 'Gombi District',
            'price_crypto': '3.2',
            'crypto_currency': 'ETH',
            'price_usd': '10240.00',
            'size_sqm': '40468.00',
            'size_acres': '10.00',
            'zoning_type': ZoningType.RESIDENTIAL,
            'parcel_id': 'CO-DEN-2026-1122',
        })
        self.assertEqual(response.status_code, 302)
        created_land = LandListing.objects.get(parcel_id='CO-DEN-2026-1122')
        self.assertEqual(created_land.seller, self.seller)

    def test_buyer_submit_offer(self):
        self.client.login(username='buyer1', password='password123')
        response = self.client.post(reverse('app:submit_offer', kwargs={'slug': self.land.slug}), {
            'offer_price_crypto': '15.5',
            'crypto_currency': 'ETH',
            'offer_price_usd': '49600.00',
            'buyer_wallet_address': self.buyer.crypto_wallet_address,
            'notes': 'Ready to transfer to escrow immediately.',
        })
        self.assertEqual(response.status_code, 302)
        tx = Transaction.objects.filter(buyer=self.buyer, land=self.land).first()
        self.assertIsNotNone(tx)
        self.assertEqual(tx.status, Transaction.Status.OFFER_SUBMITTED)

    def test_seller_accept_offer_and_buyer_payment(self):
        # Create offer
        tx = Transaction.objects.create(
            land=self.land,
            buyer=self.buyer,
            seller=self.seller,
            offer_price_crypto=15.5,
            crypto_currency='ETH',
            offer_price_usd=49600.00,
            buyer_wallet_address=self.buyer.crypto_wallet_address,
            status=Transaction.Status.OFFER_SUBMITTED
        )

        # Seller accepts
        self.client.login(username='seller1', password='password123')
        response = self.client.post(reverse('app:respond_to_offer', kwargs={'transaction_id': tx.transaction_id}), {
            'action': 'accept'
        })
        self.assertEqual(response.status_code, 302)
        tx.refresh_from_db()
        self.assertEqual(tx.status, Transaction.Status.ACCEPTED)

        # Buyer submits payment hash
        self.client.login(username='buyer1', password='password123')
        response = self.client.post(reverse('app:submit_payment_hash', kwargs={'transaction_id': tx.transaction_id}), {
            'tx_hash': '0xABCDEF1234567890ETHHASH'
        })
        self.assertEqual(response.status_code, 302)
        tx.refresh_from_db()
        self.assertEqual(tx.status, Transaction.Status.ESCROW_LOCKED)
        self.assertEqual(tx.tx_hash, '0xABCDEF1234567890ETHHASH')

    def test_admin_confirm_escrow_payment(self):
        tx = Transaction.objects.create(
            land=self.land,
            buyer=self.buyer,
            seller=self.seller,
            offer_price_crypto=15.5,
            crypto_currency='ETH',
            offer_price_usd=49600.00,
            buyer_wallet_address=self.buyer.crypto_wallet_address,
            tx_hash='0xABCDEF1234567890ETHHASH',
            status=Transaction.Status.ESCROW_LOCKED
        )

        self.client.login(username='admin1', password='password123')
        response = self.client.get(reverse('app:confirm_escrow_payment', kwargs={'transaction_id': tx.transaction_id}))
        self.assertEqual(response.status_code, 302)

        tx.refresh_from_db()
        self.land.refresh_from_db()
        self.assertEqual(tx.status, Transaction.Status.COMPLETED)
        self.assertEqual(self.land.status, LandListing.Status.SOLD)

    def test_user_registration_with_role_without_wallet(self):
        response = self.client.post(reverse('app:register'), {
            'username': 'newbuyer',
            'email': 'newbuyer@example.com',
            'first_name': 'New',
            'last_name': 'Buyer',
            'role': UserRole.BUYER,
            'password1': 'x9$K#mP2!vL7qW1z',
            'password2': 'x9$K#mP2!vL7qW1z',
        })
        self.assertEqual(response.status_code, 302)
        new_user = User.objects.get(username='newbuyer')
        self.assertEqual(new_user.role, UserRole.BUYER)

    def test_lgas_api_endpoint(self):
        response = self.client.get(reverse('app:get_lgas_api') + '?state=Adamawa')
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data['state'], 'Adamawa')
        self.assertIn('Gombi', json_data['lgas'])
        self.assertIn('Michika', json_data['lgas'])

    def test_receipt_access_by_all_involved_parties(self):
        # Create an offer / transaction
        tx = Transaction.objects.create(
            land=self.land,
            buyer=self.buyer,
            seller=self.seller,
            offer_price_crypto=15.5,
            crypto_currency='ETH',
            offer_price_usd=49600.00,
            buyer_wallet_address=self.buyer.crypto_wallet_address,
            status=Transaction.Status.OFFER_SUBMITTED,
            notes='Initial purchase offer'
        )

        receipt_url = reverse('app:generate_receipt_pdf', kwargs={'transaction_id': tx.transaction_id})

        # 1. Unauthenticated user is redirected to login
        self.client.logout()
        res_anon = self.client.get(receipt_url)
        self.assertEqual(res_anon.status_code, 302)
        self.assertIn('login', res_anon.url)

        # 2. Buyer can view inline receipt
        self.client.login(username='buyer1', password='password123')
        res_buyer = self.client.get(receipt_url)
        self.assertEqual(res_buyer.status_code, 200)
        self.assertEqual(res_buyer['Content-Type'], 'application/pdf')
        self.assertIn('inline', res_buyer['Content-Disposition'])
        self.assertIn(str(tx.transaction_id), res_buyer['Content-Disposition'])

        # 3. Buyer can download receipt via ?download=1
        res_buyer_download = self.client.get(f"{receipt_url}?download=1")
        self.assertEqual(res_buyer_download.status_code, 200)
        self.assertEqual(res_buyer_download['Content-Type'], 'application/pdf')
        self.assertIn('attachment', res_buyer_download['Content-Disposition'])

        # 4. Seller can view and download receipt
        self.client.login(username='seller1', password='password123')
        res_seller = self.client.get(receipt_url)
        self.assertEqual(res_seller.status_code, 200)
        self.assertEqual(res_seller['Content-Type'], 'application/pdf')
        self.assertIn('inline', res_seller['Content-Disposition'])

        res_seller_download = self.client.get(f"{receipt_url}?download=1")
        self.assertEqual(res_seller_download.status_code, 200)
        self.assertIn('attachment', res_seller_download['Content-Disposition'])

        # 5. Platform Admin can view and download receipt
        self.client.login(username='admin1', password='password123')
        res_admin = self.client.get(receipt_url)
        self.assertEqual(res_admin.status_code, 200)
        self.assertEqual(res_admin['Content-Type'], 'application/pdf')

        # 6. Uninvolved third-party user is forbidden (403)
        self.client.login(username='stranger', password='password123')
        res_stranger = self.client.get(receipt_url)
        self.assertEqual(res_stranger.status_code, 403)

    def test_receipt_after_payment_completed(self):
        # Create completed transaction with payment tx_hash
        tx = Transaction.objects.create(
            land=self.land,
            buyer=self.buyer,
            seller=self.seller,
            offer_price_crypto=15.5,
            crypto_currency='ETH',
            offer_price_usd=49600.00,
            buyer_wallet_address=self.buyer.crypto_wallet_address,
            tx_hash='0x0123456789abcdef0123456789abcdef01234567',
            status=Transaction.Status.COMPLETED
        )

        receipt_url = reverse('app:generate_receipt_pdf', kwargs={'transaction_id': tx.transaction_id})

        # Buyer can download completed receipt
        self.client.login(username='buyer1', password='password123')
        response = self.client.get(receipt_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(len(response.content) > 0)

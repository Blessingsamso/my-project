document.addEventListener('DOMContentLoaded', function() {
  const priceInput = document.getElementById('id_price_crypto');
  const currencySelect = document.getElementById('id_crypto_currency');
  const nairaInput = document.getElementById('id_naira_price');

  // Helper to convert crypto to naira
  function updateNaira() {
    const price = priceInput.value;
    const currency = currencySelect.value;
    if (price && currency) {
        fetch('/api/convert-crypto-to-naira/?amount=' + price + '&currency=' + currency)
            .then(res => res.json())
            .then(data => {
                nairaInput.value = parseFloat(data.naira_amount).toFixed(2);
            });
    }
  }

  // Helper to convert naira to crypto (you might need a new API)
  function updateCrypto() {
    const naira = nairaInput.value;
    const currency = currencySelect.value;
    if (naira && currency) {
        fetch('/api/convert-naira-to-crypto/?amount=' + naira + '&currency=' + currency)
            .then(res => res.json())
            .then(data => {
                priceInput.value = parseFloat(data.crypto_amount).toFixed(6);
            });
    }
  }

  if (priceInput && currencySelect && nairaInput) {
      priceInput.addEventListener('input', updateNaira);
      currencySelect.addEventListener('change', updateNaira);
      nairaInput.addEventListener('input', updateCrypto);
  }
});

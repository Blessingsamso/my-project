with open('templates/app/create_land.html', 'r') as f:
    content = f.read()

# Replace Currency and Price order
currency_block = """        <div>
          <label class="mb-1 block text-xs font-semibold uppercase text-slate-500">Currency *</label>
          {{ form.crypto_currency }}
        </div>
        <div>
          <label class="mb-1 block text-xs font-semibold uppercase text-slate-500">Price *</label>
          {{ form.price_crypto }}
        </div>"""

price_and_currency_old = """      <div class="grid gap-4 md:grid-cols-2">
        <div>
          <label class="mb-1 block text-xs font-semibold uppercase text-slate-500">Price *</label>
          {{ form.price_crypto }}
        </div>
        <div>
          <label class="mb-1 block text-xs font-semibold uppercase text-slate-500">Currency *</label>
          {{ form.crypto_currency }}
        </div>
      </div>"""

content = content.replace(price_and_currency_old, """      <div class="grid gap-4 md:grid-cols-2">
        <div>
          <label class="mb-1 block text-xs font-semibold uppercase text-slate-500">Currency *</label>
          {{ form.crypto_currency }}
        </div>
        <div>
          <label class="mb-1 block text-xs font-semibold uppercase text-slate-500">Price *</label>
          {{ form.price_crypto }}
        </div>
        <div class="md:col-span-2">
           <label class="mb-1 block text-xs font-semibold uppercase text-slate-500">Naira Equivalent</label>
           <div id="naira_equivalent" class="text-emerald-700 font-bold p-3 border rounded-2xl bg-slate-50 border-slate-200">₦0.00</div>
        </div>
      </div>""")

with open('templates/app/create_land.html', 'w') as f:
    f.write(content)

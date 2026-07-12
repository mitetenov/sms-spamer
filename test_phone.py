from phone_utils import format_phone_ru
fmts = format_phone_ru('+79001234567')
for k, v in sorted(fmts.items()):
    print(f'  {k}: {v}')

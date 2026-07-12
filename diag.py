import sys
sys.path.insert(0, '.')
from services.registry import load_services
svcs = load_services()
for s in svcs:
    slug = s.service_name
    url = s.url
    ok = bool(slug and url.startswith('http'))
    if not ok:
        print(f'BAD: service_name={slug!r} url={url!r} type={type(s).__name__}')
print('Done checking.')

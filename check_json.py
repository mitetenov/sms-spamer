import json
with open('services/services.json') as f:
    data = json.load(f)
print(f'JSON entries: {len(data)}')
group_b = ['beeline_tv','cian','delimobil','dns','ekapusta','finuslugi','globus','invitro','joymoney','lenta','platiza','pochtabank','rostel','rutube','sber','sravni','start','vsk','yoomoney','zaimer']
missing = [s for s in group_b if s not in data]
print(f'Missing from JSON: {missing} ({len(missing)})')

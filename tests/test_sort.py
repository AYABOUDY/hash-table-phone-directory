from app import Directory, Record
D = Directory()
users = sorted([e.username for e in D.by_username.table if e.is_active()], key=lambda s: s.lower())
print('first 10 users:', users[:10])
D.insert(Record('5559999','zoe','Room Z'))
users = sorted([e.username for e in D.by_username.table if e.is_active()], key=lambda s: s.lower())
print('last 5 users:', users[-5:])

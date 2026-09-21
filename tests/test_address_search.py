from app import Directory
D = Directory()
print('Initially count:', sum(1 for e in D.by_username.table if e.is_active()))
D.load_samples()
print('After loading samples, count:', sum(1 for e in D.by_username.table if e.is_active()))
recs = D.search_all('Room 11', by='address')
print('Search address "Room 11" ->', len(recs))
for r in recs:
    print('  ', r.username, r.phone_number, 'address_hidden? ', r.address)

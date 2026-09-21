from app import Directory, Record

d = Directory()

# Search by username
entry, probes = d.search('alice', by='username')
print('Search username=alice ->', entry, 'probes=', probes)

# Search by phone
entry, probes = d.search('5550001', by='phone')
print('Search phone=5550001 ->', entry, 'probes=', probes)

# Insert new record
new = Record('5559999', 'zoe', 'Room 999')
probes = d.insert(new, by='username')
print('Insert zoe ->', probes)
entry, probes = d.search('zoe', by='username')
print('Search zoe ->', entry, 'probes=', probes)

# Delete by username
ok = d.delete('zoe', by='username')
print('Deleted zoe?', ok)
entry, probes = d.search('zoe', by='username')
print('Search zoe after delete ->', entry)

# Save and load
d.save('test_save.csv')
d2 = Directory()
d2.load('test_save.csv')
count = sum(1 for e in d2.by_username.table if e.is_active())
print('Loaded count:', count)
from app import Directory
D=Directory()
recs = D.search_all('Alice', by='username')
print('Found Alice (case-insensitive):', len(recs))
recs2 = D.search_all('5550001', by='phone')
print('Phone 5550001:', len(recs2))

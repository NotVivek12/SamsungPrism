import database

professors = database.load_professors_data()
print(f'Loaded {len(professors)} professors')
if professors:
    print(f'Sample professor: {professors[0]}')
else:
    print('No professors loaded!')

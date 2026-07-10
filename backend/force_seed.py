from app.dummy_data import generate_dummy_data
print("Force seeding the database...")
generate_dummy_data(force=True)
print("Database successfully synchronized and seeded!")

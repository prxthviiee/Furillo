import pandas as pd
from models import db, User
import os

def import_ngos(app):
    # Path to your Excel file
    file_path = os.path.join(os.getcwd(), 'NGO DATA.xlsx')

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False

    # Load the Excel data
    df = pd.read_excel(file_path)

    with app.app_context():
        for _, row in df.iterrows():
            ngo_user = User(
                username=row.get('Username', row.get('Name', '')).lower().replace(' ', '_'),
                email=row.get('Email', ''),
                password_hash='',  # Set a default or random password if needed
                user_type='ngo',
                is_profile_complete=True,
                ngo_name=row.get('Name', ''),
                ngo_established=row.get('Established', ''),
                ngo_occupancy=row.get('Occupancy', None),
                address=row.get('Address', ''),
                pin_code=row.get('Pin Code', ''),
                ngo_contact=row.get('Phone', ''),
                ngo_types_animals=row.get('Types of Animals', ''),
            )
            db.session.add(ngo_user)
        db.session.commit()
        print("✅ NGO data imported successfully!")
        return True

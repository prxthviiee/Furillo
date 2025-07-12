import pandas as pd
from models import db, NGO
from app import app  # assuming your Flask app is named 'app'
import os

# Path to your Excel file
file_path = os.path.join(os.getcwd(), 'berlin_ngos.xlsx')

# Load the Excel data
df = pd.read_excel(file_path)

with app.app_context():
    for _, row in df.iterrows():
        ngo = NGO(
            name=row['Name'],
            address=row['Address'],
            phone=row.get('Phone', ''),
            email=row.get('Email', ''),
            latitude=row.get('Latitude', None),
            longitude=row.get('Longitude', None)
        )
        db.session.add(ngo)

    db.session.commit()
    print("✅ NGO data imported successfully!")

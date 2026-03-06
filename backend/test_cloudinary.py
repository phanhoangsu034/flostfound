import os
from dotenv import load_dotenv
load_dotenv('c:/Users/dell 5411/Desktop/JS-CLUB/LÀM PROJECT/CTV-Team-1X-BET-23-1/backend/.env')
import cloudinary
import cloudinary.uploader
import cloudinary.api
try:
    print('Testing connection...')
    print(cloudinary.api.ping())
    print('Testing folder creation...')
    res = cloudinary.api.create_folder('flostfound/posts')
    print('Folder created:', res)
    print('Listing root folders...')
    folders = cloudinary.api.root_folders()
    for f in folders.get('folders', []):
        print(f['name'])
except Exception as e:
    print('Error:', e)

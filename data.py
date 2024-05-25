from datetime import datetime
import json
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rentify.settings')

django.setup()

from home.models import CustomUser, Property


def import_data_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        for item in data:
            model_name = item['model']
            fields = item['fields']
            if model_name == 'app.Property':
                owner_id = fields.pop('owner') 
                print(owner_id)# Get owner ID and remove from fields
                owner = CustomUser.objects.get(pk=owner_id)
                property = Property.objects.create(owner=owner, **fields)


if __name__ == "__main__":
    file_path = "./data.json" 
    import_data_from_json(file_path)
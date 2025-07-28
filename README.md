# Hostel-Management-System
# To connect with mongodb use this connection steps
Installation Steps:

1. Install Djongo and the MongoDB Python driver:
```bash
pip install djongo pymongo
```

2. In your `settings.py`, modify the DATABASES setting:
```python
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'your_db_name',
        'CLIENT': {
            'host': 'mongodb://localhost:27017',
            'username': 'your_username',  
            'password': 'your_password', 
            'authSource': 'admin', 
            'authMechanism': 'SCRAM-SHA-1'
        }
    }
}
```

3. Add to your `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    ...
    'djongo',
    ...
]

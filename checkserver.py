import requests
import sys

try:
    r = requests.get('http://localhost:5175', timeout=3)
    print(f'Status: {r.status_code}')
except Exception as e:
    print(f'Error: {e}')

try:
    r = requests.get('http://localhost:8000', timeout=3)
    print(f'Status: {r.status_code}')
except Exception as e:
    print(f'Error: {e}')

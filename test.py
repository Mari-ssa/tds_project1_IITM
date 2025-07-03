import requests

url = "http://127.0.0.1:5000/api/"
data = {
    "question": "What is the difference between a repository and a working directory in Git?"
}

response = requests.post(url, json=data)
print(response.status_code)
print(response.json())
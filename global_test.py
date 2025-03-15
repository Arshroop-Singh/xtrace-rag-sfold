import requests

url = "https://beta0-api.xtrace.ai/data"

payload = "{\n    \"index_name\": \"near-learning-club\",\n    \"context\": \"this is yet another test context\",\n    \"knowledge_base\": \"test\"\n}"
headers = {
    'x-api-key': 'pR4EPkE9AV5YlLVUlBqax5rN1jWMAPDbaO6Jysxp',
    'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)

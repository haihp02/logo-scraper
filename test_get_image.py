import requests
from io import BytesIO
from PIL import Image

response = requests.get('https://cdn.vectorstock.com/i/1000v/31/94/awesome-circle-gradient-logo-design-vector-26673194.jpg')
img = Image.open(BytesIO(response.content)).convert('RGB')
width, height = img.size
img = img.crop((0, 0, width, height - 80))
img.save('test.png')
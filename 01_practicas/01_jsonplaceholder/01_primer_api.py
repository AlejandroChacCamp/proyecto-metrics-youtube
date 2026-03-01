import requests
respuesta = requests.get("https://jsonplaceholder.typicode.com/posts/101")
print(respuesta.status_code)

datos = respuesta.json()
print(type(datos))
print("Título:", datos['title'])
print("body:", datos['body'])
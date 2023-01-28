# Servicio de Publicaciones

## Setup

```bash
docker compose up -d
```

## Endpoints

Puede ver la documentación de los endpoints en [http://localhost:8000/docs](http://localhost:8000/docs), esta **documentación es equivalente a un postman** (se puede [descargar en formato JSON](http://localhost:8000/openapi.json)). Esta modelada para cumplir con: [Esquema de publicaciones](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/entrega-1-proyecto-202311/wiki/Gesti%C3%B3n-de-publicaciones)

De querer probarlo en la consola de comandos puede hacerlo con:

```bash
# Crear post
curl --json '{ "routeId": 1, "userId": 1, "plannedStartDate": "2020-01-01T00:00:00", "plannedEndDate": "2020-01-01T00:00:00", "createdAt": "2020-01-01T00:00:00" }' localhost:8000
# Obtener post
curl localhost:8000/1
# Buscar post
curl localhost:8000?routeId=1
curl localhost:8000?filter=me
```

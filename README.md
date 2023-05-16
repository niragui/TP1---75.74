# TP1 75.74

Para ejecutar el sistena primero se deben levantar las imagenes del servidor con "make docker-compose-server-up" y luego las del cliente con "make docker-compose-clients-up"

Si se desean ver los valores de cada lado solo se debe ejecutar "make docker-compose-server-logs" para el servidor y "make docker-compose-client-logs" para el cliente.

Una vez finalizado deben cerrarse las imagenes con "make docker-compose-server-down" y "make docker-compose-client-down"

El sistema tambien incluye un archivo python para re-escribir el docker compose permitiendo asi que el sistema pueda escalarse como se desee. Para esto simplemente se debe ejecutar con python3 el archivo "docker_creater.py" y le pedira una serie de valores que define cuantos nodos de cada tipo se presentan.

Datasets from: https://www.kaggle.com/datasets/jeanmidev/public-bike-sharing-in-north-america

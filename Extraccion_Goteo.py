
import requests
import certifi
import json
import time

from requests.auth import HTTPBasicAuth

# Configuración general
API_BASE_URL = "https://api.goteo.org/v1/projects/"
CREDENCIALES = HTTPBasicAuth('', '')
CERTIFICADO = certifi.where()

# Función para consultar proyectos dentro de un rango de fechas
def recolectar_proyectos(fecha_inicio, fecha_fin):
    proyectos = []
    pagina = 1

    while True:
        parametros = {
            "from_date": fecha_inicio,
            "to_date": fecha_fin,
            "page": pagina,
            "limit": 100
        }

        respuesta = requests.get(API_BASE_URL, params=parametros, auth=CREDENCIALES, verify=CERTIFICADO)
        if respuesta.status_code != 200:
            print(f"Error en la página {pagina}: {respuesta.status_code}")
            break

        contenido = respuesta.json()
        elementos = contenido.get('items', [])
        if not elementos:
            break

        for item in elementos:
            print(f"ID: {item.get('id')} | Nombre: {item.get('name')}")

        proyectos.extend(elementos)
        pagina += 1
        time.sleep(3)

    return proyectos

# Función para consultar los detalles de un solo proyecto
def detalles_proyecto(proyecto_id):
    enlace = f"{API_BASE_URL}{proyecto_id}"
    respuesta = requests.get(enlace, auth=CREDENCIALES, verify=CERTIFICADO)

    if respuesta.status_code == 200:
        return respuesta.json()
    else:
        print(f"No se pudo obtener el proyecto {proyecto_id} (código {respuesta.status_code})")
        return None

# Flujo principal del script
if __name__ == "__main__":
    print("Iniciando recolección de proyectos...")

    lista_proyectos = recolectar_proyectos("2012-01-01", "2023-12-31")

    with open("proyectos_resumen.json", "w") as archivo:
        json.dump(lista_proyectos, archivo, indent=4)

    print(f"Se guardaron {len(lista_proyectos)} proyectos.")

    print("Consultando detalles individuales...")
    detalles_completos = []

    for proyecto in lista_proyectos:
        pid = proyecto.get("id")
        if pid:
            print(f"Obteniendo detalles para: {pid}")
            detalle = detalles_proyecto(pid)
            if detalle:
                detalles_completos.append(detalle)
            time.sleep(3)

    with open("proyectos_detalles.json", "w") as archivo:
        json.dump(detalles_completos, archivo, indent=4)

    print("Proceso finalizado.")

import requests
from io import StringIO

def download_csv_from_url(url):
    # Descarga el contenido del archivo
    response = requests.get(url)

    if response.status_code == 200:
        # Lee el contenido como CSV
        csv_content = StringIO(response.text)
        return csv_content
    else:
        raise Exception("Error al descargar el archivo", response)
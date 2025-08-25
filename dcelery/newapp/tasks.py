import time

from celery import group, shared_task
from django.core.management import call_command
from dcelery.celery_config import app
import logging
import requests
import re
import pandas as pd

logger = logging.getLogger(__name__)


@app.task(queue="tasks")
def management_command():
    resp = requests.get("http://app:8000/api/recipe/recipes")
    strllm = resp.json()   

    data = strllm["data"]  
    print(data)

    convocatorias = []
    titulo, apertura, cierre, link, alcance, objetivo = None, None, None, None, None, None

    for item in data:
        # Buscar títulos + alcance
        if "Alcance:" in item:
            partes = item.split("\nAlcance:")
            titulo = partes[0].strip()
            alcance = partes[1].split("\n")[0].strip()

            # objetivo (empieza con "El objetivo" o "Se busca")
            match_obj = re.search(r"(El objetivo.+|Se busca.+)", item, re.DOTALL)
            if match_obj:
                objetivo = match_obj.group(1).strip()

        # Buscar apertura
        elif item.startswith(" Apertura"):
            apertura = item.replace("Apertura", "").strip()

        # Buscar cierre
        elif item.startswith(" Cierre"):
            cierre = item.replace("Cierre", "").strip()

        # Buscar link
        elif "Más Información" in item:
            match = re.search(r"\((https?://[^\)]+)\)", item)
            if match:
                link = match.group(1)

            # Cuando ya tenemos todo, guardamos
            convocatorias.append({
                "titulo": titulo,
                "alcance": alcance,
                "objetivo": objetivo,
                "apertura": apertura,
                "cierre": cierre,
                "link": link
            })

            # Reset variables para la próxima convocatoria
            titulo, apertura, cierre, link, alcance, objetivo = None, None, None, None, None, None

    # Convertir a DataFrame
    df = pd.DataFrame(convocatorias)

    # Mostrar
    print(df)

# @shared_task
# def tp1(queue='celery'):
#     time.sleep(3)
#     return

# @shared_task
# def tp2(queue='celery:1'):
#     time.sleep(3)
#     return

# @shared_task
# def tp3(queue='celery:2'):
#     time.sleep(3)
#     return

# @shared_task
# def tp4(queue='celery:3'):
#     time.sleep(3)
#     return
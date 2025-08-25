FROM continuumio/miniconda3:4.10.3

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instalar TA-Lib y XGBoost desde conda
RUN conda install -c conda-forge ta-lib
RUN conda install -c conda-forge xgboost

# Copiar archivos al contenedor
COPY . /usr/src/app/
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh
COPY ./requirements.txt /usr/src/app/requirements.txt

# Establecer el directorio de trabajo
WORKDIR /usr/src/app

# Dar permisos de ejecución al entrypoint
RUN chmod +x /usr/src/app/entrypoint.sh

# Instalar dependencias
RUN pip install -r requirements.txt
RUN conda install -c conda-forge celery=5.2.7 kombu=5.2.4 vine=5.0.0 -y

# Comando por defecto
#CMD ["/usr/src/app/entrypoint.sh"]

FROM continuumio/miniconda3:4.10.3

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instalar pip explícitamente
RUN conda install -y pip

# Dependencias nativas con conda
RUN conda install -c conda-forge ta-lib -y
RUN conda install -c conda-forge xgboost -y

# Celery stack SOLO con conda
RUN conda install -c conda-forge celery=5.2.7 kombu=5.2.4 vine=5.0.0 -y

# Copiar archivos
COPY . /usr/src/app/
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh
COPY ./requirements.txt /usr/src/app/requirements.txt

WORKDIR /usr/src/app
RUN chmod +x /usr/src/app/entrypoint.sh

# Pip SIEMPRE al final
RUN pip install --upgrade pip setuptools wheel
RUN pip install --prefer-binary -r requirements.txt

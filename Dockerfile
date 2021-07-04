# Python-Basisimage
FROM python:3.8.8

# Bash-Shell nutzen
SHELL ["/bin/bash", "-c"]

RUN mkdir /usr/local/Challenge-BE-Revenue-App-main
WORKDIR /usr/local/Challenge-BE-Revenue-App-main
COPY . .

# Umgebungsvariablen
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# virtuelle Umgebung erstellen
ENV VIRTUAL_ENV=/usr/local/flask_env
RUN python3.8 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Installation der erforderlichen Python-Pakete
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python","application"]
# Establecer la imagen base
FROM python:3.9

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el archivo de requisitos al contenedor
COPY requirements.txt .

# Instalar los requisitos
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install
# Copiar el código fuente al contenedor
COPY . .

EXPOSE 5000

# Establecer el punto de entrada
# ENTRYPOINT ["flask", "--app", "server", "run"]
CMD ["flask", "run", "--host=0.0.0.0"]

# Usar una imagen base con Python
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar los archivos de la aplicación
COPY . .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto donde corre Flask
EXPOSE 5000

# Variable de entorno para que Flask se ejecute correctamente
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Instala Flask explícitamente y usa gunicorn para producción
RUN pip install flask gunicorn

# Comando para iniciar la aplicación
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]



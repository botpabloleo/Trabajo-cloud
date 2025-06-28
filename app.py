from flask import Flask, render_template, request
import boto3
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
app = Flask(__name__)

# Conexión a S3
s3 = boto3.client('s3',
    region_name=os.getenv("S3_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

# Conexión a RDS
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS archivos (id SERIAL PRIMARY KEY, nombre TEXT, fecha TIMESTAMP)")
conn.commit()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        archivo = request.files["archivo"]
        nombre = archivo.filename

        # Subir a S3
        s3.upload_fileobj(archivo, os.getenv("S3_BUCKET"), nombre)

        # Guardar en RDS
        cur.execute("INSERT INTO archivos (nombre, fecha) VALUES (%s, %s)", (nombre, datetime.now()))
        conn.commit()

        return "Archivo subido correctamente"

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)

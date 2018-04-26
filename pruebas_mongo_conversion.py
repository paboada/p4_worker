import boto3
import botocore
import os
import pydub
import glob
import shutil
import smtplib
import time
from pymongo import MongoClient
import pprint


######################################################################################################
db_mongo=os.environ["USER_DB_MONGO"]
try:
    client = MongoClient(db_mongo) #La direccion ip publica del servidor ec2 IPv4 Public IP
except:
    print("Fallo conexion")

print("************************************************************************************")
print("Prueba conexion a Mongo AWS")
print("************************************************************************************")
db = client.concursos
doc = db.WebConcursos_audiolocutor.count()
print(doc)
users = db.auth_user.count()
print(users)
#documento_buscado = db.WebConcursos_audiolocutor.find({"id" : 27 })
#print(documento_buscado)
#db.WebConcursos_audiolocutor.update({ "id": 27}, { "$set": { "archivo_convertido": "Prueba.mp3" , "estado": "Convertido" } })
# Create SQS client
######################################################################################################


######################################################################################################
print("************************************************************************************")
print("Prueba conexion a cola en AWS")
print("************************************************************************************")
access_id=os.environ["S3_AWS_ACCESS_KEY_ID"]
access_secret=os.environ["S3_AWS_SECRET_ACCESS_KEY"]
region=os.environ["AWS_DEFAULT_REGION"]
sqs = boto3.resource('sqs', aws_access_key_id=access_id, region_name=region, aws_secret_access_key=access_secret)
#sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName='sqs_concursos')
url_queue=queue.url
print(url_queue)
######################################################################################################


######################################################################################################
print("************************************************************************************")
print("Prueba descarga de archivo desde S3")
print("************************************************************************************")
path_media = '/app/'
archivo_descarga = "doublebassSustentacion.wav"
s3 = boto3.resource('s3', aws_access_key_id=access_id, aws_secret_access_key=access_secret)
bucket = s3.Bucket('media-supervoices')
nombre_bucket = 'media-supervoices'
Prefijo = 'media/' + archivo_descarga
print ("Prefijo: ", Prefijo)
for bucket in s3.buckets.all():
    for obj in bucket.objects.filter(Prefix=Prefijo):
        print("Descargando archivo desde: ", obj.key)
        #print(format(obj.key))
        try:
            s3.Bucket(nombre_bucket).download_file(obj.key, archivo_descarga)
            print("Archivo descargado")
        except:
            print("Ocurrio un error en la DESCARGA del archivo")
######################################################################################################
print("************************************************************************************")
print("Prueba conversion ")
print("************************************************************************************")
archivo_descarga = "doublebassSustentacion.wav"
msplit = archivo_descarga.split(".")
if msplit[1]=='wav':
    print("Convirtiendo de WAV a MP3..........")
    try:
        mp3_file = msplit[0] + '.mp3'
        wav_file = path_media + archivo_descarga
        print("wav_file: ", wav_file, "sound = pydub.AudioSegment.from_wav(wav_file)")
        sound = pydub.AudioSegment.from_wav(wav_file)
        mp3_file = path_media + mp3_file
        print("mp3_file: ", mp3_file, "sound.export(mp3_file, format= mp3")
        sound.export(mp3_file, format= "mp3")
        print("Termino conversion.........")
        #os.remove(wav_file)
        #pref_bucket = 'media/' + mp3_file
        #print("Guardando archivo: ", mp3_file, " en S3" )
        #s3_cliente.upload_file(mp3_file, nombre_bucket, pref_bucket)
        #os.remove(mp3_file)
        #message.delete()
        ok=1
    except:
        print("Ocurrio un error en la CONVERSION del archivo")
        print("No se elimina el mensaje de la cola")
        ok=0

print("************************************************************************************")
print("Este es un script para probar conexion a Mongo y a SQS en AWS")
print("************************************************************************************")

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

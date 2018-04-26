print("****************************************************************************************************************************")
print("Este es el script produccion para descargar archivo, convertirlo, guardar el mp3 en S3, cambiar estado en base de datos,etc")
print("****************************************************************************************************************************")

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

print("Inicio de la Ejecucion de batchMP3.py adaptado para sqs")
print(time.strftime("%d/%m/%y %H:%M:%S"))

email_host=os.environ["SES_EMAIL_HOST"]
email_port=os.environ["SES_EMAIL_PORT"]
email_user=os.environ["SES_EMAIL_HOST_USER"]
email_pass=os.environ["SES_EMAIL_HOST_PASSWORD"]
db_mongo=os.environ["USER_DB_MONGO"]

path_media = '/app/'
#path_procesados = '/home/ec2-user/Proyecto_3_D/procesados/'


# Create SQS client
print("Inicia revision de mensajes en la cola sqs")
access_id=os.environ["S3_AWS_ACCESS_KEY_ID"]
access_secret=os.environ["S3_AWS_SECRET_ACCESS_KEY"]
sqs = boto3.resource('sqs', aws_access_key_id=access_id, aws_secret_access_key=access_secret)
queue = sqs.get_queue_by_name(QueueName='sqs_concursos')
url_queue=queue.url
print("Conectado a la url: ", url_queue)


#Create S3 client
access_id=os.environ["S3_AWS_ACCESS_KEY_ID"]
access_secret=os.environ["S3_AWS_SECRET_ACCESS_KEY"]
s3_cliente = boto3.client('s3', aws_access_key_id=access_id, aws_secret_access_key=access_secret)
s3 = boto3.resource('s3', aws_access_key_id=access_id, aws_secret_access_key=access_secret)
bucket = s3.Bucket('media-supervoices')
nombre_bucket = 'media-supervoices'

cont = 0
#while True:
while cont<100000:
    print("secuencia:", cont)
    messages = queue.receive_messages(QueueUrl=url_queue, AttributeNames=['All'], MessageAttributeNames=['All'], MaxNumberOfMessages=10) # adjust MaxNumberOfMessages if needed
    print("Mensajes encontrados: " , len(messages))
    for message in messages: # 'Messages' is a list
    # process the messages
        print("************************************************************************************")
        print("Mensaje encontrando en SQS del archivo: ", (message.message_attributes['archivo_original']['StringValue']))
        archivo_descarga = message.message_attributes['archivo_original']['StringValue']
        id_audio_cambiar = message.message_attributes['id_audio']['StringValue']
        print("Buscando archivo ", archivo_descarga, " en S3........." )
        try:
            s3.meta.client.head_bucket(Bucket=nombre_bucket)
        except botocore.exceptions.ClientError as e:
            error_code = int(e.response['Error']['Code'])
            print(error_code)
        Prefijo = 'media/' + archivo_descarga
        print ("Prefijo: ", Prefijo)
        for bucket in s3.buckets.all():
            for obj in bucket.objects.filter(Prefix=Prefijo):
                print("Descargando archivo desde: ", obj.key)
                #print(format(obj.key))
                try:
                    s3.Bucket(nombre_bucket).download_file(obj.key, archivo_descarga)
                except:
                    print("Ocurrio un error en la DESCARGA del archivo")

                msplit = archivo_descarga.split(".")
                if msplit[1]=='wav':
                    print("Convirtiendo de WAV a MP3..........")
                    try:
                        mp3_file = msplit[0] + '.mp3'
                        wav_file = path_media + archivo_descarga
                        print("wav_file: ", wav_file)
                        sound = pydub.AudioSegment.from_wav(wav_file)
                        mp3_file_path = path_media + mp3_file
                        print("mp3_file: ", mp3_file_path)
                        sound.export(mp3_file_path, format= "mp3")
                        print("Termino conversion.........")
                        os.remove(wav_file)
                        print("Guardando archivo: ", mp3_file, " en S3" )
                        pref_bucket = 'media/' + mp3_file
                        s3_cliente.upload_file(mp3_file, nombre_bucket, pref_bucket)
                        os.remove(mp3_file)
                        message.delete()
                        ok=1
                    except:
                        print("Ocurrio un error en la CONVERSION del archivo")
                        print("No se elimina el mensaje de la cola")
                        ok=0
                        try:
                            os.remove(wav_file)
                            os.remove(mp3_file)
                        except:
                            print("No hay archivos para borrar en el worker")
                else:
                    print("Convirtiendo de OGG a MP3..........")
                    try:
                        msplit[1]=='ogg'
                        mp3_file = msplit[0] + '.mp3'
                        ogg_file = path_media+archivo_descarga
                        sound = pydub.AudioSegment.from_ogg(ogg_file)
                        sound.export(mp3_file, format= "mp3")
                        os.remove(ogg_file)
                        pref_bucket = 'media/' + mp3_file
                        print("Guardando archivo: ", mp3_file, " en S3" )
                        s3_cliente.upload_file(mp3_file, nombre_bucket, pref_bucket)
                        os.remove(mp3_file)
                        message.delete()
                        ok=1
                    except:
                        print("Ocurrio un error en la CONVERSION del archivo")
                        print("No se elimina el mensaje de la cola")
                        ok=0
                        try:
                            os.remove(wav_file)
                            os.remove(mp3_file)
                        except:
                            print("No hay archivos para borrar en el worker")
        if ok == 1:
            print("Inicia proceso en MongoDB.............")
            client = MongoClient(db_mongo) #La direccion ip publica del servidor ec2 IPv4 Public IP
            db = client.concursos
            print("ID audio a buscar en Mongo:", message.message_attributes['id_audio']['StringValue'])
            cursor = db.WebConcursos_audiolocutor.find({"id" : int(id_audio_cambiar) })
            for doc in cursor:
                print("Imprimiento cursor")
                print("Documento Mongo encontrado para : ",  doc["archivo_original"])
                db.WebConcursos_audiolocutor.find_one_and_update({ "id": int(id_audio_cambiar) }, { "$set": { "archivo_convertido": mp3_file , "estado": "Convertido" }})
            print("Inicia el envio de correo de notificacion..........")
            cursor = db.WebConcursos_audiolocutor.find({"id": int(id_audio_cambiar) },{"email":1, "_id":0})
            for doc in cursor:
                print("Se enviara correo a: ")
                print(doc["email"])
                smtp = smtplib.SMTP(email_host, email_port)
                remitente = 'supervoices.cloud@gmail.com'
                destinatario = doc["email"]
                asunto = "Aviso de procesamiento de audio"
                encabezado = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (remitente, destinatario,asunto)
                email = encabezado + "Hola! Te informamos que tu archivo de audio " + mp3_file + " a sido procesado con exito! "
                smtp.starttls()
                smtp.ehlo()
                try:
                    smtp.login(email_user, email_pass)
                    print("Enviando correo............")
                    smtp.sendmail(remitente, destinatario, email)
                    smtp.close()
                    print("Finalizado............")
                except smtplib.SMTPAuthenticationError as e:
                    print(e.SMTPAuthenticationError)
        else:
            print("No se cambia estado en base de datos ni se envia correo")
        print("************************************************************************************")
    cont=cont+1
    time.sleep(5)

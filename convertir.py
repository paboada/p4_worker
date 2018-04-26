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

path_media = '/app/'
archivo_descarga = "doublebassSustentacion.wav"

print("************************************************************************************")
print("Prueba conversion convertir.py")
print("************************************************************************************")
archivo_descarga = "doublebassSustentacion.wav"
msplit = archivo_descarga.split(".")
if msplit[1]=='wav':
    print("Convirtiendo de WAV a MP3..........")
    try:
        mp3_file = msplit[0] + '.mp3'
        wav_file = path_media + archivo_descarga
        print("wav_file: ", wav_file)
        sound = pydub.AudioSegment.from_wav(wav_file)
        mp3_file = path_media + mp3_file
        print("mp3_file: ", mp3_file)
        sound.export(mp3_file, format= "mp3")
        print("Termino conversion.........")
        print("Guardando archivo: ", mp3_file, " en S3" )
        s3_cliente.upload_file(mp3_file, nombre_bucket, pref_bucket)
        ok=1
    except:
        print("Ocurrio un error en la CONVERSION del archivo")
        print("No se elimina el mensaje de la cola")
        ok=0

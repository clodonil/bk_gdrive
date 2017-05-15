# coding=UTF-8

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

class gdrive():
   def __init__(self):
       #conectando no google
       gauth = GoogleAuth()
       gauth.LoadCredentialsFile("mycreds.txt")
       
       if gauth.credentials is None:
          # Authenticate if they're not there
          gauth.LocalWebserverAuth()
       elif gauth.access_token_expired:
          # Refresh them if expired
          gauth.Refresh()
       else:
          # Initialize the saved creds
          gauth.Authorize()
       # Save the current credentials to a file
       gauth.SaveCredentialsFile("mycreds.txt")

       drive = GoogleDrive(gauth)

#textfile = drive.CreateFile()
#textfile.SetContentFile('eng.txt')
#textfile.Upload()
#print textfile

#drive.CreateFile({'id':textfile['id']}).GetContentFile('eng-dl.txt')


   def upload(filename):
       pass



   def download(filename):
       pass

   def list():
       pass

   def delete(filename):
       pass


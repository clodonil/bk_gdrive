# coding=UTF-8
from __future__ import print_function
import httplib2
import os
import datetime
from apiclient import discovery
from apiclient.http import MediaFileUpload
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.service_account import ServiceAccountCredentials
import subprocess
import logging
import glob
import tarfile
import yaml
import sys
import os


class Backup_Magento():
    def __init__(self):
        '''
             Carga dos arquivos de configurcao
        '''
        try:
          with open('config.yaml', 'r') as f:
               self.params = yaml.load(f)
        except:
               print('Erro no arquivo de configuracao (config.yaml)')
               sys.exit(1)

        # criando os diretorios
        self.checkdir()


        #logs
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # create a file handler
        handler = logging.FileHandler(self.params['admin']['log'])
        handler.setLevel(logging.INFO)

        # create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # add the handlers to the logger
        self.logger.addHandler(handler)


        self.log('backup Inicializado')


    def checkdir(self):
        '''
          Verifica se o diretorios basicos existem
        '''
        dirs = []
        dirs.append(self.params['admin']['log'].split("/")[0])
        dirs.append(self.params['backup']['storage'])
        for dir in dirs:
            if not os.path.exists(dir):
               os.makedirs(dir)

        if not os.path.exists(self.params['admin']['secret_google']):
            print("Arquivo do json do google não encontrado.")
            sys.exit(1)

    def backup_mysql(self):
        '''
          Backup do banco do mysql
        '''
        data     = datetime.datetime.now().strftime("%d-%m-%Y")
        filename = self.params['backup']['storage'] + 'db_'+self.params['mysql']['database'] +  '.sql'
        dados = {} 
        dados['user'] = self.params['mysql']['user']
        dados['pass'] = self.params['mysql']['passwd']
        dados['host'] = self.params['mysql']['host']
        dados['port'] = self.params['mysql']['port']
        dados['db']   = self.params['mysql']['database']
        dados['output'] = filename
   
        cmd = "mysqldump --user={user} --password={pass} --host={host} --port={port} {db} > {output}".format(**dados)
        if os.system(cmd) != 0:
           self.log('Problema no backup do Mysql')
           return False
        try:
           filename_tar = self.params['backup']['storage'] + 'db_'+self.params['mysql']['database']+"-" + data + '.tar.gz'
           tar = tarfile.open(filename_tar, "w:gz")
           tar.add(filename)
           tar.close()
           return filename_tar
        except:
           self.log('Problema com a compactacao do backup do Mysql')
           return False

    def backup_magento(self):
        '''
          Backup da pasta do magento, considerando que esta na maquina local
        '''
        data     = datetime.datetime.now().strftime("%d-%m-%Y")
        filename = self.params['backup']['storage'] + 'sys_magento-' +  data + '.tar.gz'
        path     = self.params['magento']['path']
        try:
           tar = tarfile.open(filename, "w:gz")
           tar.add(path)
           tar.close()
           return filename
        except:
           self.log('Erro ao realizar a compactacao do magento')
           return False

    def delete_file(self,service,f_id,filename):
        '''
          Deleta os arquivos localmente e remotamente
        '''
        try:
           service.files().delete(fileId=f_id).execute()
           os.remove(self.params['backup']['storage']+filename)
        except:
           self.log("Erro ao apagar arquivos")
           return False

        self.log("Arquivo deletado: {0}".format(filename))
        return True

    def gdrive_connect(self):
        '''
          Conecta no servico do google drive
        '''
        KEY_FILE_NAME = self.params['admin']['secret_google']
        SCOPES = 'https://www.googleapis.com/auth/drive'
        try:
           credentials = ServiceAccountCredentials.from_json_keyfile_name(filename=KEY_FILE_NAME, scopes=SCOPES)
           http        = credentials.authorize(httplib2.Http())
           service     = discovery.build(serviceName="drive", version="v3", credentials=credentials)
           return service
        except:
           self.log('error ao conectar no google')
           return False



    def gdrive_list_file(self,service):
        '''
           Retorna a quantidade de arquivos no google
           sendo o primeiro do mysql e segundo do magento
        '''
        query_magento="name contains 'sys_'"
        query_mysql  ="name contains 'db_'"

        tmp = service.files().list(q=query_magento, orderBy='name',fields="files(id, name)").execute()
        files_magento = tmp.get('files', [])

        tmp = service.files().list(q=query_mysql, orderBy='name',fields="files(id, name)").execute()
        files_mysql = tmp.get('files', [])


        n_files_magento  = len(files_magento) 
        n_files_mysql    = len(files_mysql)
        files = [n_files_magento, n_files_mysql,files_magento,files_mysql]

        return files

    def coletor_lixo(self):
        '''
           Limpa os arquivos temporarios, limpa os arquivo excedentes
        '''
        if self.params['backup']['storage_local'] == False:
           for f_file in glob.glob(self.params['backup']['storage']+"*"):
               try:
                  os.remove(f_file)
               except:
                  self.log('Erro ao apagar arquivos temporarios')


        # Verificando se o numero maximo de arquivo foi criado
        self.check_limit_file()


        # Deletando arquivos temporarios  
        try:
           os.remove(self.params['backup']['storage']+"*.sql")
        except:
           self.log('Erro ao apagar arquivos tmp *.sql')

        self.log('backup Finalizado')
    def check_limit_file(self):
        '''
            Verifica o numero máximo de arquivos armazenado
        '''
        max_file_magento = self.params['backup']['magento_rotation']
        max_file_mysql   = self.params['backup']['mysql_rotation']


        service = self.gdrive_connect()

        (gdrive_magfile,gdrive_myfile,f_magento,f_mysql) = self.gdrive_list_file(service)
        
        # Verifica a quant de arquivos mysql
        if gdrive_myfile > max_file_mysql:
           gfile = f_mysql[0] 
           #deletando arquivo gdrive
           self.delete_file(service, gfile['id'],gfile['name'])
           self.log("apagando o arquivo {0} no gdrive".format(gfile['name']))
           # Apagando o arquivo local
           try:
              os.remove(self.params['backup']['storage'] + gfile['name'])
           except:
             self.log("erro ao apagar arquivo: {0}".format(gfile['name']))

        #Verifica a quant de arquivos magent
        if gdrive_magfile > max_file_magento:
           gfile = f_magento[0]
           #deletando arquivo gdrive
           self.delete_file(service, gfile['id'],gfile['name'])
           # Apagando o arquivo local
           try:
              os.remove(self.params['backup']['storage'] + gfile['name'])
           except:
              self.log("erro ao apagar arquivo: {0}".format(gfile['name']))

        return True


    def create_dir(self,service,  name):
        '''
           Cria o diretorio para os arquivos
        '''
        folder_metadata = {
           'name' : name,
           'mimeType' : 'application/vnd.google-apps.folder'
        }

        # Pesquisando se a pasta ja existe
        folder_query = "name contains '%s' and mimeType = '%s'" % (name,"application/vnd.google-apps.folder")
        folder_list  = service.files().list(q=folder_query).execute()
        folder_ret   = folder_list.get('files',[])
      
        if len(folder_ret) > 0 :
           folder_id = folder_ret[0]['id']
           return folder_id
        else:
           self.log('Criando pasta')
           folder = service.files().create(body=folder_metadata, fields='id, name').execute()
           folderID = folder.get('id')
           self.compartilhar(service,folderID)
           return folderID




    def compartilhar(self,service, fileID):
        '''
           compartilhar o arquivo enviado
        '''
        email = self.params['admin']['email']
        batch = service.new_batch_http_request(callback=callback)
        user_permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': email
        }
        batch.add(service.permissions().create(
             fileId=fileID,
             body=user_permission,
             fields='id',
        ))
        batch.execute()


    def upload(self,filename):
        '''
          Upload dos arquivos para o gdrive
        '''
        dir = self.params['admin']['gdrive_dir']    

        service = self.gdrive_connect()
        folder_dir  = self.create_dir(service,dir)

        arq = filename.split("/")[-1]

        file_metadata = {
             'name' : arq,
             'parents': [ folder_dir ]
        }
        media = MediaFileUpload(filename, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='name,id').execute()
        fileID = file.get('id')
#        self.compartilhar(service,fileID)

        return True



    def log(self,msg):
        self.logger.info(msg)



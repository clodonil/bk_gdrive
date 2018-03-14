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
from libs.AppException import *
import subprocess
import logging
import glob
import tarfile
import yaml
import sys
import os


class Backup_App():
    def __init__(self,path):
        '''
             Carga dos arquivos de configurcao
        '''
        filename=path
        try:
          with open(filename, 'r') as f:
             self.params = yaml.load(f)
        except:
               raise ErroObtendoDados(msg="Problema para abrir o arquivo de configuracao: {tipo}", tipo="config.yaml")

        # criando os diretorios
        self.checkdir()


        #logs
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # create a file handler
        handler = logging.FileHandler(self.params['admin']['logFile'])
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
        dirs.append(self.params['backup']['storage'])

        for dir in dirs:
            if not os.path.exists(dir):
               try:
                  os.makedirs(dir)
               except:
                   raise ErroAoProcessar(msg="Erro ao criar o diretório {0}".format(dir))


    def backup_mysql(self):
        '''
          Backup do banco 
        '''
        data     = datetime.datetime.now().strftime("%d-%m-%Y")
        filename = self.params['backup']['storage'] + 'db_'+self.params['db']['database'] +  '.sql'
        dados = {} 
        dados['user'] = self.params['db']['user']
        dados['pass'] = self.params['db']['passwd']
        dados['host'] = self.params['db']['host']
        dados['port'] = self.params['db']['port']
        dados['db']   = self.params['db']['database']
        dados['output'] = filename
   
        cmd = "mysqldump --user={user} --password={pass} --host={host} --port={port} {db} > {output}".format(**dados)
        if os.system(cmd) != 0:
           self.log('Problema no backup do Mysql')
           return False
        try:
           filename_tar = self.params['backup']['storage'] + 'db_'+self.params['db']['database']+"-" + data + '.tar.gz'
           tar = tarfile.open(filename_tar, "w:gz")
           tar.add(filename)
           tar.close()
           return filename_tar
        except:
           self.log('Problema com a compactacao do backup do Mysql')
           raise ErroAoProcessar(msg="Erro ao compactar arquido do banco de dados")

    def backup_app(self):
        '''
          Backup da pasta do magento, considerando que esta na maquina local
        '''
        data          = datetime.datetime.now().strftime("%d-%m-%Y")
        filename      = self.params['backup']['storage'] + 'sys_' + self.params['app']['name'] +'-'+  data + '.tar.gz'
        path          = self.params['app']['path']
        exclude_files = self.params['app']['path_exclude']

        try:
           tar = tarfile.open(filename, "w:gz")
           tar.add(path,filter=exclude_files)
           tar.close()
           return filename
        except:
           self.log('Erro ao realizar a compactacao do app')
           raise ErroAoProcessar(msg="Erro ao compactar arquivo de aplicacao")

    def exclude_files(self,tarinfo):
        '''
          Verificar se o arquivo da aplicacao nao vai ser incluido no tar
        '''
        path_exclude =  self.params['app']['path_exclude'].split(',')

        retorno  = tarinfo
        filename = tarinfo.name

        for path in path_exclude:
            normalize     = path.replace('/','')
            temp          = filename.replace('/','').replace(normalize,'')
            file_limpo    = filename.replace('/','').replace(temp,'')


            if normalize == file_limpo:
               retorno = None

        return retorno


    def delete_file(self,service,f_id,filename):
        '''
          Deleta os arquivos localmente e remotamente
        '''
        try:
           service.files().delete(fileId=f_id).execute()
           os.remove(self.params['backup']['storage']+filename)
        except:
            self.log("Limpando arquivos Temp")
            raise ErroAoProcessar(msg="Erro ao limpar arquivos Temp")
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
           raise ErroAoComunicarComServidor(msg="Erro ao comunicar com o google Api")
           self.log('error ao conectar no google, verifique o arquivo de chave e as permissao do google')

    def lista(self):
        ''' 
           lista a quantidade de arquivos e os arquivos armazenados
        '''
        service = self.gdrive_connect() 
        #service.messages.send(
        #message = (service.messages().send(self.params['admin']['email_shared'], body='Lista de arquivos de backup').execute())
        #try:
        status = open(self.params['admin']['listaFile'],'w')
        (gdrive_magfile,gdrive_myfile,files_app,files_db) = self.gdrive_list_file(service)
        status.write("{0}\n".format("-"*100))
        status.write("\tLISTA DE ARQUIVOS DE BACKUP\n")
        status.write("{0}\n".format("-"*100))
        for files in files_app:
            status.write("\t{0}\n".format(files['name']))

        for files in files_db:
            status.write("\t{0}\n".format(files['name']))
        status.write("{0}\n".format("-"*100))
        self.log("Lista de arquivos criado: {0}".format(self.params['admin']['listaFile']))
        #except:
        #    raise ErroObtendoDados(msg="Impossivel obter a lista de arquivos do gdrive")
        #    self.log("Erro ao criar lista de arquivos")

    def gdrive_list_file(self,service):
        '''
           Retorna a quantidade de arquivos no google
           sendo o primeiro do mysql e segundo do magento
        '''
        query_app    ="name contains 'sys_'"
        query_db     ="name contains 'db_'"

        tmp       = service.files().list(q=query_app, orderBy='name',fields="files(id, name)").execute()
        files_app = tmp.get('files', [])

        tmp      = service.files().list(q=query_db, orderBy='name',fields="files(id, name)").execute()
        files_db = tmp.get('files', [])


        n_files_app      = len(files_app) 
        n_files_db       = len(files_db)
        files = [n_files_app, n_files_db,files_app,files_db]

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
                  raise ErroAoProcessar(msg="Impossivel apagar o arquivo temporario {0}".format(f_file))


        # Verificando se o numero maximo de arquivo foi criado
        self.check_limit_file()


        # Deletando arquivos temporarios  
        for lixo in glob.glob(self.params['backup']['storage']+"*.sql"):
            try:
               os.remove(lixo)
            except:
               self.log('Erro ao apagar arquivos tmp *.sql')

        self.log('backup Finalizado')

    def check_limit_file(self):
        '''
            Verifica o numero máximo de arquivos armazenado
        '''
        max_file_app     = self.params['backup']['app_rotation']
        max_file_db      = self.params['backup']['db_rotation']


        service = self.gdrive_connect()

        # Verifica se conectou no google
        if service:
           try:
                (gdrive_magfile,gdrive_myfile,file_app,file_db) = self.gdrive_list_file(service)
           except:
                raise ErroAoComunicarComServidor(msg="Erro ao comunicar com o servidor do Google")

        
           # Verifica a quant de arquivos mysql
           if gdrive_myfile > max_file_db:
              gfile = file_db[0] 
              #deletando arquivo gdrive
              self.delete_file(service, gfile['id'],gfile['name'])
              self.log("apagando o arquivo {0} no gdrive".format(gfile['name']))
              # Apagando o arquivo local
              try:
                 filename=self.params['backup']['storage'] + gfile['name']
                 os.remove(filename)
              except:
                 self.log("erro ao apagar arquivo: {0}".format(filename))

           #Verifica a quant de arquivos magent
           if gdrive_magfile > max_file_app:
              gfile = file_app[0]
              #deletando arquivo gdrive
              self.delete_file(service, gfile['id'],gfile['name'])
              # Apagando o arquivo local
              try:
                filename=self.params['backup']['storage'] + gfile['name']
                os.remove(filename)
              except:
                self.log("erro ao apagar arquivo: {0}".format(filename))

           return True
        else:
           return False


    def create_dir(self,service,  name):
        '''
           Cria o diretorio para os arquivos
        '''
        self.log("Check da pasta pasta {0}".format(name))

        folder_metadata = {
           'name' : name,
           'mimeType' : 'application/vnd.google-apps.folder'
        }

        try:
           # Pesquisando se a pasta ja existe
           folder_query = "name contains '%s' and mimeType = '%s'" % (name,"application/vnd.google-apps.folder")
           folder_list  = service.files().list(q=folder_query).execute()
           folder_ret   = folder_list.get('files',[])
      
           if len(folder_ret) > 0 :
              folderID = folder_ret[0]['id']
           else:
               self.log('Criando pasta')
               folder = service.files().create(body=folder_metadata, fields='id, name').execute()
               folderID = folder.get('id')
               self.compartilhar(service,folderID)
           return folderID
        except:
            self.log("Erro ao criar pasta")
            return False



    def compartilhar(self,service, fileID):
        '''
           compartilhar o arquivo enviado
        '''
        self.log("Compartilhando arquivo {0}".format(fileID))
        email = self.params['admin']['email_shared']
        #try:
        batch = service.new_batch_http_request(callback=self.callback)
            #batch = service.new_batch_http_request()
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
        #except:
        #    self.log("Erro ao compartilhar o arquivo")

    def callback(self,request_id, response, exception):
        if exception:
           # Handle error
           self.log(exception)
        else:
            self.log("Permissao Id: %s" % response.get('id'))


    def upload(self,filename):
        '''
          Upload dos arquivos para o gdrive
        '''
        self.log("Upload do arquivo {0}".format(filename))
        dir = self.params['admin']['gdrive_dir']    
        try:
           service = self.gdrive_connect()
           folder_dir  = self.create_dir(service,dir)

           if folder_dir != False:

                arq = filename.split("/")[-1]

                file_metadata = {
                      'name' : arq,
                      'parents': [ folder_dir ]
                }
                media = MediaFileUpload(filename, resumable=True)
                file = service.files().create(body=file_metadata, media_body=media, fields='name,id').execute()
                fileID = file.get('id')
                #self.compartilhar(service,fileID)
                return True
        except:
            self.log("Problema no upload do arquivo")
        return False



    def log(self,msg):
        self.logger.info(msg)



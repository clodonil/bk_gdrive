import sys
from libs.BkApp import Backup_App
from libs.AppException import *
import argparse

'''
   Programa principal
'''


# Carga de parametros
def params():
    parser = argparse.ArgumentParser(description = 'Script de Backup do Magento no GDrive.')
    parser.add_argument('--app', action='store_true', dest = 'app',
                                                   default = False, required = False,
                                                   help = 'Coloque essa opcao para fazer backup da aplicacao.')

    parser.add_argument('--db', action='store_true', dest = 'db',
                                                   default = False, required = False,
                                                   help = 'Coloque essa opcao para fazer backup do Banco de Dados.')

    parser.add_argument('--lista', action='store_true', dest = 'lista',
                                                   default = False, required = False,
                                                   help = 'Lista os arquivos armazenados.')

    parser.add_argument('--config', dest = 'config',
                                                   default = '/etc/bk_gdrive/config.yaml', required = False,
                                                   help = 'path do caminho de configuracao (config.yaml).')



    args = parser.parse_args()

    # Verificar se um parametro pelo menos foi passado
    if not args.lista and not args.app and not args.db:
       parser.print_help()
       sys.exit(1)

    return args    

def main(args):
    '''
       Modulo principal
    '''
    local    = Backup_App(args.config)

    # lista todos os arquivos
    if args.lista:
        #listando todos os arquivos
        local.lista()

    else:
       # Verifica se chegou no numero limite de arquivos para backup
       if not local.check_limit_file():
          local.log('Espaco para backup indefinido...')
          return False

       # Backup dos arquivos
       if args.db:
           db_file   = local.backup_mysql()
           # upload dos novos backups
           if db_file:
              local.upload(db_file)

       if args.app:
           filebackup = local.backup_app()
           #upload dos novos backups
           if filebackup:
              local.upload(filebackup)

       # limpa os arquivos de cache e tmps
       local.coletor_lixo()

       #Gera a lista de arquivos
       local.lista()
    return True

if __name__ == "__main__":
    args=params()

    try:
      main(args)
    except AppException as e:
         print(e.msg)
         exit(e.code)
    exit(0)

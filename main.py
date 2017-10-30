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
    parser.add_argument('--magento', action='store_true', dest = 'magento',
                                                   default = False, required = False,
                                                   help = 'Coloque essa opcao para fazer backup do magento.')

    parser.add_argument('--mysql', action='store_true', dest = 'mysql',
                                                   default = False, required = False,
                                                   help = 'Coloque essa opcao para fazer backup do Mysql.')

    parser.add_argument('--lista', action='store_true', dest = 'lista',
                                                   default = False, required = False,
                                                   help = 'Lista os arquivos armazenados.')

    parser.add_argument('--config', dest = 'config',
                                                   default = '/etc/bk_magento_gdrive/', required = False,
                                                   help = 'path do caminho de configuracao.')



    args = parser.parse_args()

    # Verificar se um parametro pelo menos foi passado
    if not args.lista and not args.magento and not args.mysql:
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
       if args.mysql:
           mysql_file   = local.backup_mysql()
           # upload dos novos backups
           if mysql_file:
              local.upload(mysql_file)

       if args.magento:
           magento_file = local.backup_magento()
           #upload dos novos backups
           if not magento_file:
              local.upload(magento_file)

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

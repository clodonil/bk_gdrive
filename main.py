import sys
from libs.bkmagento import Backup_Magento

'''
   Programa principal
'''


params=[]

for opcao in sys.argv:
    params.append(opcao)

local    = Backup_Magento()

# Verifica se chegou no numero limite de arquivos para backup
if not local.check_limit_file():
    print('Espaco para backup indefinido...')
    sys.exit(1)

if len(params) == 1  or "mysql" in params:
    # Backup dos arquivos
    mysql_file   = local.backup_mysql()
    # upload dos novos backups
    if mysql_file != False:
       local.upload(mysql_file)

if len(params) == 1  or "magento" in params:
   magento_file = local.backup_magento()
   if magento_file != False:
      local.upload(magento_file)

# limpa os arquivos de cache e tmps
local.coletor_lixo()

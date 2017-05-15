import sys
from libs.bkmagento import Backup_Magento

'''
   Programa principal
'''

local    = Backup_Magento()

# Verifica se chegou no numero limite de arquivos para backup
if not local.check_limit_file():
    print('Espaco para backup indefinido...')
    sys.exit(1)

# Backup dos arquivos
mysql_file   = local.backup_mysql()
# upload dos novos backups
if mysql_file != False:
   local.upload(mysql_file)

magento_file = local.backup_magento()
if magento_file != False:
   local.upload(magento_file)

# limpa os arquivos de cache e tmps
local.coletor_lixo()

# Backup do Magento em Google Drive

Esse script foi escrito para resolver um problema pessoal de backup automatizado no google Driver. Fique a vontade para reportar problemas ou melhorá-lo.

Basicamente o script faz a compactação dos arquivos de banco de dados e do sistema e envia para o gdrive. Também existe a possibilidade de manter o backup local. 

O script controla/rotaciona a quantidade de arquivos de backup.

[![Screen Shot](http://www.devops-sys.com.br/screenshot/bkmagento1.jpg)](http://www.devops-sys.com.br/screenshot/bkmagento1.jpg)

## Instalação
A instalação do script é bastante simples. Primeiramente clone o projeto do github:

```bash
$ git clone https://github.com/clodonil/bk_magento_gdrive/
```
Entre no diretório criado e instale as dependências:
```bash
$ cd bk_magento_gdrive/
$ pip install -r requirements
```

## Criar a conta de Serviço do Google

É necessário criar uma conta de serviço no google para permitir autenticação do script e fazer o upload dos arquivos.
Os seguintes passos vão te ajudar nesse processo:
1. Faça autenticação no [Google API](https://console.developers.google.com/apis/library).
[![Screen Shot](http://www.devops-sys.com.br/screenshot/bkmagento2.jpg)](http://www.devops-sys.com.br/screenshot/bkmagento2.jpg)

2.  Na opção "Credentials" crie um novo projeto e as credenciais;
[![Screen Shot](http://www.devops-sys.com.br/screenshot/bkmagento3.jpg)](http://www.devops-sys.com.br/screenshot/bkmagento3.jpg)
3.  Escolha a opção de "Service Account Key" e faça download do arquivo json.
4.  Habilite o Google Drive Api

[![Screen Shot](http://www.devops-sys.com.br/screenshot/bkmagento4.jpg)](http://www.devops-sys.com.br/screenshot/bkmagento4.jpg)


### config.yaml
Antes de executar o script, ajuste o arquivo de configuração.
```yaml
admin:
   email: email@localhost 
   secret_google: secrets.json
   gdrive_dir: Magento-Backup
   log: logs/backupMagento.log
mysql:
   host: localhost
   user: root
   passwd: magento
   database: magento
   port: 3306
magento:
   path: /var/www/html/
backup:
   mysql_rotation: 10
   magento_rotation: 10
   storage_local: True
   storage: storage/
```
As principais linhas de configuração são:
  * **email**: *E-Mail que vai ter acesso aos arquivos de backup* 
  * **secret_google**: *Nome do arquivo json criado no google Api*
  * **gdrive_dir**: *Nome da pasta criado no google para armazenar os backups*
  * **log**: *log da aplicação*
  * **path**: *Diretório do armazenamento do magento*
  * **mysql_rotation**: *Quantidade de arquivos mantidos de Mysql*
  * **magento_rotation**: *Quantidade de arquivos mantidos de magento*
  * **storage_local**: *True para manter o backup local ou False para manter apenas no google*
  * **storage**: *Diretório para manter os backups locais*


### Crontab
Para o backup ser automatizado adicione as seguintes linhas no crontab
```html
# Backup diário do mysql
0 5  * * *  /opt/bk_magento/main.py --mysql
# Backup semanal do Magento
0 5 1  * * /opt/bk_magento/main.py --magento
# Backup diário do Mysql e Magento
0 5 * * * /opt/bk_magento/main.py --mysql --magento
```
## Licence

Source code can be found on [github](https://github.com/georgeOsdDev/markdown-edit), licenced under [MIT](http://opensource.org/licenses/mit-license.php).

Developed by [clodonil Trigo](http://devops-sys.com.br)


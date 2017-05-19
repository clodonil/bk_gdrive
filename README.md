# Backup do Magento em Google Drive

Esse script foi escrito para resolver um problema pessoal de backup automatizado no google Driver. Fique a vontade para reportar problemas ou melhora-ló

[![Screen Shot](bkmagento1.jpg)](http://www.devops-sys.com.br/screenshot/)

## Instalação
A instalação do script é bastante simples. Primeiramente clone o projeto do github:

```bash
$ git clone https://github.com/clodonil/bk_magento_gdrive/
```
Entre no diretório criado e instale as dependências:
```bash
$ cd bk_magento_gdrive/
$ pip install -f requirements
```

## Criar a conta de Serviço do Google

É necessário criar uma conta de serviço no google para permitir autenticação do script e fazer o upload dos arquivos.
Os seguintes passos vão te ajudar nesse processo:
[![Screen Shot](bkmagento2.jpg)](https://www.devops-sys.com.br/screenshot/)
[![Screen Shot](bkmagento3.jpg)](https://www.devops-sys.com.br/screenshot/)
[![Screen Shot](bkmagento4.jpg)](https://www.devops-sys.com.br/screenshot/bkmagento4.jpg)
* Faça autenticação no [Google API](https://console.developers.google.com/apis/library). 
* Na aba "Credentials", crie um nova Credencial, conforme
Part of Editor is depend on [CodeMirror](http://codemirror.net/).It enabeles

* Display **line number**.
* **Match Brackets** in the document.
* Visible `Tab` key
* **Highlight syntax** of markdown.
* **Drag and Drop** file read.

For more option, see [programming API](http://codemirror.net/doc/manual.html) of CodeMirror, and Hack [Markdown Edit](http://github.com/georgeosddev/markdown-edit)

### config.yaml
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
   ssh_host: localhost
   ssh_user:
   ssh_pass:
   ssh_port:
   path: /var/www/html/
backup:
   mysql_rotation: 10
   magento_rotation: 10
   storage_local: True
   storage: storage/

```


### Crontab
To display converted HTML like Github, Markdown-Edit apply github.css from highlight.js and github-style.css inspired by [gollum](https://github.com/gollum/gollum/blob/master/lib/gollum/public/gollum/css/template.css).

```html
<link rel="stylesheet" href="bower_components/highlightjs/styles/github.css">
<link rel="stylesheet" href="css/github-style.css">
```

If you want to see raw html what [Github's API](http://developer.github.com/v3/markdown/#render-a-markdown-document-in-raw-mode) responsed, click `Raw .html` button on navbar.

## Getting Started

### Install On your local PC

#### Download Sources

use git

```bash
git clone http://github.com/georegeosddev/markdown-edit.git
```

Or download from [Here](https://github.com/georgeOsdDev/markdown-edit/zipball/master)




## Licence

Source code can be found on [github](https://github.com/georgeOsdDev/markdown-edit), licenced under [MIT](http://opensource.org/licenses/mit-license.php).

Developed by [clodonil Trigo](http://devops-sys.com.br)


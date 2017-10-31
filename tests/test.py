import unittest




def exclude_dir(exclude):
    paths = ["/var/www/html/x1","/var/www/html/index.html"]

    retorno=False
    for path in paths: 
        normalize = path.replace('/','')
        temp = exclude.replace('/','').replace(normalize,'')
        exclude_limpo = exclude.replace('/','').replace(temp,'')

        if normalize == exclude_limpo:
           retorno= True

    return retorno

class bk_gdrive(unittest.TestCase):
        def test_diretorio(self):
            # testa diretorio a um nivel
            self. assertFalse(exclude_dir('/var/www/html/zip'))
            # testa diretoria a 2 nivel
            self. assertTrue(exclude_dir('/var/www/html/x1/zip'))
            #testa diretoia a 3 nivel
            self. assertTrue(exclude_dir('/var/www/html/x1/x3/zip'))
            #testar aquivo
            self. assertTrue(exclude_dir('/var/www/html/index.html'))
            # testar um  caminho errado 
            self. assertFalse(exclude_dir('/var/www/file.txt'))
            




if __name__ == '__main__':
        unittest.main()

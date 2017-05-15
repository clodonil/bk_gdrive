import sys
sys.path.append('../')
from libs.bkmagento import Backup_Magento



if __name__ == '__main__':
    test_google = Backup_Magento()
    test_google.check_limit_file()
    doctest.testmod()

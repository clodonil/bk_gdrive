import argparse


parser = argparse.ArgumentParser(description = 'Script de Backup do Magento no GDrive.')

parser.add_argument('--magento', action = 'store', dest = 'magento',
                                                   default = True, required = False,
                                                   help = 'Coloque True ou False para nao realizar o backup, default True.')



parser.add_argument('--mysql', action = 'store', dest = 'mysql',
                                                   default = True, required = False,
                                                   help = 'Coloque True ou False para nao realizar o backup, default True.')


args = parser.parse_args()

print(args)
if args.mysql:
    print("Mysql == true")
else:
    print("Mysql == False")

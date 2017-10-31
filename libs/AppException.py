# -*- coding: utf-8 -*-
class AppException(Exception):
    def __init__(self, **kwargs):
        if 'msg' in kwargs:
            self.msg= kwargs['msg']
        self.msg = self.msg.format(**kwargs)

class ErroObtendoDados(AppException):
    def __init__(self, **kwargs):
        self.msg = "Erro {erro}, devido a {razao}"
        self.code = 2
        super().__init__(**kwargs)

class ErroAoComunicarComServidor(AppException):
    def __init__(self, **kwargs):
        self.msg = "Não foi possível comunicar com o servidor {srv}"
        self.code = 3
        super().__init__(**kwargs)

class ErroAoProcessar(AppException):
    def __init__(self, **kwargs):
        self.msg = "Não possível realizar tarefa {tarefa}"
        self.code = 4
        super().__init__(**kwargs)

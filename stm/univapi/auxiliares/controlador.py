from abc import ABCMeta


class Controlador(object, metaclass=ABCMeta):
    def lista(self):
        raise NotImplementedError()

    def to_json(self):
        raise NotImplementedError()

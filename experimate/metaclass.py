import inspect
import types
from inspect import isfunction


class A():
    def log(self, p):
        print(p)


class B(A):
    def log(self, p):
        super().log('b'+p)
        print(p)


class Base(type):

    def __new__(metacls, cls, bases, namespace):
        for base in bases:
            print(base)

        upper_namespace = {}
        for k, v in namespace.items():
            if not isfunction(v) and not k.startswith('__'):
                upper_namespace[k.upper()] = v
            else:
                upper_namespace[k] = v
        return super().__new__(metacls, cls, bases, upper_namespace)


class BmixinL():
    def log(self, p):
        super(B, self).log('m')
        print('Bmixin')


class BmixinR():
    def log5(self, p):
        super(B, self).log('C')
        print('BmixinR')


class C(B, BmixinR):
    def log(self, p):
        super(B, self).log('c'+p)
        self.log5('tt')
        print(p)


class D(C):
    def log(self, p):
        super().log('d'+p)
        print(p)


class E(D, metaclass=Base):
    e = 10

    def log(self, p):
        super().log('e'+p)
        print(p)


if __name__ == '__main__':

    testE = D()
    print(D.__dict__)
    testE.log('test')

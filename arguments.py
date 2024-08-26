import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename = r'C:\Users\mrm\Downloads\MMR\Aptcon\Notepad challenge\UserLog.log',level = logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', filemode = 'w')



def logger(func):
    def log_func(*args, **kwargs):
        func(*args, **kwargs)
        logging.info('Func "{}", Pos Args "{}", Kw Args {}'.format(func.__name__, args, kwargs))
    return log_func


def attrAccess(*args):
    def IntAttrAccess(class_):
        class_.__getattr__orig = class_.__getattribute__
        class_.__setattr__orig = class_.__setattr__
        
        valData = []

        def new_getattr(self,name):
            if name == 'mileage':
                val = class_.__getattr__orig(self, name)
            return val
        
        def new_setattr(self, name, val):
            PastVal = new_getattr(self, name)
            print(PastVal)
            if name == args[0]:
                valData.append(val)
                print(valData)
                if val == valData[-1]:
                    print('Attr: {} = {} --> {}'.format(name, valData[-1], val))
   
            return class_.__setattr__orig(self, name, val)
       

        
        class_.__getattribute__ = new_getattr
        class_.__setattr__ = new_setattr

        return class_
    return IntAttrAccess

##@logger
##def add(x, y): 
##    return x+y
##
##
##add(3,3)

##@attrAccess('mileage')
##class Car:
##    def __init__(self, VIN):
##        self.mileage = 0
##        self.VIN = VIN
##
##car = Car('ABC123')
##car.mileage = 12
##car.mileage = 3
##car.mileage
##print('The VIN is', car.VIN)


class TankError(Exception):
    pass

def ObjTracking(className):
    def wrapper(func):
        def internalWrapper(*args):
##            func(*args)
##            print("{} instance is created: \n   \
##            Instance name: {}                   \
##            Instance Attributes: {}\n           \
##            \n                                  \
##            --Obj Tracking Report--             \
##            ".format(className, self, args)
            func(*args)
            print("From __init__: \n", args)
            
        return internalWrapper
    return wrapper
            

class Tank:

    @ObjTracking('Tank')
    def __init__(self, capacity):
        self.capacity = capacity
        self.__level = 0

    @property
    def level(self):
        return self.__level

    @level.setter
    def level(self, amount):
        print(self)
        if amount > 0:
            # fueling
            if amount <= self.capacity:
                self.__level = amount
            else:
                raise TankError('Too much liquid in the tank')
        elif amount < 0:
            raise TankError('Not possible to set negative liquid level')

    @level.deleter
    def level(self):
        if self.__level > 0:
            print('It is good to remember to sanitize the remains from the tank!')
        self.__level = None

# our_tank object has a capacity of 20 units
our_tank = Tank(20)

# our_tank's current liquid level is set to 10 units
our_tank.level = 10
print('Current liquid level:', our_tank.level)

our_tank.level = 8
print('Current liquid level:', our_tank.level)

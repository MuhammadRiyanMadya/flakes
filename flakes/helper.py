#! usr/bin/env python3

"""
General helper module
"""
import inspect

def Debugging(args: list):
    for arg in args:
        currentFrame = inspect.currentframe()
        try:
            frameLocals = currentFrame.f_back.f_locals
            varName = [name for name,value in frameLocals.items() if value is arg][0]
        finally:
            del currentFrame
        print("This the value inside \"{}\":\n\n {}\n".format(varName,arg))
        try:
            if type(arg).__name__ == 'list':
                print("size: {}\n".format(len(arg)))
            elif type(arg).__name__ == 'ndarray':
                print("size: {}\n".format(arg.shape))
            else:
                print("----sp----\n type: {}".format(type(arg).__name__))
        except Exception as e:
            print(e)
        print("=========================================================================")
    return

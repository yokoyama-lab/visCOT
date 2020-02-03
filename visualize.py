import os
from src import flow, yacc
from src.flow import Matplotlib

import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy import interpolate

class main:
    while True:
        try:
            s = input('>>> ')
            object = yacc.parser.parse(s)
            matplotlib = Matplotlib()
            object.set_matplotlib(matplotlib)
            object.draw()
            print("draw successful!")
            print("You can save picture or watch in matplotlib:"+"\n"+"If you want to save, please type \"save\"."+"\n"+"If you want to watch, please type \"watch\".")
            type = input(':')
            if type == "save":
                dirname = "flow_picture/"
                os.makedirs(dirname, exist_ok=True)
                filename = dirname + s + '.png'
                matplotlib.save_matplotlib(filename)
            elif type == "watch":
                matplotlib.show_matplotlib()
            else:
                pass
            matplotlib.clear_matplotlib()
        except AttributeError:
            print("please type correct syntax.")
        except EOFError:
            break

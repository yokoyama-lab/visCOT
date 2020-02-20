"""
Visualization program of tree representation of structurally stable incompressible flow in two dimensional multiply-connected domain
"""
# -*- coding: utf-8 -*-

import os
from src import flow, yacc
from src.flow import Canvas

"""
入力した木表現に対する流線を表示
"""
def main():
    while True:
        try:
            s = input('>>> ')
            object = yacc.parser.parse(s)
            canvas = Canvas()
            object.set_canvas(canvas)
            object.draw()
            print("draw successful!")
            print("You can save picture or watch in matplotlib:"+"\n"+"If you want to save, please type \"save\"."+"\n"+"If you want to watch, please type \"watch\".")
            type = input(':')
            if type == "save":
                dirname = "flow_picture/"
                os.makedirs(dirname, exist_ok=True)
                filename = dirname + s + '.png'
                canvas.save_canvas(filename)
            elif type == "watch":
                canvas.show_canvas()
            else:
                pass
            canvas.clear_canvas()
        except AttributeError:
            print("please type correct syntax.")
        except EOFError:
            break

if __name__ == "__main__":
    main()

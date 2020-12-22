"""
Visualization program of tree representation of structurally stable incompressible flow in two dimensional multiply-connected domain
"""
# -*- coding: utf-8 -*-

import os
from visualize import flow, yacc
from visualize.flow import Canvas
import argparse

"""
入力した木表現に対する流線を表示
"""
def main():
    parser = argparse.ArgumentParser(description='Visualize COT representation.')
    parser.add_argument('-i', '--interactive', help='interactive mode', action='store_true')
    parser.add_argument('-o', '--output', help='specify an output file (.png).')
    args = parser.parse_args()
    # print(args)

    canvas = Canvas()
    if args.interactive:
        while True:
            try:
                s = input('>>> ')
                object = yacc.parser.parse(s)
                object.set_canvas(canvas)
                object.draw()
                type = input('Select (save/show):')
                if type == "save":
                    filename = s + '.png'
                    canvas.save_canvas(filename)
                elif type == "show":
                    canvas.show_canvas()
                else:
                    pass
                canvas.clear_canvas()
            except AttributeError:
                print("please type correct syntax.")
            except EOFError:
                break
    else:
        object = yacc.parser.parse(input())
        object.set_canvas(canvas)
        object.draw()
        if args.output is None:
            canvas.show_canvas()
        else:
            canvas.save_canvas(args.output)

if __name__ == "__main__":
    main()

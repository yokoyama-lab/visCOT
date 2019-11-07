import flow
import yacc
import os

class main:
    while True:
        try:
            s = input('>>> ')
            object=yacc.parser.parse(s)
            object.draw()
            print(object.show())
            print("draw successful!")
            print("save picture or watch in matplotlib:"+"\n"+"if you want to save, please type \"save\""+"\n"+"if you want to show, please type \"watch\"")
            type=input(':')
            if(type=="save"):
                dirname = "flow_picture/"
                os.makedirs(dirname, exist_ok=True)
                filename = dirname+s+'.png'
                flow.save_matplotlib(filename)
            elif(type=="watch"):
                flow.show_matplotlib()
            else:
                pass
        except AttributeError:
            print("please tpye corect syntax.")
        except EOFError:
            break

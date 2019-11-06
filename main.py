import flow
import yacc

class main:
    if __name__ == '__main__':
     while True:
        try:
            s = input('>>> ')
        except EOFError:
            break
        print(yacc.parser.parse(s).show())
        yacc.parser.parse(s).draw()
        filename = s+'.png'
        flow.save_matplotlib(filename)
        flow.show_matplotlib()
        break
    
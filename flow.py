# 抽象構文木

import abc

import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy import interpolate

#matplotlibの設定
plt.figure()
ax = plt.axes()
plt.axis('off')
ax.set_aspect('equal')

def show_matplotlib():
    plt.show()

#スプライン補間
def spline(x,y,point,deg):
    tck,u = interpolate.splprep([x,y],k=deg,s=0)
    u = np.linspace(0,1,num=point,endpoint=True)
    spline = interpolate.splev(u,tck)
    return spline[0],spline[1]

#スプライン補間関数、引数はx座標y座標のタプルのリスト
def draw_spline(xy):
    count = len(xy)
    x = []
    y = []
    for i in range(0,count):
        a_xy = xy[i]
        x.append(a_xy[0])
        y.append(a_xy[1])
    if(count>=4):
        a,b = spline(x,y,100,3)
    elif(count==3):
        a,b = spline(x,y,100,2)
    else:
        print("draw_splineにおいて無効な入力がありました")
        a=[]
        b=[]
    plt.plot(a,b,color="black")

#円描画、引数centerはタプル
def draw_circle(r,center=(0,0),circle_fill=False,fc="grey"):
    if(circle_fill):
        circ=plt.Circle(center,r,ec="black",fc=fc,linewidth=1.5)
    else:
        circ=plt.Circle(center,r,ec="black",fill=False,linewidth=1.5)
    ax.add_patch(circ)
    ax.plot()

#theta=0で右向きの矢印
def draw_arrow(center,theta=0):
    col='k'
    arst='wedge,tail_width=0.6,shrink_factor=0.5'
    plt.annotate('',xy=(center[0]+(0.1*math.cos(theta)),center[1]+(0.05*math.sin(theta))),xytext=(center[0]+(0.1*math.cos(math.pi+theta)),center[1]+(0.1*math.sin(math.pi+theta))),arrowprops=dict(arrowstyle=arst,connectionstyle='arc3',facecolor=col,edgecolor=col,shrinkA=0,shrinkB=0))

#zoomした際大きさが変化する点をプロットする関数
def draw_point(center):
    plt.plot([center[0]], [center[1]],'k.')

class Node(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self):
        pass

    def show(self):
        pass

    def draw(self,center=(0,0)):#描画する際に親から与える中心点
        pass

    def return_detail(self):#この図形の専有領域の半径を返す
        pass

   # def parse(self):            # PLYでparseを作成するのではなく，このメソッドを実装してparserを作っても良い．
    #    pass

class A0(Node):
    def __init__(self,head):    #子の半径を定義
        self.head = head        #抽象構文木の作成

    def draw(self,center=[(0,0)]):#描画する際に親から与える中心点
        self.head.draw(center)
        #return center#子に与える中心点

    def show(self):
        return "a0("+ self.head.show() +")"

class B0_plus(Node):
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail

    def show(self):
        return "b0+("+ self.head.show() +"," + self.tail.show() +")"

class B0_minus(Node):
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail

    def show(self):
        return "b0-("+ self.head.show() +"," + self.tail.show() + ")"

class A_plus(Node):
    def __init__(self, head):
        self.head = head
        self.margin=0.5#子の専有領域と親の領域の余白
        self.r = head.r + self.margin
        self.bool_child = True
        self.child = [self.r]

    def show(self):
        return "a+(" + self.head.show() + ")"

    def draw(self,center=(0,0)):#描画する際に親から与える中心点
        draw_circle(self.r ,center)
        draw_arrow((center[0]-self.r,center[1]),theta=math.radians(270))
        draw_arrow((center[0]+self.r,center[1]),theta=math.radians(90))
        self.head.draw(center)

class A_minus(Node):
    def __init__(self, head):
        self.head = head
        self.r = head.r

    def show(self):
        return "a-(" + self.head.show() + ")"

class A2(Node):
    def __init__(self, head ,tail):
        self.head = head
        self.tail = tail

    def show(self):
        return "a2(" + self.head.show() + ',' + self.tail.show() + ")"

    def draw(self,center):
        pass

class Cons(Node):
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail
        self.child = []
        if(head.bool_child==True or tail.bool_child==True):
            if(head.bool_child==True):
                self.child.extend(head.child)
            if(tail.bool_child==True):
                self.child.extend(tail.child)

    def show(self):
        return "cons(" + self.head.show() + ", " + self.tail.show() + ")"

    def draw(self,children_list):
        self.head.draw(children_list.pop(0))
        if(len(children_list)!=1):
            self.tail.draw(children_list)
        else:
            self.tail.draw(children_list.pop(0))

class Nil(Node):
    def __init__(self):
        self.bool_child=False
        self.r=0

    def show(self):
        return "n"

    def draw(self,center=(0,0)):
        pass

class Leaf(Node):
    def __init__(self):
        self.bool_child=False
        self.r = 0

    def show(self):
        return "l"

    def draw(self,center=(0,0)):
        pass

class B_plus_plus(Node):
    def __init__(self, head ,tail):
        #headは上の円の半径、tailは下の円の半径
        self.head = head
        self.tail = tail
        self.margin=0.5#子の専有領域と親の領域の余白
        self.l_up_r = head.r #上の図の占有領域(半径)
        self.l_down_r = tail.r # 下の図の占有領域(半径)
        self.r = (2*self.l_up_r + 2*self.l_down_r + 4*self.margin) / 2 #全体の占有領域(半径)


    def show(self):
        return "b++(" + self.head.show() + ',' + self.tail.show() + ")"

    def draw(self,center=(0,0)):#描画する際に親から与える中心点
        draw_point((center[0],self.l_down_r+center[1]-self.l_up_r))#２つの円の交点
        draw_circle(self.l_up_r+self.margin,(center[0],self.l_down_r+self.margin+center[1]))#上の円
        draw_circle(self.l_down_r+self.margin,(center[0],-self.l_up_r-self.margin+center[1]))#下の円
        draw_arrow((center[0],self.l_down_r+2*self.margin+center[1]+self.l_up_r),math.radians(0))#上の円の矢印
        draw_arrow((center[0],-self.l_up_r-2*self.margin+center[1]-self.l_down_r),math.radians(180))#下の円の矢印
        self.head.draw((center[0],self.l_down_r+self.margin+center[1]))
        self.tail.draw((center[0],-self.l_up_r-self.margin+center[1]))

class B_plus_minus(Node):
    def __init__(self, head ,tail):
        self.head = head
        self.tail = tail
        self.r_1 = head.r + tail.r + 2#外の図の占有領域
        self.r_2 = tail.r + 1 # 中の図の占有領域
        self.r = self.r_1 + self.r_2 #全体の占有領域

    def show(self):
        return "b+-(" + self.head.show() + ',' + self.tail.show() + ")"

    def draw(self,center=(0,0)):#描画する際に親から与える中心点
        draw_circle(self.r_1 , (center[0], self.r_2 + center[1]))
        draw_circle(self.r_2 + self.r_1 , (center[0],center[1]))
        self.head.draw((center[0], self.r_2 + 1 + center[1]))
        self.tail.draw((center[0],center[1]- self.r_1))

class B_minus_minus(Node):
    def __init__(self, head ,tail):
        self.head = head
        self.tail = tail
        self.r_1 = head.r + 2 #上の図の占有領域
        self.r_2 = tail.r + 2 # 下の図の占有領域
        self.r = self.r_1 + self.r_2 #全体の占有領域

    def show(self):
        return "b--(" + self.head.show() + ',' + self.tail.show() + ")"

    def draw(self,center=(0,0)):#描画する際に親から与える中心点
        draw_circle(self.r_1 , (center[0], self.r_2  + center[1]))
        draw_circle(self.r_2 , (center[0], -self.r_1  + center[1]))
        self.head.draw((center[0], self.r_2 + center[1]))
        self.tail.draw((center[0], -self.r_1  + center[1]))

class B_minus_plus(Node):
    def __init__(self, head ,tail):
        self.head = head
        self.tail = tail
        self.r_1 = head.r + tail.r + 2#外の図の占有領域
        self.r_2 = tail.r + 1 # 中の図の占有領域
        self.r = self.r_1 + self.r_2 #全体の占有領域

    def show(self):
        return "b-+(" + self.head.show() + ',' + self.tail.show() + ")"

    def draw(self,center=(0,0)):#描画する際に親から与える中心点
        draw_circle(self.r_1 , (center[0], self.r_2 + center[1]))
        draw_circle(self.r_1+ self.r_2 , (center[0],center[1]))
        self.head.draw((center[0], self.r_2 + center[1]))
        self.tail.draw((center[0],center[1]- self.r_1))

class Beta_plus(Node):
    def __init__(self,head):
        self.head = head
        self.margin=0.5#要素の両脇に作るスペースの大きさ
        self.children_list=head.child
        self.children_list_count=len(self.children_list)
        self.high_children=0
        self.children_length=0
        self.longest_children=0
        for i in range(0,self.children_list_count):
            child=self.children_list[i]
            self.children_length=self.children_length+child[1]+self.margin#両脇にマージンを作成
            if(self.high_children<child[0]):
                self.high_children=child[0]
            if(self.longest_children<child[1]):
                self.longest_children=child[1]
        if(self.children_length/2<=self.longest_children):
            self.children_length=self.longest_children*2#betaとC系が重ならないように180度を超えないように
        self.center_r=(self.children_length)/(2*math.pi)#betaの円
        self.r=self.center_r+self.high_children#親に渡す全体の大きさ

    def show(self):
        return "be+(" + self.head.show() +  ")"

    def draw(self,center):
        draw_circle(self.center_r,center,circle_fill=True)
        for_children=[]
        length=0
        for i in range(0,self.children_list_count):
            length=length+self.margin
            for_children.append([length,self.center_r,center])#子供それぞれについて円周の基準点からどれだけ離れているかと、betaの半径、betaの中心
            child=self.children_list[i]
            length=length+child[1]
        self.head.draw(for_children)

class Beta_minus(Node):
    def __init__(self, head):
        self.head = head

    def show(self):
        return "be-(" + self.head.show() + ")"

class C_plus(Node):
    def __init__(self, head ,tail):
        self.head = head
        self.tail = tail
        self.margin=1#c系の要素の両脇に作るスペースの大きさ
        self.circ_margin=0.5#子のb系の要素と親の間の距離
        self.b_r = head.r
        self.children_list=tail.child
        self.children_list_count=len(self.children_list)
        self.high_children=0
        self.children_length=0
        self.high=0
        self.bottom_length=0
        for i in range(0,self.children_list_count):
            child=self.children_list[i]
            self.children_length=self.children_length+child[1]+self.margin
            if(self.high_children<child[0]):
                self.high_children=child[0]
        if((2*self.b_r)>self.children_length):
            self.bottom_length=self.b_r#ここについては後で確認すべき
        else:
            self.bottom_length=self.children_length
        self.high=(2*self.b_r)+self.high_children+self.margin

    def show(self):
        return "c+(" + self.head.show() + ',' + self.tail.show() + ")"

    def draw(self,children_list):
        self.length=children_list[0]
        self.center_r=children_list[1]
        self.center=children_list[2]
        self.start_theta=self.length/self.center_r
        self.start_point=((self.center_r*math.cos(self.start_theta))+self.center[0],(self.center_r*math.sin(self.start_theta))+self.center[1])
        self.end_theta=(self.length+self.children_length)/self.center_r
        self.end_point=((self.center_r*math.cos(self.end_theta))+self.center[0],(self.center_r*math.sin(self.end_theta))+self.center[1])
        self.high_theta=((self.end_theta-self.start_theta)/2)+self.start_theta
        self.high_point=(((self.center_r+self.high)*math.cos(self.high_theta))+self.center[0],((self.center_r+self.high)*math.sin(self.high_theta))+self.center[1])
        self.b_center=((self.center_r+self.high_children+self.circ_margin+self.b_r)*math.cos(self.high_theta)+self.center[0],(self.center_r+self.high_children+self.circ_margin+self.b_r)*math.sin(self.high_theta)+self.center[1])
        self.b_r_theta=math.pi-((math.pi/2)+self.high_theta)#180-(90+high_theta)bの専有領域の中心を基準に三角関数を適用するための準備
        self.b_r_center=(((self.b_r+self.circ_margin)*(math.cos(-self.b_r_theta)))+self.b_center[0],((self.b_r+self.circ_margin)*(math.sin(-self.b_r_theta))+self.b_center[1]))#0度の点
        self.b_l_center=(((self.b_r+self.circ_margin)*(math.cos(math.pi-self.b_r_theta)))+self.b_center[0],((self.b_r+self.circ_margin)*(math.sin(math.pi-self.b_r_theta))+self.b_center[1]))#180度の点
        self.b_rr_center=(((self.b_r+self.circ_margin)*(math.cos(-self.b_r_theta-(math.pi/6))))+self.b_center[0],((self.b_r+self.circ_margin)*(math.sin(-self.b_r_theta-(math.pi/6)))+self.b_center[1]))#-30度の点
        self.b_ll_center=(((self.b_r+self.circ_margin)*(math.cos(math.pi-self.b_r_theta+(math.pi/6))))+self.b_center[0],((self.b_r+self.circ_margin)*(math.sin(math.pi-self.b_r_theta+(math.pi/6)))+self.b_center[1]))#210度の点

        if(self.b_r!=0):
            draw_spline([self.start_point,self.b_rr_center,self.b_r_center,self.high_point,self.b_l_center,self.b_ll_center,self.end_point])
        else:
            draw_spline([self.start_point,self.high_point,self.end_point])
        draw_point(self.start_point)
        draw_point(self.end_point)
        draw_arrow(self.high_point,self.high_theta+math.radians(90))
        print("c",self.start_point,self.end_point,self.start_theta,self.end_theta,self.bottom_length,self.length,self.children_length,self.high)
        for_children=[]
        plus_length=self.length
        for i in range(0,self.children_list_count):
            plus_length=plus_length+self.margin/2
            for_children.append([self.b_center,[plus_length,self.center_r,self.center]])#子供それぞれについて円周の基準点からどれだけ離れているかと、betaの半径、betaの中心
            child=self.children_list[i]
            plus_length=plus_length+child[1]
        self.head.draw(for_children)


class C_minus(Node):
    def __init__(self, head ,tail):
        self.head = head
        self.tail = tail

    def show(self):
        return "c-(" + self.head.show() + ',' + self.tail.show() + ")"



#   a0(cons(a+(b++(b++(l,l),l)),n))
#

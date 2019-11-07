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

#matplotlibを表示
def show_matplotlib():
    plt.show()

def save_matplotlib(self):
    print("save picture! ")
    plt.savefig(self)

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

#xy_1からxy_2まで直線を引く関数
def draw_line(xy_1,xy_2):
    x_1=xy_1[0]
    y_1=xy_1[1]
    x_2=xy_2[0]
    y_2=xy_2[1]
    plt.plot([x_1,x_2],[y_1, y_2], 'k-')

#半径とthetaと中心点を使って二次元上の点の位置を求める関数
def theta_point(theta,r,center):
    return ((r*math.cos(theta))+center[0],(r*math.sin(theta))+center[1])

#C系の配列[(self.high,self.bottom_length),...]から最も大きい高さを求める関数
def c_list_high(children):
    high=0
    for child in children:
        if(high<child[0]):
            high=child[0]
    return high

#C系の配列[(self.high,self.bottom_length),...]から円周を求める関数
def c_list_circ_length(children,margin): #marginはc同士の間に空けたいスペース
    circ_length=0#円周を保存する変数
    longest_child=0#最も長い子供の長さを保存する変数
    for child in children:
        circ_length=circ_length+child[1]+margin #スペース分円周を伸ばす
        if(longest_child<child[1]):
            longest_child=child[1]
    if(circ_length/2<=longest_child): #もし円周の半分以上の長さを持つ子供がいれば、円周の長さをその子供に合わせる(C系とb系が重なることを避ける)
        circ_length=longest_child*2
    return circ_length

#Cをdrawするための配列[[基準点からの距離,親の半径,親の中心,親がB0かどうか],...]を作成する関数
def make_list_for_c(children,parent_r,parent_center,parent_type,margin,parent_length=0):#parent_lengthは親の円の特定の位置から書き始めたいとき用(a2など)
    c_list=[]
    length=parent_length
    for child in children:
        length=length+margin
        c_list.append([length,parent_r,parent_center,parent_type])#子供それぞれについて円周の基準点からどれだけ離れているかと、betaの半径、betaの中心、親がB0かどうか
        length=length+child[1]
    return c_list

class Node(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self):
        pass

    def show(self):
        pass

    def draw(self):
        pass

   # def parse(self):            # PLYでparseを作成するのではなく，このメソッドを実装してparserを作っても良い．
    #    pass

class A0(Node):
    def __init__(self,head):    #子の半径を定義
        self.type = "A0"
        self.head = head        #抽象構文木の作成
        self.margin = 0.5
        self.children_list=head.child #A0に送られるchildは[r,type]
        print("A0 was made!")

    def draw(self):
        long_child=0
        children_data=[] #drawで引数として渡す
        count_r=0
        if(self.head.type=="Nil"):
            draw_line((-1,0),(1,0)) #一様流を書く
        else:
            for child in self.children_list: #子供達の中で一番長いrを求める
                if(child[0]>long_child):
                    long_child=child[0]
            edge=long_child+self.margin
            for child in self.children_list:
                children_data.append((0,-count_r)) #子供それぞれについて中心点を作成して配列に格納
                if(child[1]=="A2"):
                    draw_line((-edge,-count_r),(-child[0],-count_r))
                    draw_line((child[0],-count_r),(edge,-count_r))
                elif(child[1]=="A_minus"):
                    draw_line((-edge,-count_r+child[0]),(edge,-count_r+child[0]))
                else:
                    draw_line((-edge,-count_r-child[0]),(edge,-count_r-child[0]))
                count_r=count_r+child[0]*2+self.margin*2 #次の子供の中心点をy軸に-r*2して繰り返す
        print("plot A0.")
        self.head.draw(children_data)
        #return center#子に与える中心点

    def show(self):
        return "a0("+ self.head.show() +")"

class B0_plus(Node):
    def __init__(self, head, tail):
        self.type = "B0_plus"
        self.head = head
        self.tail = tail
        self.margin=0.5
        self.children_list=tail.child
        high_children=c_list_high(self.children_list)
        children_length=c_list_circ_length(self.children_list,self.margin)
        if(children_length/(2*math.pi)>head.r+high_children+self.margin):
            self.r=(children_length)/(2*math.pi)
        else:
            self.r=head.r+high_children+self.margin
        print("B0_plus was made!.")

    def draw(self):
        side_r=self.r+self.margin
        ax.axvspan(-side_r,side_r,-side_r,side_r,color="gray",alpha = 0.5)#self.rの周りを塗り潰す
        draw_circle(self.r,(0,0),circle_fill=True,fc="white")
        for_children=make_list_for_c(self.children_list,self.r,(0,0),True,self.margin)
        print("plot B0_plus.")
        self.head.draw((0,0))
        self.tail.draw(for_children)

    def show(self):
        return "b0+("+ self.head.show() +"," + self.tail.show() +")"

class B0_minus(Node):
    def __init__(self, head, tail):
        self.type = "B0_minus"
        self.head = head
        self.tail = tail
        self.margin=0.5
        self.children_list=tail.child
        high_children=c_list_high(self.children_list)
        children_length=c_list_circ_length(self.children_list,self.margin)
        if(children_length/(2*math.pi)>head.r+high_children+self.margin):
            self.r=(children_length)/(2*math.pi)
        else:
            self.r=head.r+high_children+self.margin
        print("B0_plus was made!.")
        print("B0_minus was made!.")

    def draw(self):
        side_r=self.r+self.margin
        ax.axvspan(-side_r,side_r,-side_r,side_r,color="gray",alpha = 0.5)#self.rの周りを塗り潰す
        draw_circle(self.r,(0,0),circle_fill=True,fc="white")
        for_children=make_list_for_c(self.children_list,self.r,(0,0),True,self.margin)
        print("plot B0_plus.")
        self.head.draw((0,0))
        self.tail.draw(for_children)


    def show(self):
        return "b0-("+ self.head.show() +"," + self.tail.show() + ")"

class A_plus(Node):
    def __init__(self, head):
        self.type="A_plus"
        self.head = head
        self.margin=0.5#子の専有領域と親の領域の余白
        self.r = head.r + self.margin
        self.child = [(self.r,self.type)]
        print("A_plus was made!")

    def draw(self,center):#描画する際に親から与える中心点
        draw_circle(self.r ,center)
        draw_arrow((center[0]-self.r,center[1]),theta=math.radians(270))
        draw_arrow((center[0]+self.r,center[1]),theta=math.radians(90))
        print("plot A_plus.")
        self.head.draw(center)

    def show(self):
        return "a+(" + self.head.show() + ")"

class A_minus(Node):
    def __init__(self, head):
        self.type="A_minus"
        self.head = head
        self.margin=0.5#子の専有領域と親の領域の余白
        self.r = head.r + self.margin
        self.child = [(self.r,self.type)]
        print("A_minus was made!")

    def draw(self,center):#描画する際に親から与える中心点
        draw_circle(self.r ,center)
        draw_arrow((center[0]-self.r,center[1]),theta=math.radians(90))
        draw_arrow((center[0]+self.r,center[1]),theta=math.radians(270))
        print("plot A_minus.")
        self.head.draw(center)

    def show(self):
        return "a-(" + self.head.show() + ")"

class A2(Node):
    def __init__(self, head ,tail):
        self.type="A2"
        self.head = head
        self.tail = tail
        self.margin=0.5#子同士のスペースの定義
        if(c_list_high(head.child)>c_list_high(tail.child)):
            self.high=c_list_high(head.child)
        else:
            self.high=c_list_high(tail.child)#高さを調べる変数
        len_of_plus_circ=c_list_circ_length(head.child,self.margin)+self.margin#plus回りの長さ
        len_of_minus_circ=c_list_circ_length(tail.child,self.margin)+self.margin#minus回りの長さ
        if(len_of_plus_circ>=len_of_minus_circ):
            self.len_of_circ=len_of_plus_circ*2
        else:
            self.len_of_circ=len_of_minus_circ*2
        self.center_r=(self.len_of_circ)/(2*math.pi)#a_2の円の半径
        self.r=self.center_r+self.high#専有領域の半径
        self.child=[(self.r,self.type)]

    def draw(self,center):
        draw_circle(self.center_r,center,circle_fill=True)#a_2の描画
        draw_point((center[0]+self.center_r,center[1]))#一様流との交点の描画(右)
        draw_point((center[0]-self.center_r,center[1]))#一様流との交点の描画(左)
        draw_line((center[0]-self.r,center[1]),(center[0]-self.center_r,center[1]))
        draw_line((center[0]+self.center_r,center[1]),(center[0]+self.r,center[1]))
        for_plus_children=make_list_for_c(self.head.child,self.center_r,center,False,self.margin)
        for_minus_children=make_list_for_c(self.tail.child,self.center_r,center,False,self.margin,parent_length=self.len_of_circ/2)
        print("plot A2.")
        self.head.draw(for_plus_children)
        self.tail.draw(for_minus_children)

    def show(self):
        return "a2(" + self.head.show() + ',' + self.tail.show() + ")"

class Cons(Node):
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail
        self.type = head.type
        head_child=[s for s in head.child if s != (0,0)]
        tail_child=[s for s in tail.child if s != (0,0)]
        self.child = []
        if (len(head.child)!=0):
            for child in head_child:
                self.child.append(child)
        if (len(tail.child)!=0):
            for child in tail_child:
                self.child.append(child)
        print("Cons was made!",self.child)

    def draw(self,children_list):
        print(children_list)
        if(len(children_list)!=0):
            if(isinstance(children_list,tuple)):
                self.head.draw(children_list)
            else:
                self.head.draw(children_list.pop(0))
            if(len(children_list)>=1):
                self.tail.draw(children_list)
            else:
                self.tail.draw((0,0))
        print("plot Cons.")

    def show(self):
        return "cons(" + self.head.show() + ", " + self.tail.show() + ")"

class Nil(Node):
    def __init__(self):
        self.type="Nil"
        self.child=([(0,0)])
        print("Nil was made!")

    def show(self):
        return "n"

    def draw(self,center):
        pass

class Leaf(Node):
    def __init__(self):
        self.r=0
        print("Leaf was made!")

    def show(self):
        return "l"

    def draw(self,center):
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
        print("B_plus_plus was made!")

    def draw(self,center=(0,0)):#描画する際に親から与える中心点
        draw_point((center[0],self.l_down_r+center[1]-self.l_up_r))#２つの円の交点
        draw_circle(self.l_up_r+self.margin,(center[0],self.l_down_r+self.margin+center[1]))#上の円
        draw_circle(self.l_down_r+self.margin,(center[0],-self.l_up_r-self.margin+center[1]))#下の円
        draw_arrow((center[0],self.l_down_r+2*self.margin+center[1]+self.l_up_r),math.radians(0))#上の円の矢印
        draw_arrow((center[0],-self.l_up_r-2*self.margin+center[1]-self.l_down_r),math.radians(180))#下の円の矢印
        print("plot B_plus_plus.")
        self.head.draw((center[0],self.l_down_r+self.margin+center[1]))
        self.tail.draw((center[0],-self.l_up_r-self.margin+center[1]))

    def show(self):
        return "b++(" + self.head.show() + ',' + self.tail.show() + ")"

class B_plus_minus(Node):
    def __init__(self, head ,tail):
        self.head = head
        self.tail = tail
        self.margin=0.5#子の専有領域と親の領域の余白
        self.l_up_r = head.r #上の図の占有領域(半径)
        self.l_down_r = tail.r # 下の図の占有領域(半径)
        self.r = (2*self.l_up_r + 2*self.l_down_r + 4*self.margin) / 2
        print("B_plus_minus was made!")

    def draw(self,center=(0,0)):#描画する際に親から与える中心点
        draw_circle(self.l_up_r+self.margin,(center[0],self.l_down_r+self.margin+center[1]))
        draw_circle(self.l_up_r+self.l_down_r+2*self.margin,(center[0],center[1]))
        draw_point((center[0],self.l_down_r+self.margin+center[1]+self.l_up_r+self.margin))
        draw_arrow((center[0],self.l_down_r+self.margin+center[1]-self.l_up_r-self.margin),theta=math.radians(180))
        draw_arrow((center[0],center[1]-(self.l_up_r+self.l_down_r+2*self.margin)))
        print("plot B_plus_minus.")
        self.head.draw((center[0],self.l_down_r+self.margin+center[1]))
        self.tail.draw((center[0],-self.l_up_r-self.margin+center[1]))

    def show(self):
        return "b+-(" + self.head.show() + ',' + self.tail.show() + ")"

class Beta_plus(Node):
    def __init__(self,head):
        self.head = head
        self.margin=0.5#要素の両脇に作るスペースの大きさ
        high_children=c_list_high(head.child)
        children_length=c_list_circ_length(head.child,self.margin)
        self.center_r=(children_length)/(2*math.pi)#betaの円
        self.r=self.center_r+high_children#親に渡す全体の大きさ
        print("Beta_plus was made!")

    def draw(self,center):
        draw_circle(self.center_r,center,circle_fill=True)
        for_children=make_list_for_c(self.head.child,self.center_r,center,False,self.margin)
        print("plot Beta_plus.")
        self.head.draw(for_children)

    def show(self):
        return "be+(" + self.head.show() +  ")"

class B_minus_minus(Node):
    def __init__(self, head ,tail):
        self.head = head
        self.tail = tail
        self.margin=0.5#子の専有領域と親の領域の余白
        self.r = (2*head.r + 2*tail.r + 4*self.margin) / 2 #全体の占有領域(半径)
        print("B_minus_minus was made!")

    def draw(self,center=(0,0)):#描画する際に親から与える中心点
        draw_point((center[0],self.tail.r+center[1]-self.head.r))#２つの円の交点
        draw_circle(self.head.r+self.margin,(center[0],self.tail.r+self.margin+center[1]))#上の円
        draw_circle(self.tail.r+self.margin,(center[0],-self.head.r-self.margin+center[1]))#下の円
        draw_arrow((center[0],self.tail.r+2*self.margin+center[1]+self.head.r),math.radians(180))#上の円の矢印
        draw_arrow((center[0],-self.head.r-2*self.margin+center[1]-self.tail.r),math.radians(0))#下の円の矢印
        print("plot B_minus_minus.")
        self.head.draw((center[0],self.tail.r+self.margin+center[1]))
        self.tail.draw((center[0],-self.head.r-self.margin+center[1]))

    def show(self):
        return "b--(" + self.head.show() + ',' + self.tail.show() + ")"

class B_minus_plus(Node):
    def __init__(self, head ,tail):
        self.head = head
        self.tail = tail
        self.margin=0.5#子の専有領域と親の領域の余白
        self.l_up_r = head.r #上の図の占有領域(半径)
        self.l_down_r = tail.r # 下の図の占有領域(半径)
        self.r = (2*self.l_up_r + 2*self.l_down_r + 4*self.margin) / 2
        print("B_minus_plus was made!")

    def show(self):
        return "b-+(" + self.head.show() + ',' + self.tail.show() + ")"

    def draw(self,center=(0,0)):#描画する際に親から与える中心点
        draw_circle(self.l_up_r+self.margin,(center[0],self.l_down_r+self.margin+center[1]))
        draw_circle(self.l_up_r+self.l_down_r+2*self.margin,(center[0],center[1]))
        draw_point((center[0],self.l_down_r+self.margin+center[1]+self.l_up_r+self.margin))
        draw_arrow((center[0],self.l_down_r+self.margin+center[1]-self.l_up_r-self.margin),theta=math.radians(0))
        draw_arrow((center[0],center[1]-(self.l_up_r+self.l_down_r+2*self.margin)),theta=math.radians(180))
        print("plot B_minus_plus.")
        self.head.draw((center[0],self.l_down_r+self.margin+center[1]))
        self.tail.draw((center[0],-self.l_up_r-self.margin+center[1]))

class Beta_minus(Node):
    def __init__(self, head):
        self.head = head
        self.margin=0.5#要素の両脇に作るスペースの大きさ
        self.high_children=c_list_high(head.child)
        self.children_length=c_list_circ_length(head.child,self.margin)
        self.center_r=(self.children_length)/(2*math.pi)#betaの円
        self.r=self.center_r+self.high_children#親に渡す全体の大きさ
        print("Beta_minus was made!")

    def draw(self,center):
        draw_circle(self.center_r,center,circle_fill=True)
        for_children=make_list_for_c(self.head.child,self.center_r,center,False,self.margin)
        print("plot Beta_minus.")
        self.head.draw(for_children)

    def show(self):
        return "be-(" + self.head.show() + ")"

class C_plus(Node):
    def __init__(self, head ,tail):
        self.head = head
        self.tail = tail
        self.type = "C_plus"
        self.margin=1#c系の要素の両脇に作るスペースの大きさ
        self.circ_margin=0.5#子のb系の要素と親の間の距離
        self.high_children=c_list_high(tail.child)
        self.children_length=c_list_circ_length(tail.child,self.margin)
        if((2*head.r)>self.children_length):
            bottom_length=head.r#ここについては後で確認すべき
        else:
            bottom_length=self.children_length
        self.high=(2*head.r)+self.high_children+self.margin
        self.child=[(self.high,bottom_length)]
        print("C_plus was made!")

    def draw(self,children_list):
        self.length=children_list[0]
        self.center_r=children_list[1]
        self.center=children_list[2]
        self.bool_b0=children_list[3]
        self.start_theta=self.length/self.center_r
        self.start_point=theta_point(self.start_theta,self.center_r,self.center)
        self.end_theta=(self.length+self.children_length)/self.center_r
        self.end_point=theta_point(self.end_theta,self.center_r,self.center)
        self.high_theta=((self.end_theta-self.start_theta)/2)+self.start_theta
        if(self.bool_b0):
            self.high_point=theta_point(self.high_theta,self.center_r-self.high,self.center)
            self.b_center=theta_point(self.high_theta,self.center_r-self.high_children-self.circ_margin-self.head.r,self.center)
        else:
            self.high_point=theta_point(self.high_theta,self.center_r+self.high,self.center)
            self.b_center=theta_point(self.high_theta,self.center_r+self.high_children+self.circ_margin+self.head.r,self.center)
        if(self.head.r!=0):
            self.b_r_theta=math.pi-((math.pi/2)+self.high_theta)#180-(90+high_theta)bの専有領域の中心を基準に三角関数を適用するための準備
            self.b_r_center=theta_point(-self.b_r_theta,self.head.r+self.circ_margin,self.b_center)#0度の点
            self.b_l_center=theta_point(math.pi-self.b_r_theta,self.head.r+self.circ_margin,self.b_center)#180度の点
            self.b_rr_center=theta_point(-self.b_r_theta-(math.pi/6),self.head.r+self.circ_margin,self.b_center)#-30度の点
            self.b_ll_center=theta_point(math.pi-self.b_r_theta+(math.pi/6),self.head.r+self.circ_margin,self.b_center)#210度の点
            draw_spline([self.start_point,self.b_rr_center,self.b_r_center,self.high_point,self.b_l_center,self.b_ll_center,self.end_point])
        else:
            draw_spline([self.start_point,self.high_point,self.end_point])
        draw_point(self.start_point)
        draw_point(self.end_point)
        draw_arrow(self.high_point,self.high_theta+math.radians(90))
        for_children=make_list_for_c(self.tail.child,self.center_r,self.center,self.bool_b0,self.margin/2,parent_length=self.length)
        print("plot C_plus.")
        self.head.draw(self.b_center)
        self.tail.draw(for_children)

    def show(self):
        return "c+(" + self.head.show() + ',' + self.tail.show() + ")"

class C_minus(Node):
    def __init__(self, head ,tail):
        self.head = head
        self.tail = tail
        self.type = "C_minus"
        self.margin=1#c系の要素の両脇に作るスペースの大きさ
        self.circ_margin=0.5#子のb系の要素と親の間の距離
        self.children_list=tail.child
        self.b_r = head.r
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
        self.bool_child=True
        self.child=[(self.high,self.bottom_length)]
        print("C_minus was made!")

    def draw(self,children_list):
        self.length=children_list[0]
        self.center_r=children_list[1]
        self.center=children_list[2]
        self.bool_b0=children_list[3]
        self.start_theta=self.length/self.center_r
        self.start_point=((self.center_r*math.cos(self.start_theta))+self.center[0],(self.center_r*math.sin(self.start_theta))+self.center[1])
        self.end_theta=(self.length+self.children_length)/self.center_r
        self.end_point=((self.center_r*math.cos(self.end_theta))+self.center[0],(self.center_r*math.sin(self.end_theta))+self.center[1])
        self.high_theta=((self.end_theta-self.start_theta)/2)+self.start_theta
        if(self.bool_b0):
            self.high_point=theta_point(self.high_theta,self.center_r-self.high,self.center)
            self.b_center=theta_point(self.high_theta,self.center_r-self.high_children-self.circ_margin-self.b_r,self.center)
        else:
            self.high_point=theta_point(self.high_theta,self.center_r+self.high,self.center)
            self.b_center=theta_point(self.high_theta,self.center_r+self.high_children+self.circ_margin+self.b_r,self.center)
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
        draw_arrow(self.high_point,self.high_theta+math.radians(270))
        for_children=[]
        plus_length=self.length
        for i in range(0,self.children_list_count):
            plus_length=plus_length+self.margin/2
            for_children.append([plus_length,self.center_r,self.center,self.bool_b0])#子供それぞれについて円周の基準点からどれだけ離れているかと、betaの半径、betaの中心
            child=self.children_list[i]
            plus_length=plus_length+child[1]
        print("plot C_minus.")
        self.head.draw(self.b_center)
        self.tail.draw(for_children)

    def show(self):
        return "c-(" + self.head.show() + ',' + self.tail.show() + ")"


#a0(cons(a+(b++(b++(l,l),l)),cons(a+(l),n)))
#a0(cons(a+(l),cons(a+(l),n)))
#a0(cons(a2(cons(c+(l,n),cons(c+(l,n),n)),cons(c-(l,n),cons(c-(l,n),n))),n))
#a0(cons(a+(b++(be+(cons(c+(l,n),n)),l)),n))
#a0(cons(a+(b++(be+(cons(c+(l,n),n)),be+(cons(c+(l,n),n)))),n))
#a0(cons(a+(be+(cons(c+(l,cons(c-(l,n),n)),cons(c+(l,n),n)))),n))
#a0(cons(a+(be+(cons(c+(l,n),cons(c+(l,n),n)))),n))
#a0(cons(a+(be+(cons(c+(b++(b++(b++(be+(cons(c+(l,n),n)),be+(cons(c+(l,n),n))),l),l),cons(c-(l,n),n)),cons(c+(l,n),n)))),n))
#b0+(l,(cons(c+(l,n),n)))
#b0-(b--(l,l),(cons(c-(l,n),cons(c-(l,n),cons(c-(l,n),n)))))

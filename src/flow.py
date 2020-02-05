import abc

import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy import interpolate

# 半径とthetaと中心点を使って二次元上の点の位置を求める関数
def theta_point(theta, r, center):
    return (r * math.cos(theta) + center[0], r * math.sin(theta) + center[1])

# C系の配列[(self.high,self.bottom_length),...]から最も大きい高さを求める関数
def c_list_high(children):
    return max(map(lambda x: x[0], children))

# C系の配列[(self.high,self.bottom_length),...]から円周を求める関数
def c_list_circ_length(children, margin):  
    # marginはc同士の間に空けたいスペース
    circ_length = 0  # 円周を保存する変数
    longest_child = 0  # 最も長い子供の長さを保存する変数
    for child in children:
        circ_length += child[1]+margin  # スペース分円周を伸ばす
        if longest_child < child[1]:
            longest_child = child[1]
    # もし円周の半分以上の長さを持つ子供がいれば、円周の長さをその子供に合わせる
    # (C系とb系が重なることを避ける)
    if circ_length/2 <= longest_child:
        circ_length = longest_child*2
    return circ_length

# Cをdrawするための配列[[基準点からの距離,親の半径,親の中心,親がB0かどうか],...]を作成する関数
# parent_lengthは親の円の特定の位置から書き始めたいとき用(a2など)
def make_list_for_c(children, parent_r, parent_center, parent_type, margin, parent_length=0, first_child=False):
    c_list = []
    length = parent_length
    if parent_type and first_child:
        length += 0.3
        for child in children:
            # 子供それぞれについて円周の基準点からどれだけ離れているかと、betaの半径、betaの中心、親がB0かどうか
            c_list.append({"length":length, "parent_r":parent_r, "parent_center":parent_center, "parent_type":parent_type})
            if length+(margin/len(children))-child[1] < length:
                length += 1.5
            else:
                length += (margin/len(children))-child[1]+1
    else:
        for child in children:
            length += margin
            c_list.append({"length":length, "parent_r":parent_r, "parent_center":parent_center, "parent_type":parent_type})
            length += child[1]
    return c_list

class Canvas:
    # matplotlibの初期化設定
    def __init__(self):
        self.ax = plt.axes()
        plt.axis('off')
        self.ax.set_aspect('equal')

    # 作成された図を表示
    def show_canvas(self):
        plt.tight_layout()
        plt.show()

    # 作成された画像を保存
    def save_canvas(self, file_name):
        print("save picture! ")
        plt.tight_layout()
        plt.savefig(file_name)

    # matplotlibのデータ削除
    def clear_canvas(self):
        plt.close("all")
        plt.cla()
        plt.axis('off')
        self.ax.set_aspect('equal')

    # スプライン補間
    def spline(self, x, y, point, deg):
        tck, u = interpolate.splprep([x, y], k=deg, s=0)
        u = np.linspace(0, 1, num=point, endpoint=True)
        spline = interpolate.splev(u, tck)
        return spline[0], spline[1]

    # スプライン補間関数、引数はx座標y座標のタプルのリスト
    def draw_spline(self, xy):
        count = len(xy)
        x = []
        y = []
        for i in range(0, count):
            a_xy = xy[i]
            x.append(a_xy[0])
            y.append(a_xy[1])
        if count >= 4:
            a, b = self.spline(x, y, 100, 3)
        elif count == 3:
            a, b = self.spline(x, y, 100, 2)
        plt.plot(a, b, color="black")

    # 円描画、引数centerはタプル
    def draw_circle(self, r, center=(0, 0), circle_fill=False, fc="grey"):
        if circle_fill:
            circ = plt.Circle(center, r, ec="black", fc=fc, linewidth=1.5)
        else:
            circ = plt.Circle(center, r, ec="black", fill=False, linewidth=1.5)
        self.ax.add_patch(circ)
        self.ax.plot()

    # theta=0で右向きの矢印
    def draw_arrow(self, center, theta=0):
        col = 'k'
        arst = 'wedge,tail_width=0.6,shrink_factor=0.5'
        plt.annotate('', xy=(center[0]+(0.1*math.cos(theta)), center[1]+(0.05*math.sin(theta))), xytext=(center[0]+(0.1*math.cos(math.pi+theta)), center[1]+(0.1*math.sin(math.pi+theta))), arrowprops=dict(arrowstyle=arst, connectionstyle='arc3', facecolor=col, edgecolor=col, shrinkA=0, shrinkB=0))

    # zoomした際大きさが変化する点をプロットする関数
    def draw_point(self, center):
        plt.plot([center[0]], [center[1]], 'k.')

    # xy_1からxy_2まで直線を引く関数
    def draw_line(self, xy_1, xy_2):
        plt.plot([xy_1[0], xy_2[0]], [xy_1[1], xy_2[1]], 'k-')

    # 半径rの周りを塗りつぶす関数
    def axvspan(self, r):
        self.ax.axvspan(-r, r, -r, r, color="gray", alpha=0.5)

class Node(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self):
        self.canvas = None
        self.head = None
        self.tail = None

    def draw(self, *arg):
        pass

    def plot_arrow(self, *arg):
        pass

    def set_canvas(self, canvas):
        self.canvas = canvas
        if self.head is not None:
            self.head.set_canvas(canvas)
        if self.tail is not None:
            self.tail.set_canvas(canvas)

class A0(Node):
    def __init__(self, head):    # 子の半径を定義
        super().__init__()
        self.type = "A0"
        self.head = head        # 抽象構文木の作成
        self.margin = 0.5

    def draw(self):
        long_child = 0
        children_data = []  # drawで引数として渡す
        count_r = 0
        if self.head.type == "Nil":
            # 一様流を書く
            self.canvas.draw_line((-1, 0), (1, 0))
            self.canvas.draw_arrow((0, 0), math.pi)
        else:
            for child in self.head.child:  # 子供達の中で一番長いrを求める
                if child[0] > long_child:
                    long_child = child[0]
            edge = long_child + self.margin
            for child in self.head.child:
                # 次の子供の中心点をy軸に-r*2して繰り返す
                count_r += child[0] + self.margin
                # 子供それぞれについて中心点を作成して配列に格納
                children_data.append({"center":(0, -count_r), "edge":edge})
                count_r += child[0] + self.margin
        self.head.draw(children_data)

class B0(Node):
    def __init__(self, head, tail):
        super().__init__()
        self.head = head
        self.tail = tail
        self.margin = 0.5
        high_children = c_list_high(tail.child)
        children_length = c_list_circ_length(tail.child, self.margin)
        self.r = max(children_length / (2 * math.pi), head.r + high_children + self.margin)

    def draw(self):
        side_r = self.r + self.margin
        self.canvas.axvspan(side_r)
        self.canvas.draw_circle(self.r, (0, 0), circle_fill=True, fc="white")
        self.plot_arrow()
        for_children = make_list_for_c(self.tail.child, self.r, (0, 0), True, 2*self.r*math.pi, first_child=True)
        self.head.draw((0, 0))
        self.tail.draw(for_children)

class B0_plus(B0):
    def plot_arrow(self):
        self.canvas.draw_arrow((self.r, 0), math.pi/2)

class B0_minus(B0):
    def plot_arrow(self):
        self.canvas.draw_arrow((self.r, 0), math.pi*1.5)

class A_Flip(Node):
    def __init__(self, head):
        super().__init__()
        self.head = head
        self.margin = 0.5  # 子の専有領域と親の領域の余白
        self.r = head.r + self.margin

    def draw(self, info_dic):  # 描画する際に親から与える中心点
        center = info_dic["center"]
        edge = info_dic["edge"]
        self.canvas.draw_circle(self.r, center)
        self.plot_arrow(center,edge)
        self.head.draw(center)

class A_plus(A_Flip):
    def __init__(self, head):
        super().__init__(head)
        self.type = "A_plus"
        self.child = [(self.r, self.type)]

    def plot_arrow(self, center, edge):
        self.canvas.draw_point((center[0], center[1]-self.r))
        self.canvas.draw_arrow((center[0]-self.r, center[1]), theta=math.pi*1.5)
        self.canvas.draw_arrow((center[0]+self.r, center[1]), theta=math.pi/2)
        self.canvas.draw_line((-edge, center[1]-self.r), (edge, center[1]-self.r))
        self.canvas.draw_arrow((-edge/2, center[1]-self.r), math.pi)
        self.canvas.draw_arrow((edge/2, center[1]-self.r), math.pi)

class A_minus(A_Flip):
    def __init__(self, head):
        super().__init__(head)
        self.type = "A_minus"
        self.child = [(self.r, self.type)]

    def plot_arrow(self, center, edge):
        self.canvas.draw_point((center[0], center[1]+self.r))
        self.canvas.draw_arrow((center[0]-self.r, center[1]), theta=math.pi/2)
        self.canvas.draw_arrow((center[0]+self.r, center[1]), theta=math.pi*1.5)
        self.canvas.draw_line((-edge, center[1]+self.r), (edge, center[1]+self.r))
        self.canvas.draw_arrow((-edge/2, center[1]+self.r), math.pi)
        self.canvas.draw_arrow((edge/2, center[1]+self.r), math.pi)

class A2(Node):
    def __init__(self, head, tail):
        super().__init__()
        self.type = "A2"
        self.head = head
        self.tail = tail
        self.margin = 0.5  # 子同士のスペースの定義
        if c_list_high(head.child) > c_list_high(tail.child):
            self.high = c_list_high(head.child)
        else:
            self.high = c_list_high(tail.child)  # 高さを調べる変数
        len_of_plus_circ = c_list_circ_length(head.child, self.margin) + self.margin  # plus回りの長さ
        len_of_minus_circ = c_list_circ_length(tail.child, self.margin) + self.margin  # minus回りの長さ
        if len_of_plus_circ >= len_of_minus_circ:
            self.len_of_circ = len_of_plus_circ * 2
        else:
            self.len_of_circ = len_of_minus_circ * 2
        self.center_r = self.len_of_circ / (2 * math.pi)  # a_2の円の半径
        self.r = self.center_r + self.high  # 専有領域の半径
        self.child = [(self.r, self.type)]

    def draw(self, info_dic):
        center = info_dic["center"]
        edge = info_dic["edge"]
        self.canvas.draw_circle(self.center_r, center, circle_fill=True)  # a_2の描画
        self.canvas.draw_point((center[0]+self.center_r, center[1]))  # 一様流との交点の描画(右)
        self.canvas.draw_point((center[0]-self.center_r, center[1]))  # 一様流との交点の描画(左)
        self.canvas.draw_line((center[0]-self.r, center[1]), (center[0]-self.center_r, center[1]))
        self.canvas.draw_line((center[0]+self.center_r, center[1]), (center[0]+self.r, center[1]))
        self.canvas.draw_line((-edge, center[1]), (-self.r, center[1]))
        self.canvas.draw_line((self.r, center[1]), (edge, center[1]))
        self.canvas.draw_arrow(((-edge-self.r)/2, center[1]), math.pi)
        self.canvas.draw_arrow(((self.r+edge)/2, center[1]), math.pi)
        for_plus_children = make_list_for_c(self.head.child, self.center_r, center, False, self.margin)
        for_minus_children = make_list_for_c(self.tail.child, self.center_r, center, False, self.margin, parent_length=self.len_of_circ/2)
        self.head.draw(for_plus_children)
        self.tail.draw(for_minus_children)

class Cons(Node):
    def __init__(self, head, tail):
        super().__init__()
        self.head = head
        self.tail = tail
        self.type = head.type
        head_child = [s for s in head.child if s != (0, 0)]
        tail_child = [s for s in tail.child if s != (0, 0)]
        self.child = []
        for child in head_child:
                self.child.append(child)
        for child in tail_child:
                self.child.append(child)

    def draw(self, children_list):
        self.head.draw(children_list.pop(0))
        if len(children_list) != 0:
            self.tail.draw(children_list)

class Nil(Node):
    def __init__(self):
        super().__init__()
        self.type = "Nil"
        self.child = [(0, 0)]

    def draw(self, center):
        pass

class Leaf(Node):
    def __init__(self):
        super().__init__()
        self.r = 0

    def draw(self, center):
        pass

class B_Evc(Node):
    def __init__(self, head, tail):
        super().__init__()
        # headは上の円の半径、tailは下の円の半径
        self.head = head
        self.tail = tail
        self.margin = 0.5  # 子の専有領域と親の領域の余白
        self.l_up_r = head.r  # 上の図の占有領域(半径)
        self.l_down_r = tail.r  # 下の図の占有領域(半径)
        self.r = (2 * self.l_up_r + 2 * self.l_down_r + 4 * self.margin) / 2  # 全体の占有領域(半径)

    def draw(self, center=(0, 0)):  # 描画する際に親から与える中心点
        self.canvas.draw_point((center[0], self.l_down_r+center[1]-self.l_up_r))  # ２つの円の交点
        self.canvas.draw_circle(self.l_up_r+self.margin, (center[0], self.l_down_r+self.margin+center[1]))  # 上の円
        self.canvas.draw_circle(self.l_down_r+self.margin, (center[0], -self.l_up_r-self.margin+center[1]))  # 下の円
        self.plot_arrow(center)
        self.head.draw((center[0], self.l_down_r+self.margin+center[1]))
        self.tail.draw((center[0], -self.l_up_r-self.margin+center[1]))

class B_Flip(Node):
    def __init__(self, head, tail):
        super().__init__()
        self.head = head
        self.tail = tail
        self.margin = 0.5  # 子の専有領域と親の領域の余白
        self.l_up_r = head.r  # 上の図の占有領域(半径)
        self.l_down_r = tail.r  # 下の図の占有領域(半径)
        self.r = (2 * self.l_up_r + 2 * self.l_down_r + 4 * self.margin) / 2

    def draw(self, center=(0, 0)):  # 描画する際に親から与える中心点
        self.canvas.draw_circle(self.l_up_r+self.margin, (center[0], self.l_down_r+self.margin+center[1]))
        self.canvas.draw_circle(self.l_up_r+self.l_down_r+2*self.margin, center)
        self.canvas.draw_point((center[0], self.l_down_r+self.margin+center[1]+self.l_up_r+self.margin))
        self.plot_arrow(center)
        self.head.draw((center[0], self.l_down_r+self.margin+center[1]))
        self.tail.draw((center[0], -self.l_up_r-self.margin+center[1]))

class Beta(Node):
    def __init__(self, head):
        super().__init__()
        self.head = head
        self.margin = 0.5  # 要素の両脇に作るスペースの大きさ
        high_children = c_list_high(head.child)
        children_length = c_list_circ_length(head.child, self.margin)
        self.center_r = children_length / (2 * math.pi)  # betaの円
        if children_length < 1:
            self.center_r = 7 / (2 * math.pi)
        self.r = self.center_r + high_children  # 親に渡す全体の大きさ

    def draw(self, center):
        self.canvas.draw_circle(self.center_r, center, circle_fill=True)
        for_children = make_list_for_c(self.head.child, self.center_r, center, False, self.margin)
        self.plot_arrow(center)
        self.head.draw(for_children)

class B_plus_plus(B_Evc):
    def plot_arrow(self, center):
        # 上の円の矢印
        self.canvas.draw_arrow((center[0], self.l_down_r+2*self.margin+center[1]+self.l_up_r), math.pi) 
        # 下の円の矢印
        self.canvas.draw_arrow((center[0], -self.l_up_r-2*self.margin+center[1]-self.l_down_r), 0)  

class B_plus_minus(B_Flip):
    def plot_arrow(self, center):
        self.canvas.draw_arrow((center[0], self.l_down_r+self.margin+center[1]-self.l_up_r-self.margin), theta=math.pi)
        self.canvas.draw_arrow((center[0], center[1]-(self.l_up_r+self.l_down_r+2*self.margin)))

class Beta_plus(Beta):
    def plot_arrow(self, center):
        self.canvas.draw_arrow((center[0]+self.center_r, center[1]), math.pi/2)

class B_minus_minus(B_Evc):
    def plot_arrow(self, center):
        self.canvas.draw_arrow((center[0], self.tail.r+2*self.margin+center[1]+self.head.r), 0)
        self.canvas.draw_arrow((center[0],-self.head.r-2*self.margin+center[1]-self.tail.r), math.pi)

class B_minus_plus(B_Flip):
    def plot_arrow(self, center):
        self.canvas.draw_arrow((center[0], self.l_down_r+self.margin+center[1]-self.l_up_r-self.margin), theta=0)
        self.canvas.draw_arrow((center[0], center[1]-(self.l_up_r+self.l_down_r+2*self.margin)), theta=math.pi)

class Beta_minus(Beta):
    def plot_arrow(self, center):
        self.canvas.draw_arrow((center[0]+self.center_r, center[1]), math.pi*1.5)

class C(Node):
    def __init__(self, head, tail):
        super().__init__()
        self.head = head
        self.tail = tail
        self.margin = 1  # c系の要素の両脇に作るスペースの大きさ
        self.circ_margin = 0.5  # 子のb系の要素と親の間の距離
        self.high_children = c_list_high(tail.child)
        self.children_length = c_list_circ_length(tail.child, self.margin)
        bottom_length = max(head.r*2, self.children_length)
        self.high = 2 * head.r + self.high_children + self.margin
        if (self.head.r == 0) and (len(self.tail.child) != 1):
            self.high += len(self.tail.child) * 1
        self.child = [(self.high, bottom_length)]

    def draw(self, c_data):
        if self.high_children == 0:
            self.high_children = 0.3
        length = c_data["length"]
        center_r = c_data["parent_r"]
        center = c_data["parent_center"]
        bool_b0 = c_data["parent_type"]
        start_theta = length / center_r
        start_point = theta_point(start_theta, center_r, center)
        end_theta = (length + self.children_length) / center_r
        end_point = theta_point(end_theta, center_r, center)
        high_theta = (end_theta-start_theta) / 2 + start_theta
        if bool_b0:
            high_point = theta_point(high_theta, center_r-self.high, center)
            b_center = theta_point(high_theta, center_r-self.high_children-self.circ_margin-self.head.r, center)
        else:
            high_point = theta_point(high_theta, center_r+self.high, center)
            b_center = theta_point(high_theta, center_r+self.high_children+self.circ_margin+self.head.r, center)
        self.plot_arrow(bool_b0, high_point, high_theta)
        if self.head.r != 0:
            # 180-(90+high_theta)bの専有領域の中心を基準に三角関数を適用するための準備
            b_r_theta = math.pi - (math.pi/2+high_theta)  
            # 0度の点
            b_r_center = theta_point(-b_r_theta, self.head.r+self.circ_margin, b_center)
            # 180度の点
            b_l_center = theta_point(math.pi-b_r_theta, self.head.r+self.circ_margin, b_center)
            if self.head.r * 2 < self.children_length / 2:
                self.canvas.draw_spline([start_point, high_point, end_point])
            else:
                self.canvas.draw_spline([start_point, b_r_center, high_point, b_l_center, end_point])
        else:
            self.canvas.draw_spline([start_point, high_point, end_point])
        self.canvas.draw_point(start_point)
        self.canvas.draw_point(end_point)
        for_children = make_list_for_c(self.tail.child, center_r, center, bool_b0, self.margin/1.5, parent_length=length)
        self.head.draw(b_center)
        self.tail.draw(for_children)

class C_plus(C):
    def __init__(self, head, tail):
        super().__init__(head, tail)
        self.type = "C_plus"

    def plot_arrow(self, bool_b0, high_point, high_theta):
        self.canvas.draw_arrow(high_point, high_theta+ math.pi*(1.5 if bool_b0 else 0.5))

class C_minus(C):
    def __init__(self, head, tail):
        super().__init__(head, tail)
        self.type = "C_minus"

    def plot_arrow(self, bool_b0, high_point, high_theta):
        self.canvas.draw_arrow(high_point, high_theta+ math.pi*(0.5 if bool_b0 else 1.5))

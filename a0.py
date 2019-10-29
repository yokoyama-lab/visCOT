# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 01:35:51 2019

@author: 16se090
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate

#matplotlibの設定
plt.figure()
ax = plt.axes()
plt.axis('off')
ax.set_aspect('equal')

#スプライン補間
def spline(x,y,point,deg):
    tck,u = interpolate.splprep([x,y],k=deg,s=0) 
    u = np.linspace(0,1,num=point,endpoint=True) 
    spline = interpolate.splev(u,tck)
    return spline[0],spline[1]

#要素数4以上用のスプライン補間関数、引数はx座標y座標のタプルのリスト
def draw_spline(xy):
    count = len(xy)
    x = []
    y = []
    for i in range(0,count):
        a_xy = xy[i]
        x.append(a_xy[0])
        y.append(a_xy[1])
    a,b = spline(x,y,100,3)
    plt.plot(a,b,color="black")

#円描画、引数centerはタプル
def draw_circle(r,center=(0,0)):
    circ=plt.Circle(center,r,ec="black",fill=False,linewidth=1.5)
    ax.add_patch(circ)
    ax.plot()

#上が開いているbeta系スプライン補間(b系の上側など)
def up_beta_spline(r,center=(0,0)):
    r_top = (center[0]+r,center[1])
    l_top = (center[0]-r,center[1])
    bottom = (center[0],center[1]-(r+2))
    left = (center[0]-(r+1),center[1]-r)
    right = (center[0]+(r+1),center[1]-r)
    return [r_top,right,bottom,left,l_top]
    #draw_spline([r_top,right,bottom,left,l_top])

#下が開いているbeta系スプライン補間(b系の下側など)
def down_beta_spline(r,center):
    top = (center[0],center[1]+(r+2))
    r_bottom = (center[0]+r,center[1])
    l_bottom = (center[0]-r,center[1])
    left = (center[0]-(r+1),center[1]+r)
    right = (center[0]+(r+1),center[1]+r)
    return [l_bottom,left,top,right,r_bottom]
    #draw_spline([l_bottom,left,top,right,r_bottom])

#引数centerの値で平行移動したものを描く
def draw_move_spline(l_xy,center):
    xy=[]
    for i in range(0,len(l_xy)):
        a_xy = l_xy[i]
        tpl=((a_xy[0]+center[0]),(a_xy[1]+center[1]))
        xy.append(tpl)
    draw_spline(xy)

#上下の点を与えその中心を返す
def define_center(top=(0,0),down=(0,0)):
    return (top[0],top[1]-(top[1]-down[1])/2)

class A0:
    
    def __init__(self,head,a0_r=0):#子の半径を定義
        self.head = head 
        if head == "XXXXXXX":  #子供のクラス
            self.a0_r = a0_r
            self.r = self.a0_r + 1
        elif head == self.n:
            self.head()
            self.a0_r =a0_r
    
    def draw(self,center=(0,0)):#描画する際に親から与える中心点
        draw_circle(self.r,center)
        return center#子に与える中心点
    
    def show(self):
        return "a0("+ self.head.show() +")" #初めの文字を読み取り抽象構文木の作成
    
    def return_detail(self):#この図形の専有領域の半径を返す
        return self.r
    
class cons:
    
    def __init__(self,cons_r=0,head,tail):
        self.head = head
        self.tail = tail
        
        self.head()
        self.cons.r =cons.r 
        self.r = cons.r
        
        if tail == self.cons:
            self.tail()
            self.
            
        
        
        
        
        
        
        
        
        
        
        
        
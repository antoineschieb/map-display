import os
import numpy as np
import tkinter as tk
import math
import cmath
import scipy.special 
from PIL import Image, ImageTk



from parameters import X_OFF, Y_OFF, BEATMAPS_PATH

class Segment:
    def __init__(self,x0,y0,x1,y1):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
    
    def at(self,t):
        try:
            assert 0<=t<=1
        except:
            print(t)
        
        return (1-t)*self.x0 + t*self.x1  , (1-t)*self.y0 + t*self.y1


class Bezier:
    def __init__(self,points_list):
        self.points_list = points_list
        self.n = len(points_list)

    def at(self,t):
        assert 0<=t<=1
        Bx_t = 0
        By_t = 0
        for i in range(self.n): # sum starts
            [Px,Py] = self.points_list[i]
            prodx = scipy.special.binom(self.n-1, i) * math.pow(1-t,self.n-1-i) * math.pow(t,i) * Px 
            prody = scipy.special.binom(self.n-1, i) * math.pow(1-t,self.n-1-i) * math.pow(t,i) * Py
            Bx_t += prodx 
            By_t += prody 
        return Bx_t,By_t

    def slope_vector_at(self,t):
        b1 = Bezier(self.points_list[1:])
        b2 = Bezier(self.points_list[:-1])
        xd2,xdd2 = b2.at(t) 
        xd1,xdd1 = b1.at(t) 
        
        return self.n * (xd2 - xd1) ,  self.n * (xdd2 - xdd1)




def get_hobj_str_list(osu_file_path):
    hobj_str_list = []
    flag=False
    with open(osu_file_path,'r') as f:
        for _, line in enumerate(f):
            if flag:hobj_str_list.append(line[:-1])
            if line=='[HitObjects]\n':flag=True
    return hobj_str_list

def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb 


def hex_to_rgb(h):
    h=h[1:]
    return list(int(h[i:i+2], 16) for i in (0, 2, 4))

def darker(rgb_list):
    return tuple(np.multiply(rgb_list,0.40).astype(int))

def whiter(rgb_list):
    ret=[]
    for c in rgb_list:
        newc = min(255,c+150)
        ret.append(newc)
    return tuple(np.array(ret).astype(int))

def change_hex(h,f): 
    r = hex_to_rgb(h)
    return rgb_to_hex(f(r))
        


def get_time_windows(od):
    t300 = 19.5 + 6*(10-od)
    t100 = 59.5 + 8*(10-od)
    t50 = 99.5 + 10*(10-od)
    return [t50,t100,t300]




# https://osu.ppy.sh/help/wiki/Beatmapping/Approach_rate

def get_preempt_from_ar(ar):
    if ar<5:
        preempt = 1200 + 600 * (5 - ar) / 5
        fade_in = 800 + 400 * (5 - ar) / 5
    elif ar>5:
        preempt = 1200 - 750 * (ar - 5) / 5
        fade_in = 800 - 500 * (ar - 5) / 5
    else:
        preempt = 1200
        fade_in = 800
    return preempt,fade_in

def get_sliderbody_points( x,y, curve_type, list_of_points ,r ):
    ret_list = []
    
    
    if curve_type=='L' or curve_type=='P': #linear
        #assert len(list_of_points)==1
        x1,y1 = list_of_points[-1]
        
        dx=x1-x
        dy=y1-y
        distance= math.sqrt( dx*dx + dy*dy )

        slider_body_segment = Segment(x,y,x1,y1)

        for t in np.arange(0,1,0.02):
            xt,yt = slider_body_segment.at(t)
            
            xt1 = xt + (-dy)*float(r)/distance 
            xt2 = xt - (-dy)*float(r)/distance 

            yt1 = yt + (dx)*float(r)/distance 
            yt2 = yt - (dx)*float(r)/distance 

            ret_list.append( [xt1,yt1] )
            ret_list.append( [xt2,yt2] )

    if curve_type=='B': # Bézier
        L=[[x,y]] # sliderhead is also first bezier ctrl point
        
        for [xi,yi] in list_of_points:
            L.append([xi,yi])
  
        bezier_curve = Bezier(L)

        for t in np.arange(0,1,0.02):
            
            xt,yt = bezier_curve.at(t)

            dx,dy = bezier_curve.slope_vector_at(t) 
            distance = np.linalg.norm([dx,dy])

                        
            xt1 = xt + (-dy)*float(r)/distance 
            xt2 = xt - (-dy)*float(r)/distance 

            yt1 = yt + (dx)*float(r)/distance 
            yt2 = yt - (dx)*float(r)/distance 

            ret_list.append( [xt1,yt1] )
            ret_list.append( [xt2,yt2] )
            #ret_list.append( [xt,yt] )

    return ret_list

def parse_point(str_coords):
    x = int(str_coords.split(':')[0])
    y = int(str_coords.split(':')[1])
    return x,y

def draw_point(canvas,x,y,r,color):
    canvas.create_oval(x+X_OFF, y+Y_OFF, x+X_OFF, y+Y_OFF,fill='black',outline=color)

def triangle_function(x):
    if int(x)%2 == 0:
        y=x-int(x) 
    else:
        y=int(x)+1-x 
    return y

def angle_between(p1, p2):  #0--->2pi
    ang1 = np.arctan2(*p1[::-1])
    ang2 = np.arctan2(*p2[::-1])
    return (ang1 - ang2) % (2 * np.pi)



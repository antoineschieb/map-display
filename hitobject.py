import os
import numpy as np

from utils import parse_point

class HitObject:
    def __init__(self,x,y,time,type_str,objectParams=None):
        self.x = x
        self.y = y
        self.time = time
        self.type_str = type_str
        self.objectParams = objectParams
        self.is_part_of_stream = False

    def __str__(self):
        print('---Hit object description---')
        print('Type of object : '+self.type_str)
        print('x : '+str(self.x))
        print('y : '+str(self.y))
        print('mapped at : '+str(self.time) + ' ms')
        print('Additional data :')
        print(self.objectParams)
        print('stream??'+str(self.is_part_of_stream))
        return ''
    
    @classmethod
    def from_str(cls, hobj_str):
        L = hobj_str.split(',')
        x = int(L[0])
        y = int(L[1])
        time = int(L[2])
        typeint = int(L[3])

        if typeint & 1:
            # circle
            # no additional data needed
            return cls(x,y,time,'circle')

        if (typeint>>1) & 1:
            # slider
            d = dict()
            ## curve type
            curve = L[5]
            
            points = []  
            for s in L[5].split('|')[1:]:
                x_curve,y_curve = parse_point(s)
                points.append([x_curve,y_curve])
            
            d['curve'] = {
                'type' : curve[0], #first char 
                'points_list' : points
            }
            ##number of slides
            d['slides'] = int(L[6])
            ##visual length
            d['length'] = float(L[7])
            return cls(x,y,time,'slider', d)

        if (typeint>>3) & 1:
            # spinner
            d=dict()
            d['end_time'] = int(L[5])
            return cls(x,y,time,'spinner',d)

        raise Exception
    
        
    def flip_Y(self): #used for HR mod
        
        if self.type_str=='circle':
            self.y = 384 - self.y

        if self.type_str=='slider':
            self.y = 384 - self.y

            PL = self.objectParams['curve']['points_list']
            for i in range(len(PL)):
                self.objectParams['curve']['points_list'][i][1] = 384 - self.objectParams['curve']['points_list'][i][1]
                
        return self

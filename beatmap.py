import os
import numpy as np

from utils import get_hobj_str_list
from hitobject import HitObject
from parameters import BEATMAPS_PATH


class Beatmap:
    def __init__(self,metadata,cs,ar,od,slider_multiplier,slider_tick_rate,hit_objects_list):
        self.metadata = metadata
        self.cs = cs 
        self.ar = ar
        self.od = od
        self.slider_multiplier = slider_multiplier
        self.slider_tick_rate = slider_tick_rate
        self.hit_objects_list = hit_objects_list
        self.HRed=False
    
    @classmethod
    def from_osu_file(cls, osu_file_path):
        
        metadata = dict()
        with open(osu_file_path,'r') as f:
            for _, line in enumerate(f):
                if len(line.split(':')) > 1:
                    l = line.split(':')[1]

                if line.startswith('CircleSize:'):
                    cs = float(l)                    
                if line.startswith('ApproachRate:'):
                    ar = float(l)                
                if line.startswith('OverallDifficulty:'):
                    od = float(l)                
                if line.startswith('SliderMultiplier:'):
                    slider_multiplier = float(l)                
                if line.startswith('SliderTickRate:'):
                    slider_tick_rate = float(l)                
                
                if line.startswith('BeatmapID:'):
                    metadata['BeatmapID'] = int(l[:-1])                
                if line.startswith('Artist:'):
                    metadata['Artist'] = l[:-1]                
                if line.startswith('Title:'):
                    metadata['Title'] = l[:-1]                
                if line.startswith('Creator:'):
                    metadata['Creator'] = l[:-1]                
                if line.startswith('Version:'):
                    metadata['Version'] = l[:-1]

        hit_objects_list = []        
        for obj_str in get_hobj_str_list(osu_file_path):
            hit_objects_list.append(HitObject.from_str(obj_str))

        return cls(metadata,cs,ar,od,slider_multiplier,slider_tick_rate,hit_objects_list)

    def add_HR(self):
        assert not self.HRed 
        self.od = min(10,self.od*1.4)
        self.ar = min(10,self.ar*1.4)
        self.cs *= 1.3 #maybe fix very high cs cap

        for i in range(len(self.hit_objects_list)):
            self.hit_objects_list[i] = self.hit_objects_list[i].flip_Y()
        
        self.HRed=True
        return self


    def add_DT(self):
        raise NotImplementedError



    def look_for_spaced_streams(self,bpm,spacing_factor):
        circle_radius_px = int((109 - 9 * self.cs)/2)
        for i in range(len(self.hit_objects_list)-1):
            self.hit_objects_list[i].is_part_of_stream = False
            current = self.hit_objects_list[i]
            next_one = self.hit_objects_list[i+1]

            if current.type_str == next_one.type_str == 'circle':
                if next_one.time - current.time <= (15000/bpm)*1.03: #3% margin error
                    if np.linalg.norm([ next_one.x - current.x , next_one.y - current.y ]) >= circle_radius_px*spacing_factor:
                        self.hit_objects_list[i].is_part_of_stream = True

        return self






    def __str__(self):
        print('---Beatmap Info---')
        print( self.metadata['Artist'] + ' - ' + self.metadata['Title'] + ' [' + self.metadata['Version'] +']' )
        print('CS : '+str(self.cs))
        print('AR : '+str(self.ar))
        print('OD : '+str(self.od))
        print('slider speed multiplier : '+str(self.slider_multiplier))
        print('slider tick rate : '+str(self.slider_tick_rate))
        print('number of hit objects : '  + str(len( self.hit_objects_list )) )
        return ''




def get_beatmap_object_from_ID(bid):
    for dirname in os.scandir(BEATMAPS_PATH):
        
        if os.path.isdir(os.path.join(BEATMAPS_PATH,dirname)):
            for entry in os.scandir( os.path.join(BEATMAPS_PATH,dirname)):
        
                if entry.path.endswith('.osu'):
                    
                    try:
                        b=Beatmap.from_osu_file(entry.path)
                        bbid = b.metadata['BeatmapID']
                        if bbid == bid:
                            return b 
                    except:
                        continue

                    
    
    return None
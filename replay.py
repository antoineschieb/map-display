import numpy as np
import math
import cmath
import json
import tkinter as tk

import beatmap 
from utils import get_time_windows, angle_between


class Replay:

    def __init__(self,metadata,txy):
        self.metadata = metadata
        self.txy = txy 


    @classmethod
    def from_json(cls,json_file_path):
        return cls(get_metadata(json_file_path),get_txy(json_file_path))


    def get_spaced_streams_clicks(self,beatmap):
        off = self.metadata['cursor_time_offset']
        circle_radius_px = int((109 - 9 * beatmap.cs)/2)

        complex_points=[]
        [time_window_50,time_window_100,time_window_300] = get_time_windows(beatmap.od)
        for h_o_i in range(len(beatmap.hit_objects_list)-1) :
            h_o = beatmap.hit_objects_list[h_o_i]
            h_o_next = beatmap.hit_objects_list[h_o_i+1]
            if h_o.is_part_of_stream:
                direction_vector = [h_o_next.x - h_o.x , h_o_next.y - h_o.y ]
                norm = np.linalg.norm(direction_vector)
                direction_vector = np.multiply( circle_radius_px / norm, direction_vector)
                closest_time = time_window_50
                for i in range(1,len(self.txy)):
                    t = self.txy[i][0]
                    
                    if t+off<h_o.time-time_window_50:
                        continue #too early for this circle
                    if t+off>h_o.time+time_window_50:
                        continue #too late for this circle
                    if (self.txy[i][-1] == self.txy[i-1][-1] ) and (self.txy[i][-2] == self.txy[i-1][-2]): 
                        continue #not a click

                    timedelta = (t+off) - h_o.time
                    
                    if abs(timedelta) < closest_time:
                        
                        closest_time = abs(timedelta)
                        registered = [self.txy[i][1],self.txy[i][2]]

                        off_aim = np.subtract(registered,[h_o.x,h_o.y])
                        dist_from_center =np.linalg.norm(off_aim) / circle_radius_px
                        angle = angle_between(off_aim,direction_vector)
                if dist_from_center<=1:
                    complex_points.append([dist_from_center,angle])
        
        return complex_points

def get_metadata(json_file_path):
    with open(json_file_path) as json_data:
        data = json.load(json_data)

    metadata = dict()
    metadata['beatmapMD5'] = data['beatmapMD5']
    metadata['player'] = data['playerName']
    metadata['mods'] = parse_mods(int(data['mods']))
    metadata['score'] = data['score']
    metadata['max_combo'] = data['max_combo']
    metadata['timestamp'] = data['timestamp']
    metadata['cursor_time_offset'] = int(data['replay_data'][1]['timeSinceLastAction']) + int(data['replay_data'][2]['timeSinceLastAction'])
   
    return metadata


def get_txy(json_file_path):

    with open(json_file_path) as json_data:
        data = json.load(json_data)

    CL = data["replay_data"]

    txy = np.array([[0,0,0,0,0,0,0]])
    flag_started = False
    sample=0
    for d in CL:
        
        delta_t = d['timeSinceLastAction']
        if  not flag_started and int(d['x'])!=256 and int(d['x'])!=-500  :
            flag_started = True
            continue

        if not flag_started:
            continue

        if delta_t == -12345:
            break  

        
        if delta_t>0:
            dist = math.sqrt(( d['x'] - txy[sample,1])**2 + ( d['y'] - txy[sample,2])**2 )
            inst_speed = dist / delta_t #pixels / ms (?)

            key1 = -int(d['keysPressed']['K2']) #bug in json parser, k2=k1
            key2 = -int(d['keysPressed']['M1']) #bug in json parser, m1=k2

            adding= np.array([[delta_t + txy[sample,0] , d['x'], d['y'] , dist, inst_speed , key1, key2 ]])
            txy=np.append(txy, adding  , axis=0  )
            sample+=1


    return txy 


def parse_mods(mods_int):
    L=[]
    if (mods_int>>0)&1:
        L.append('NF')

    if (mods_int>>1)&1:
        L.append('EZ')

    if (mods_int>>2)&1:
        L.append('TD')

    if (mods_int>>3)&1:
        L.append('HD')

    if (mods_int>>4)&1:
        L.append('HR')

    if (mods_int>>5)&1:
        L.append('SD')

    if (mods_int>>6)&1:
        L.append('DT')

    if (mods_int>>7)&1:
        L.append('RX')

    if (mods_int>>8)&1:
        L.append('HT')

    if (mods_int>>9)&1:
        L.remove('DT')
        L.append('NC')

    if (mods_int>>10)&1:
        L.append('FL')

    if (mods_int>>11)&1:
        L.append('AO')

    if (mods_int>>12)&1:
        L.append('SO')

    if (mods_int>>13)&1:
        L.append('AP')

    if (mods_int>>14)&1:
        L.append('PF')

    if L==[]:return 'Nomod'
    
    ret_str = ''    
    for x in L:
        ret_str += f'{x}, '

    return ret_str[:-2]



def view_hits(beatmap,replay,bpm):
    map_metadata = beatmap.metadata 
    replay_metadata = replay.metadata

    bc_r = 300 #bigcircle radius
    sc_r = 3 # smallcircle radius

    def get_xy(polar_coords):
        r=polar_coords[0]
        theta=polar_coords[1]
        i = complex(0,1)
        z = r*cmath.exp(i*theta)
        return [bc_r *z.real , bc_r *z.imag]

    def update_spacing(event):
        cnv.delete('dots')
        update_screen(0)


    def update_screen(event):
        beatmap.look_for_spaced_streams(bpm, spacing.get() )
        L = replay.get_spaced_streams_clicks(beatmap)
        count=0
        forward_hits=0
        backward_hits=0
        sum_x = 0
        mean_x = 0
        for point in L:
            [x,y]=get_xy(point)
            if x>0:forward_hits+=1
            if x<0:backward_hits+=1
            sum_x +=x

            cnv.create_oval(400+x-sc_r,400+y-sc_r,400+x+sc_r,400+y+sc_r,fill='red',tags='dots')
            count+=1
        
        if count>0:
            mean_x = sum_x/(count*bc_r)
        dots_count_var.set('Hits shown : ' +str(count))
        back_forw.set(f'{backward_hits} | {forward_hits} -----> mean x : {mean_x}')
        

    customcircle=tk.Tk()
    customcircle.title('Hits on most spaced circles')


    p  = f"Player : {replay_metadata['player']}"
    ma = f"Map : {map_metadata['Artist']} - {map_metadata['Title']} [{map_metadata['Version']}] "
    mo = f"Mods : +{replay_metadata['mods']} "
    l1 = tk.Label(text=p+'\n'+ma+'\n'+mo)
    
    dots_count_var = tk.StringVar(value='Hits shown : 0')
    l2 = tk.Label(textvariable=dots_count_var)
    
    back_forw = tk.StringVar(value='0 | 0')
    l3 = tk.Label(textvariable=back_forw)
    spacing = tk.DoubleVar()
    spacing.set(3.0)



    cnv = tk.Canvas(customcircle, width = 800, height = 800,bg='black')
    cnv.create_oval(400-bc_r,400-bc_r,400+bc_r,400+bc_r,fill='#202020',outline='#ffffff',width=2)
    cnv.create_oval(400-10,400-10,400+10,400+10,fill='white')
    cnv.create_oval(1050-bc_r,400-bc_r,1050+bc_r,400+bc_r,fill='#202020',outline='#ffffff',width=2)
    cnv.create_oval(-250-bc_r,400-bc_r,-250+bc_r,400+bc_r,fill='#202020',outline='#ffffff',width=2)
    cnv.create_line(50,750,750,750, fill='red', arrow='last', width=5)
    
    spacing_slide = tk.Scale(customcircle, variable=spacing, from_=1.5, to=3.5, resolution=0.01, orient=tk.HORIZONTAL, length=600,command=update_spacing)

    l1.pack()
    cnv.pack()
    l2.pack()
    spacing_slide.pack()
    l3.pack()

    


    customcircle.mainloop()

    return 
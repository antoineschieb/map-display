import os
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import math 
from beatmap import Beatmap
from utils import get_preempt_from_ar, rgb_to_hex, get_sliderbody_points, draw_point, parse_point, Segment, \
                  Bezier, triangle_function, darker, whiter, change_hex

from parameters import X_OFF, Y_OFF, PREEMPT_MULTIPLIER, CURSOR_BASE_SIZE, CURSOR_TRAIL_TIME, POST_DEATH, PLAY_STEP, \
    CURSORS_COLORS, CLICK_SIZE_MULTIPLIER





def draw_hitcircle(canvas,life_completion,x,y,r,draw_ac,colr='nn'):
    # hit circle

    val = int(255 * (life_completion))
    outline_color = rgb_to_hex((val,val,val))

    val_fill = int(127 * (life_completion))
    fill_color = rgb_to_hex((val_fill,val_fill,val_fill))

    if life_completion>1.0:
        fill_color=''
        outline_color = '#353535'
        r+=5
    
    if colr=='red':
        outline_color='red'

    canvas.create_oval(x-r+X_OFF, y-r+Y_OFF, x+r+X_OFF, y+r+Y_OFF , width=3,fill=fill_color,outline=outline_color)
    
    if draw_ac and life_completion<=1.0:
        # approach circle

        x0 = x - r - 3*r*(1-life_completion)
        y0 = y - r - 3*r*(1-life_completion)
        x1 = x + r + 3*r*(1-life_completion)
        y1 = y + r + 3*r*(1-life_completion)
        
        canvas.create_oval(x0+X_OFF, y0+Y_OFF, x1+X_OFF, y1+Y_OFF ,width=3,fill='',outline=outline_color)

    return 

def draw_slider(canvas, circle_life_completion, sliderball_life_completion,  x , y , r, curve_type, curve_points, slides,draw_ac ): #length????????????????????
   
    if 0<= circle_life_completion <= 1:
        val = int(255 * (circle_life_completion))
        outline_color = rgb_to_hex((val,val,val))
        
        # draw head 
        draw_hitcircle(canvas,circle_life_completion,x,y,r,draw_ac)
       
        # draw body 
        points_of_body = get_sliderbody_points( x,y, curve_type, curve_points , r )
        for xx,yy in points_of_body:
            draw_point(canvas,xx,yy,r,outline_color)

        # draw sliderqueue
        xq,yq = curve_points[-1] 
        canvas.create_oval(xq - r +X_OFF, yq - r+Y_OFF, xq + r +X_OFF, yq + r+Y_OFF ,  width=3,fill='',outline=outline_color)


    if 0<sliderball_life_completion<=1 :
        # draw head 
        canvas.create_oval(x - r +X_OFF, y - r +Y_OFF, x + r +X_OFF, y + r+Y_OFF , width=3,fill='',outline='white')     #todo: fix fill   
        
        # draw body 
        points_of_body = get_sliderbody_points( x,y, curve_type, curve_points , r )
        for xx,yy in points_of_body:
            draw_point(canvas,xx,yy,r,'white')

        # draw sliderqueue
        xq,yq = curve_points[-1]
        canvas.create_oval(xq - r+X_OFF, yq - r +Y_OFF, xq + r+X_OFF, yq + r +Y_OFF,width=3,fill='',outline='white')

        #draw sliderball 
        if curve_type=='L':seg = Segment(x,y,xq,yq)
        if curve_type=='B':
            L=[[x,y]] # sliderhead is also first bezier ctrl point
            for [xi,yi] in curve_points:
                L.append([xi,yi])
            seg = Bezier(L)

        if curve_type=='P': #TODO : dpfsfsf
            seg = Segment(x,y,xq,yq)

        xt,yt = seg.at(triangle_function(sliderball_life_completion * slides))
        canvas.create_oval(xt - r+X_OFF, yt - r +Y_OFF, xt + r+X_OFF, yt + r +Y_OFF,fill='#808080',outline='')

    return 

def draw_spinner(canvas,life_completion):
    # static circle
    x0 = 256 - 150
    y0 = 192 - 150
    x1 = 256 + 150
    y1 = 192 + 150

    canvas.create_oval(x0+X_OFF, y0+Y_OFF, x1+X_OFF, y1+Y_OFF,fill='',outline='white')

    # dynamic circle
    x0 = 256 - 150*(1-life_completion)
    y0 = 192 - 150*(1-life_completion)
    x1 = 256 + 150*(1-life_completion)
    y1 = 192 + 150*(1-life_completion)

    canvas.create_oval(x0+X_OFF, y0+Y_OFF, x1+X_OFF, y1+Y_OFF,fill='',outline='blue', width = 4)


    return 


def draw_hit_objects(canvas, time, beatmap, draw_ac):
    
    preempt,fade_in = get_preempt_from_ar(beatmap.ar)
    preempt *= PREEMPT_MULTIPLIER
    
    circle_radius_px = int((109 - 9 * beatmap.cs)/2)

    for hit_object in reversed(beatmap.hit_objects_list):
        
        
        #print(hit_object.time - preempt)

        if hit_object.type_str=='circle' and hit_object.time - preempt <= time <= hit_object.time + POST_DEATH:
            
            life_completion = float((time-(hit_object.time - preempt)) / (preempt))

            if hit_object.type_str=='circle':
                if hit_object.is_part_of_stream:
                    colr='red'
                else:
                    colr='nn'
                draw_hitcircle(canvas, life_completion, hit_object.x, hit_object.y, circle_radius_px, draw_ac, colr=colr)
        
        if hit_object.type_str=='slider':
            sliderball_time = (4.5/beatmap.slider_tick_rate) * hit_object.objectParams['slides']  * hit_object.objectParams['length']  / beatmap.slider_multiplier
            if hit_object.time - preempt <= time <= hit_object.time + sliderball_time :  
            
                circle_life_completion = float((time-(hit_object.time - preempt)) / (preempt))
                sliderball_life_completion = (time - hit_object.time) / sliderball_time

                draw_slider(canvas,circle_life_completion, sliderball_life_completion, hit_object.x, hit_object.y, circle_radius_px, \
                            hit_object.objectParams['curve']['type'], hit_object.objectParams['curve']['points_list'], \
                            hit_object.objectParams['slides'],draw_ac)

        if hit_object.type_str=='spinner' and hit_object.time <= time <= hit_object.objectParams['end_time']:
            life_completion = float((time-hit_object.time)/(hit_object.objectParams['end_time'] - hit_object.time)) 
            draw_spinner(canvas,life_completion)

    return 


def draw_cursor(root,canvas,time,replay,main_color,show_clicks_bool):

    time_offset = replay.metadata['cursor_time_offset']
    old_key1=False
    old_key2=False

    #color_click = change_hex(main_color,whiter)
    #color_idle = change_hex(main_color,whiter)
    color_idle = main_color
    color_click = main_color
    #color_idle = '#21a40f'



    for i in range(replay.txy.shape[0]):
        t,x,y,_,speed,key1,key2 = replay.txy[i,:]
        is_clicking=False

        if bool(not old_key1 and key1) ^ bool(not old_key2 and key2):
            is_clicking=True
            colr = color_click
            click_mult = CLICK_SIZE_MULTIPLIER * (time - (t+time_offset))
        else:
            colr= color_idle
            click_mult = 1.0

        if time-CURSOR_TRAIL_TIME < t+time_offset < time:
            time_delta = (time - (t+time_offset))
            
            r = 1 + CURSOR_BASE_SIZE * click_mult *(math.pow(CURSOR_TRAIL_TIME,1./4)-math.pow(time_delta,1./4))/math.pow(CURSOR_TRAIL_TIME,1./4)
            r=int(r)
            
            if is_clicking and show_clicks_bool==1:
                r=6
                canvas.create_oval(x-r+X_OFF, y-r+Y_OFF, x+r+X_OFF, y+r+Y_OFF,fill='yellow', outline=color_click, width=int(r/3))
            else:
                r=6
                alp=0.4
                create_rgba_rect(root,canvas,round(x-r+X_OFF), round(y-r+Y_OFF), round(x+r+X_OFF), round(y+r+Y_OFF), fill=colr, alpha=alp)
            
            #canvas.create_oval(x-r+X_OFF, y-r+Y_OFF, x+r+X_OFF, y+r+Y_OFF,width=int(r/5),fill=colr,outline=colr)

        old_key1 = key1
        old_key2 = key2

    return



def draw_screen(beatmap,replays):

    root = tk.Tk()
    root.geometry('1921x1061') 
    v=tk.DoubleVar()
    playback_bool = tk.IntVar()
    playback_speed= tk.DoubleVar()
    show_clicks_bool = tk.IntVar(value=1)
    show_hitobjs_bool = tk.IntVar(value=1)
    show_acs_bool = tk.IntVar(value=1)
    root.title('osu! replay viewer')

    def next_action(m=1):
        v.set(v.get()+PLAY_STEP*m)
        update_screen('')
        

    def update_v():        
        if playback_bool.get()==1:
            v.set(v.get()+int(playback_speed.get()))
            update_screen(0)
            root.after(1, update_v)

    def update_screen(event):
        play_area.delete("all")

        if show_hitobjs_bool.get()==1:
            draw_hit_objects(play_area,v.get(),beatmap,show_acs_bool.get())
        
        i=0
        for replay in replays:
            draw_cursor(root,play_area,v.get(),replay,CURSORS_COLORS[i],show_clicks_bool.get())
            i+=1


    beatmap_metadata_indicator = tk.Label(font=("Courier", 24), text=f"{beatmap.metadata['Artist']} - {beatmap.metadata['Title']} [{beatmap.metadata['Version']}]")
    
    replay_metadata_indicators=[]
    for replay in replays:
        i=replays.index(replay)
        replay_metadata_indicators.append(tk.Label(foreground=CURSORS_COLORS[i],text=f"Played by: {replay.metadata['player']}\nSubmitted on {replay.metadata['timestamp'].split('T')[0]}, at {replay.metadata['timestamp'].split('T')[1][:-5]} \nmods: +{replay.metadata['mods']} " ))

        
    prev_frame=tk.Button(root,text='<<< previous frame <<<', command= lambda : next_action(-1))
    next_frame=tk.Button(root,text='>>> next frame >>>', command= lambda : next_action(1))
    auto_play_check = tk.Checkbutton(text='Auto playback', variable=playback_bool, command= update_v, font=("Arial", 16) )
    show_clicks_check = tk.Checkbutton(text='Show clicks', variable=show_clicks_bool, font=("Arial", 16),command=lambda:update_screen(0) ) 
    show_objs_check = tk.Checkbutton(text='Show hit objects', variable=show_hitobjs_bool, font=("Arial", 16),command=lambda:update_screen(0) ) 
    show_acs_check = tk.Checkbutton(text='Show approach circles', variable=show_acs_bool, font=("Arial", 16),command=lambda:update_screen(0) ) 

    playback_slider = tk.Scale(root, variable=playback_speed, from_=1, to=50, orient=tk.HORIZONTAL, length=350)
    


    screen = tk.Frame(root,bd=20,bg='#c4c4c4')
    play_area = tk.Canvas(screen, width = 512+2*X_OFF, height = 384+2*Y_OFF,bg='black') #512x384 play area


    tmax = beatmap.hit_objects_list[-1].time
    w = tk.Scale(root, variable=v, from_=00000, to=tmax, orient=tk.HORIZONTAL, length=1900,command=update_screen)
    
    ##### packs
    beatmap_metadata_indicator.pack()
    
    for i in range(len(replay_metadata_indicators)):
        if i==0:
            s=tk.LEFT
        if i==1:
            s=tk.RIGHT
        
        replay_metadata_indicators[i].pack(side=s)
        #mods_indicators[i].pack(side=s)
    
    
    play_area.pack()
    screen.pack()
    
    prev_frame.pack()
    next_frame.pack()
    auto_play_check.pack()
    playback_slider.pack()
    w.pack()
    show_clicks_check.pack()
    show_objs_check.pack()
    show_acs_check.pack()
    root.mainloop()




images = []  # to hold the newly created image

def create_rgba_rect(root,canvas,x1, y1, x2, y2, **kwargs): 
    alpha = int(kwargs.pop('alpha') * 255)
    fill = kwargs.pop('fill')
    fill = root.winfo_rgb(fill) + (alpha,)
    image = Image.new('RGBA', (x2-x1, y2-y1) )
    draw = ImageDraw.Draw(image)
    draw.ellipse((0, 0, x2-x1, y2-y1), fill = fill)
  
    images.append(ImageTk.PhotoImage(image))
    canvas.create_image(x1, y1, image=images[-1], anchor='nw')








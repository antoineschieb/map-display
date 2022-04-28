from draw import draw_screen
from beatmap import Beatmap
from replay import Replay
from parameters import APIKEY, BEATMAPS_PATH
from beatmap import get_beatmap_object_from_ID
from replay import view_hits


import os 
import requests
import tkinter as tk
from tkinter import filedialog
import easygui

replay_paths=[]
text_var = 'Imported replays : \n'

root1 = tk.Tk()
root1.geometry('1300x200')
root1.title('Add replays')


def add_replay_file(replay_paths):
    global text_var
    chosen_replay_path = filedialog.askopenfilename(
        initialdir= '/home/antoines/Escritorio/perso/osu_r_p/map-display/replays_jsons',
        title= "Select a replay json:",
        filetypes=(("JSON Files", "*.json"),)
    )                                   
                                    

    try:
        text_var += chosen_replay_path + ' \n'
    except:
        pass
    replay_paths.append(chosen_replay_path)
    l1.configure(text=text_var)

def skip():
    global replay_paths
    replay_paths=["/home/antoines/Escritorio/perso/osu_r_p/map-display/replays_jsons/Besta - Kanpyohgo - Unmei no Dark Side -Rolling Gothic mix [FreeSongs' Rolling Hell] (2020-08-07).json","/home/antoines/Escritorio/perso/osu_r_p/map-display/replays_jsons/Yaong - Kanpyohgo - Unmei no Dark Side -Rolling Gothic mix [FreeSongs' Rolling Hell] (2017-10-28).json"]
    root1.destroy()

def go():
    root1.destroy()

l1=tk.Label(text='Imported replays : \n')
b1=tk.Button(text='Add a replay file', command=lambda:add_replay_file(replay_paths),font=('Arial',34))

b2=tk.Button(text='Go!', command=go,font=('Arial',34))

b3=tk.Button(text='Skip', command=skip,font=('Arial',34))

l1.grid(row=1,columnspan=3)
b1.grid(row=2,column=1)
b2.grid(row=2,column=2)
b3.grid(row=3,columnspan=3)
root1.mainloop()

replays_list=[]
for r in replay_paths:
    replays_list.append(Replay.from_json(r))

MD5=replays_list[0].metadata['beatmapMD5']
req = f'https://osu.ppy.sh/api/get_beatmaps?k={APIKEY}&h={MD5}'


bpm = float(requests.get(req).json()[0]['bpm'])
if bpm<=100:bpm*=2
bid = int(requests.get(req).json()[0]['beatmap_id'])
beatmap = get_beatmap_object_from_ID(bid)
#beatmap.look_for_spaced_streams(bpm,2.0)

if beatmap is None:
    print('Beatmap not found in provided folder')

if 'HR' in replays_list[0].metadata['mods'] :
    beatmap = beatmap.add_HR()



for r in replays_list:
    hits = r.get_spaced_streams_clicks(beatmap)

    

    view_hits(beatmap,r,bpm)
    

draw_screen(beatmap, replays_list)
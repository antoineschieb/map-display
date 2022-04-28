import glob
import os
import sys

def transform_last_n_replays(n):
    jsfile_path = '/home/antoines/Escritorio/perso/osu_r_p/osuReplayParser/tests/test-suite.js'
    list_of_files = glob.glob('/home/antoines/Escritorio/perso/drive_c/osu/Replays/*.osr') # * means all if need specific format then *.csv
    selected_files = sorted(list_of_files, key=os.path.getctime)[-n:]
    for osr_path in selected_files:
        print('-------------------------------------------------------------------------------------------------------')
        future_json_path = '/home/antoines/Escritorio/perso/osu_r_p/map-display/replays_jsons/' + osr_path.split('/')[-1][:-8] + '.json'
        print('[PYTHON]: Will try to export    '+ osr_path)
        os.system('nodejs ' + jsfile_path + ' "' + osr_path + '" "' + future_json_path + '"')
    return 0

transform_last_n_replays(int(sys.argv[1]))

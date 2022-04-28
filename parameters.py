with open('/home/antoines/Escritorio/perso/secret_apikey/apikey.txt','r') as f:
    APIKEY = f.read()[:-1]

#GENERAL
#BEATMAPS_PATH_old='/home/antoines/Escritorio/perso/osu_r_p/map-display/beatmaps'
BEATMAPS_PATH = '/home/antoines/Escritorio/perso/drive_c/osu/Songs'
# SCREEN
X_OFF = 190
Y_OFF = 150

# AR +-
PREEMPT_MULTIPLIER = 1.5

# CURSOR
CURSOR_TRAIL_TIME = 380
CURSOR_BASE_SIZE = 5
CLICK_SIZE_MULTIPLIER = 1.6
CURSORS_COLORS = ['#ff0000','#0000ff','#00ff00','#fff000','#000fff','#f0ff00']


# CIRCLES
POST_DEATH = 300

#REPLAY BUTTONS
PLAY_STEP = 16
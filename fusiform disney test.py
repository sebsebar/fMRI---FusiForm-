from __future__ import division
from psychopy import core, visual, event, gui, monitors, event
import pyglet
import time
import ppc
import pandas as pd #import module to handle log file data frame 
from random import sample

#MIKKEL DID NOT IMPORT THESE!! 
#import module that fetch file names
import glob

#import module that makes it possible to randomize the order of stimuli 
from random import randint

"""
SET VARIABLES
"""
# Monitor parameters
MON_DISTANCE = 60  # Distance between subject's eyes and monitor 
MON_WIDTH = 34  # Width of your monitor in cm
MON_SIZE = [1440, 900]  # Pixel-dimensions of your monitor
FRAME_RATE= 60 # Hz
SAVE_FOLDER = 'fusiform_disney_data'  # Log is saved to this folder. The folder is created if it does not exist.

# Intro-dialogue. Get subject-id and other variables.
# Save input variables in "V" dictionary (V for "variables")
V= {'ID':'','age':'','gender':['male','female'],'Scanner':['Trio','Scyra'],'Scan day': ['Tuesday','Wednesday']}
if not gui.DlgFromDict(V, order=['ID', 'age', 'gender','Scanner','Scan day']).OK: # dialog box; order is a list of keys 
    core.quit()

"""
SPECIFY TIMING AND MONITOR
"""
# Clock and timer
clock = core.Clock() 

# Create psychopy window
my_monitor = monitors.Monitor('testMonitor', width=MON_WIDTH, distance=MON_DISTANCE)  # Create monitor object from the variables above. This is needed to control size of stimuli in degrees.
my_monitor.setSizePix(MON_SIZE)
win = visual.Window(monitor=my_monitor, units='deg', fullscr=True, allowGUI=False, color='black')  # Initiate psychopy Window as the object "win", using the myMon object from last line. Use degree as units!

#Prepare Fixation cross
stim_fix = visual.TextStim(win, '+')#, height=FIX_HEIGHT)

"""
STIMULI
"""
image_ff = glob.glob('ff_*.jpg') 
image_nff = glob.glob('nff_*.jpg') 
image_fc = glob.glob('fc_*.jpg') 
image_nfc = glob.glob('nfc_*.jpg') 

#add image files as a string of list (not use , and () because then it is a list of lists)  
images = image_ff + image_nfc + image_fc + image_nff

delays=(156,206,286,366)# different time intervals between stimuli mean 4.1 sec x 60 hz refresh rate =246, in order to make less predictable and increase power.
REPETITIONS = 2 # 60 different images * 4 time delays * 2 repetitions = 120 trials
dur=int(0.7*FRAME_RATE) # duration in seconds multiplied by 60 Hz and made into integer
condition='disney_exp' #Just a variable. If the script can run several exp. then this can be called in GUI. Not relevant here.
nr_trials = len(images)*REPETITIONS

# The image size and position using ImageStim, file info added in trial list sbelow.
stim_image = visual.ImageStim(win,  # you don't have to use new lines for each attribute, but sometime it's easier to read that way
     mask=None,
    pos=(0.0, 0.0),
    size=(14.0, 10.5),
    ori=1)

"""
KEYS
"""

#important keys
KEYS_QUIT = 'escape'  # Keys that quits the experiment
KEYS_trigger=['t'] # The MR scanner sends a "t" to notify that it is starting
   # Prepare a csv log-file using the ppc script
writer = ppc.csvWriter(str(V['ID']), saveFolder=SAVE_FOLDER)  # writer.write(trial) will write individual trials with low latency


""" DO NOT KNOW HOW TO DO THIS """
def make_trial_list(condition):
#Factorial design
    trial_list = []
    
    delay_list = int(nr_trials/len(delays)) * delays
    delay_list = sample(delay_list, nr_trials)
    c = -1 
    for image in images: # images
        for rep in range(REPETITIONS):
                c = c + 1
            # Add a dictionary for every trial
                trial_list += [{
                    'ID': V['ID'],
                    'age': V['age'],
                    'gender': V['gender'],
                    'scan day':V['Scan day'],
                    'scanner':V['Scanner'],
                    'condition': condition,
                    'img': image, #image file
                    'onset':'' ,# a place to note onsets
                    'offset': '',
                    'duration_measured':'',
                    'duration_frames': dur,
                    'delay_frames' : delay_list[c],
                    'response': '',
                    'rt': '',
                    'key_t':'',
                    'KEYS_QUIT': '',
                    }]
                    

   # Randomize order
    trial_list = sample(trial_list, len(trial_list))

    # Add trial numbers and return
    for i, trial in enumerate(trial_list):
        trial['no'] = i + 1  # start at 1 instead of 0
        if i is 0:
            writer.writeheader(trial) # An added line to give headers to the log-file (see ppc.py)
    return trial_list

    
def run_condition(condition):
    """
    Runs a block of trials. This is the presentation of stimuli,
    collection of responses and saving the trial
    """
    # Loop over trials
    for trial in make_trial_list(condition):
        event.clearEvents(eventType='keyboard')# clear keyboard input to make sure that no responses are logged that do not belong to stimulus
        # Prepare image 
        stim_image.image = trial['img']

        # Display image and monitor time
        time_flip=core.monotonicClock.getTime() #onset of stimulus
        for frame in range(trial['duration_frames']):
            stim_image.draw()
            win.flip()
 
        # Display fixation cross
        offset = core.monotonicClock.getTime()  # offset of stimulus
        for frame in range(trial['delay_frames']):
            stim_fix.draw()
            win.flip()
            # Get actual duration at offset
                   

        #Log values
        trial['onset']=time_flip-exp_start
        trial['offset'] = offset-exp_start
        trial['duration_measured']=offset-time_flip

        try:
            key, time_key = event.getKeys(keyList=('y','b','escape'), timeStamped=True)[0]# timestamped according to core.monotonicClock.getTime() at keypress. Select the first and only answer.

        except IndexError:  #if no responses were given, the getKeys function produces an IndexError
            trial['response']=''
            trial['key_t']=''
            trial['rt']=''
         
        else: #if responses were given, find RT and correct responses
            trial['response']=key
            trial['key_t']=time_key-exp_start
            trial['rt'] = time_key-time_flip

        # Save trials to csv file
        writer.write(trial) 
        

"""
DISPLAY INTRO TEXT AND AWAIT SCANNER TRIGGER
"""    
textPos= [0, 0]                            # Position of question message
textHeight=0.75 # height in degrees
introText1=[u'In this experiment you have to look at pictures', # some blanks here to create line shifts
                    u'',
                    u'Press  button with INDEX finger',
                    u'if you recognize the face',
                    u'',
                    u'Press button with MIDDLE finger',
                    u'if you do not recognize the face',
                    u'',
                    u'Please stay awake. :-)']

# Loop over lines in Intro Text1
ypos=4
xpos=0
for intro in introText1:
    ypos=ypos-1
    introText1 = visual.TextStim(win=win, text=intro, pos=[xpos,ypos], height=textHeight, alignHoriz='center')
    introText1.draw()
win.flip()          # Show the stimuli on next monitor update and ...

#At the end add this!! 
#Wait for scanner trigger "t" to continue
event.waitKeys(keyList= KEYS_trigger) 
exp_start=core.monotonicClock.getTime()

""" CALL FUNCTION RUNNING THE EXPERIMENTAL LOOP"""

run_condition('disney_exp')
from __future__ import print_function
from __future__ import division
__author__ = """Alex "O." Holcombe""" ## double-quotes will be silently removed, single quotes will be left, eg, O'Connor
from psychopy import *
import psychopy.info
from psychopy import sound, monitors, logging
import numpy as np
import itertools #to calculate all subsets
from copy import deepcopy
from math import atan, pi, cos, sin, sqrt, ceil, atan2, log
import time, sys, platform, os, gc, random, shutil
eyetrackingOption = False #Include this so can turn it off, because Psychopy v1.83.01 mistakenly included an old version of pylink which prevents EyelinkEyetrackerForPsychopySUPA3 stuff from importing
if eyetrackingOption:
    from EyelinkEyetrackerForPsychopySUPA3 import Tracker_EyeLink #Chris Fajou integration
from helpersAOHtargetFinalCueLocatn import accelerateComputer, openMyStimWindow, constructThickThinWedgeRingsTargetAndCue
eyetracking = False# False if practice, else true.
getEyeTrackingFileFromEyetrackingMachineAtEndOfExperiment = False #If True, can take up to 1.5 hrs in certain conditions

quitFinder = False #debugON
if quitFinder:
    applescript="\'tell application \"Finder\" to quit\'" #quit Finder.
    shellCmd = 'osascript -e '+applescript
    os.system(shellCmd)
process_priority = 'realtime' # 'normal' 'high' or 'realtime'
disable_gc = True

subject='test'#'test'
autoLogging = False
demo = False
autopilot=True
if autopilot:  subject='auto'
feedback=True
exportImages= False #quits after one trial / output image
screenshot= False; screenshotDone = False;allowGUI = False;waitBlank = False
trackAllIdenticalColors = True#with tracking, can either use same colors as other task (e.g. 6 blobs but only 3 colors so have to track one of 2) or set all blobs identical color

seed = int( np.floor( time.time() ) )
random.seed(seed); np.random.seed(seed) #https://stackoverflow.com/a/48056075/302378
savingForEventualLog = list()
savingForEventualLog.append("Random seed:" + str(seed))

timeAndDateStr = time.strftime("%d%b%Y_%H-%M", time.localtime()) 
respTypes=['order']; respType=respTypes[0]
bindRadiallyRingToIdentify=1 #0 is inner, 1 is outer
gratingTexPix=1024#numpy textures must be a power of 2. So, if numColorsRoundTheRing not divide without remainder into textPix, there will be some rounding so patches will not all be same size
premask = False
numRings=2
radii=[25]   #Need to encode as array for those experiments wherein more than one ring presented 

respRadius=radii[0] #deg
refreshRate= 85 #85 #set to the framerate of the monitor
useClock = False #as opposed to using frame count, which assumes no frames are ever missed
fullscr=True; #show in small window (0) or full screen (1) 
scrn=0 #which screen to display the stimuli. 0 is home screen, 1 is second screen (cv: sometimes the other way around)
# create a dialog from dictionary 
infoFirst = { 'Autopilot':autopilot, 'Check refresh etc':False, 'Screen to use':scrn, 'Fullscreen (timing errors if not)': fullscr, 'Screen refresh rate': refreshRate }
OK = gui.DlgFromDict(dictionary=infoFirst, 
    title='MOT', 
    order=['Autopilot','Check refresh etc', 'Screen to use', 'Screen refresh rate', 'Fullscreen (timing errors if not)'], 
    tip={'Check refresh etc': 'To confirm refresh rate and that can keep up, at least when drawing a grating',
            'Screen to use': '0 means primary screen, 1 means second screen'},
    )
if not OK.OK:
    print('User cancelled from dialog box'); savingForEventualLog.append('User cancelled from dialog box'); core.quit()
autopilot = infoFirst['Autopilot']
checkRefreshEtc = infoFirst['Check refresh etc']
scrn = infoFirst['Screen to use']
print('scrn = ',scrn, ' from dialog box')
fullscr = infoFirst['Fullscreen (timing errors if not)']
refreshRate = infoFirst['Screen refresh rate']

if demo: refreshRate = 85. 
tokenChosenEachRing= [-999]*numRings
targetDur =  1/refreshRate * 2 # 2 #duration of target  (in seconds) but staircased in practice 
targetDur = round(targetDur * refreshRate) / refreshRate #discretize to nearest integer number of refreshes
rampUpDur=0
rampUpFrames = refreshRate*rampUpDur
ballStdDev = 1.8
mouseChoiceArea = ballStdDev*0.8 # origin =1.3
units='deg' #'cm'
timeTillReversalMin = 0.5 #0.5; 
timeTillReversalMax = 1.5# 1.3 #2.9
#monitor parameters
widthPix = 1024 #1440  #monitor width in pixels
heightPix = 768  #900 #monitor height in pixels
monitorwidth = 40.5 #28.5 #monitor width in centimeters
viewdist = 55.; #cm
pixelperdegree = widthPix/ (atan(monitorwidth/viewdist) /np.pi*180)
bgColor = [0,0,0] # [-1,-1,-1] #black background
monitorname = 'testMonitor' # 'mitsubishi' #in psychopy Monitors Center
if exportImages:
    fullscr=0; scrn=0
    widthPix = 600; heightPix = 450
    monitorwidth = 25.0
if demo:    
    scrn=0; fullscr=1
    widthPix = 1024; heightPix = 768
    monitorname='testMonitor'
    allowGUI = True
    monitorwidth = 40.5#18.0

mon = monitors.Monitor(monitorname,width=monitorwidth, distance=viewdist)#fetch the most recent calib for this monitor
mon.setSizePix( (widthPix,heightPix) )
myWin = openMyStimWindow(mon,widthPix,heightPix,bgColor,allowGUI,units,fullscr,scrn,waitBlank)
myMouse = event.Mouse(visible = 'true',win=myWin)
myWin.setRecordFrameIntervals(False)

trialsPerCondition = 2*4 #default value is 2*4 need have this as if want to block and do practice trials manually
#but ensuring its all in correct blocked condition then need to have 184 trials and esc before runs stat.

refreshMsg2 = ''
if not checkRefreshEtc:
    refreshMsg1 = 'REFRESH RATE WAS NOT CHECKED'
    refreshRateWrong = False
else: #checkRefreshEtc
    runInfo = psychopy.info.RunTimeInfo(
            # if you specify author and version here, it overrides the automatic detection of __author__ and __version__ in your script
            #author='<your name goes here, plus whatever you like, e.g., your lab or contact info>',
            #version="<your experiment version info>",
            win=myWin,    ## a psychopy.visual.Window() instance; None = default temp window used; False = no win, no win.flips()
            refreshTest='grating', ## None, True, or 'grating' (eye-candy to avoid a blank screen)
            verbose=True, ## True means report on everything 
            userProcsDetailed=True  ## if verbose and userProcsDetailed, return (command, process-ID) of the user's processes
            )
    print('Finished runInfo- which assesses the refresh and processes of this computer')
    refreshMsg1 = 'Median frames per second ='+ str( np.round(1000./runInfo["windowRefreshTimeMedian_ms"],1) )
    refreshRateTolerancePct = 3
    pctOff = abs( (1000./runInfo["windowRefreshTimeMedian_ms"]-refreshRate) / refreshRate)
    refreshRateWrong =  pctOff > (refreshRateTolerancePct/100.)
    if refreshRateWrong:
        refreshMsg1 += ' BUT'
        refreshMsg1 += ' program assumes ' + str(refreshRate)
        refreshMsg2 =  'which is off by more than' + str(round(refreshRateTolerancePct,0)) + '%!!'
    else:
        refreshMsg1 += ', which is close enough to desired val of ' + str( round(refreshRate,1) )
    myWinRes = myWin.size
    myWin.allowGUI =True

myWin.close() #have to close window to show dialog box
dlgLabelsOrdered = list() #new dialog box
myDlg = gui.Dlg(title="object tracking experiment", pos=(200,400))
if not autopilot:
    myDlg.addField('Subject name :', subject, tip='or subject code')
    dlgLabelsOrdered.append('subject')
myDlg.addField('Trials per condition (default=' + str(trialsPerCondition) + '):', trialsPerCondition, tip=str(trialsPerCondition))
dlgLabelsOrdered.append('trialsPerCondition')
myDlg.addText(refreshMsg1, color='Black')
if refreshRateWrong:
    myDlg.addText(refreshMsg2, color='Red')
msgWrongResolution = ''
if checkRefreshEtc and (not demo) and (myWinRes != [widthPix,heightPix]).any():
    msgWrongResolution = 'Instead of desired resolution of '+ str(widthPix)+'x'+str(heightPix)+ ' pixels, screen apparently '+ str(myWinRes[0])+ 'x'+ str(myWinRes[1])
    myDlg.addText(msgWrongResolution, color='Red')
    print(msgWrongResolution);  savingForEventualLog.append(msgWrongResolution)
myDlg.addText('Note: to abort press ESC at a trials response screen', color='DimGrey') # color='DimGrey') color names stopped working along the way, for unknown reason
myDlg.show()
if myDlg.OK: #unpack information from dialogue box
   thisInfo = myDlg.data #this will be a list of data returned from each field added in order
   if not autopilot:
       name=thisInfo[dlgLabelsOrdered.index('subject')]
       if len(name) > 0: #if entered something
         subject = name #change subject default name to what user entered
       trialsPerCondition = int( thisInfo[ dlgLabelsOrdered.index('trialsPerCondition') ] ) #convert string to integer
       print('trialsPerCondition=',trialsPerCondition)
       savingForEventualLog.append('trialsPerCondition ='+str(trialsPerCondition))
else: 
   print('User cancelled from dialog box.'); savingForEventualLog.append('User cancelled from dialog box')
   core.quit()

if os.path.isdir('.'+os.sep+'dataRaw'):
    dataDir='dataRaw'
else:
    msg= 'dataRaw directory does not exist, so saving data in present working directory'
    print(msg); savingForEventualLog.append(msg)
    dataDir='.'
expname = ''
fileNameWithPath = dataDir+'/'+subject+ '_' + expname+timeAndDateStr
if not demo and not exportImages:
    import shutil
    bupCodeDestination = fileNameWithPath + '.py'
    shutil.copyfile(sys.argv[0], bupCodeDestination)      
    #also save helpersAOH.py because it has critical drawing commands
    bupHelpersDestinatn = fileNameWithPath + '_helpersAOH.py'
    shutil.copyfile('helpersAOHtargetFinalCueLocatn.py', bupHelpersDestinatn)  
    logF = logging.LogFile(fileNameWithPath+'.log', 
        filemode='w',#if you set this to 'a' it will append instead of overwriting
        level=logging.INFO)#info, data, warnings, and errors will be sent to this logfile
if demo or exportImages: 
  logging.console.setLevel(logging.ERROR)  #only show this level  messages and higher
logging.console.setLevel(logging.WARNING) #DEBUG means set the console to receive nearly all messges, INFO is for everything else, INFO, EXP, DATA, WARNING and ERROR
logging.info(savingForEventualLog) #stuff recorded before log set up
if refreshRateWrong:
    logging.error(refreshMsg1+refreshMsg2)
else: logging.info(refreshMsg1+refreshMsg2)
longerThanRefreshTolerance = .10 #0.27
longFrameLimit = round(1000./refreshRate*(1.0+longerThanRefreshTolerance),3) # round(1000/refreshRate*1.5,2)
msg = 'longFrameLimit='+ str(longFrameLimit) +' Recording trials where one or more interframe interval exceeded this figure '
logging.info(msg); print(msg)
if msgWrongResolution != '':
    logging.error(msgWrongResolution)

myWin = openMyStimWindow(mon,widthPix,heightPix,bgColor,allowGUI,units,fullscr,scrn,waitBlank)
msg='Window opened'; print(msg); logging.info(msg)
myMouse = event.Mouse(visible = 'true',win=myWin)
msg='Mouse enabled'; print(msg); logging.info(msg)
runInfo = psychopy.info.RunTimeInfo(
        win=myWin,    ## a psychopy.visual.Window() instance; None = default temp window used; False = no win, no win.flips()
        refreshTest='grating', ## None, True, or 'grating' (eye-candy to avoid a blank screen)
        verbose=True, ## True means report on everything 
        userProcsDetailed=True  ## if verbose and userProcsDetailed, return (command, process-ID) of the user's processes
        )
msg = 'second window opening runInfo mean ms='+ str( runInfo["windowRefreshTimeAvg_ms"] )
logging.info(msg); print(msg)
logging.info(runInfo)
logging.info('gammaGrid='+str(mon.getGammaGrid()))
logging.info('linearizeMethod='+str(mon.getLinearizeMethod()))

eyeballRadius = 5
eyeball = visual.Circle(myWin, radius=eyeballRadius, edges=32, fillColorSpace='rgb',fillColor = (1,0,1),autoLog=autoLogging) #to outline chosen options

gaussian = visual.PatchStim(myWin, tex='none',mask='gauss',colorSpace='rgb',size=ballStdDev,autoLog=autoLogging)
gaussian2 = visual.PatchStim(myWin, tex='none',mask='gauss',colorSpace='rgb',size=ballStdDev,autoLog=autoLogging)
optionChosenCircle = visual.Circle(myWin, radius=mouseChoiceArea, edges=32, fillColorSpace='rgb',fillColor = (1,0,1),autoLog=autoLogging) #to outline chosen options
clickableRegion = visual.Circle(myWin, radius=0.5, edges=32, fillColorSpace='rgb',fillColor = (-1,1,-1),autoLog=autoLogging) #to show clickable zones
circlePostCue = visual.Circle(myWin, radius=2*radii[0], edges=32, fillColorSpace='rgb',fillColor = (-.85,-.85,-.85),lineColor=(-1,-1,-1),autoLog=autoLogging) #visual postcue
#referenceCircle allows visualisation of trajectory, mostly for debugging
referenceCircle = visual.Circle(myWin, radius=radii[0], edges=32, fillColorSpace='rgb',lineColor=(-1,-1,1),autoLog=autoLogging) #visual postcue

blindspotFill = 0 #a way for people to know if they move their eyes
if blindspotFill:
    blindspotStim = visual.PatchStim(myWin, tex='none',mask='circle',size=4.8,colorSpace='rgb',color = (-1,1,-1),autoLog=autoLogging) #to outline chosen options
    blindspotStim.setPos([13.1,-2.7]) #AOH, size=4.8; pos=[13.1,-2.7] #DL: [13.3,-0.8]
fixatnNoise = False
fixSizePix = 20 #make fixation big so flicker more conspicuous
if fixatnNoise:
    numChecksAcross = fixSizePix/4
    nearestPowerOfTwo = round( sqrt(numChecksAcross) )**2 #Because textures (created on next line) must be a power of 2
    fixatnNoiseTexture = np.round( np.random.rand(nearestPowerOfTwo,nearestPowerOfTwo) ,0 )   *2.0-1  #multiply by 2 and subtract 1 so goes from -1 to 1
    #Can counterphase flicker  noise texture to create salient flicker if you break fixation
    fixation= visual.PatchStim(myWin, tex=fixatnNoiseTexture, size=(fixSizePix,fixSizePix), units='pix', mask='circle', interpolate=False, autoLog=autoLogging)
    fixationCounterphase= visual.PatchStim(myWin, tex=-1*fixatnNoiseTexture, colorSpace='rgb',mask='circle',size=fixSizePix,units='pix',autoLog=autoLogging)
else:
    fixation = visual.PatchStim(myWin,tex='none',colorSpace='rgb',color=(.3,.3,.3),mask='circle',units='pix',size=fixSizePix,autoLog=autoLogging)
    fixationCounterphase= visual.PatchStim(myWin,tex='none',colorSpace='rgb',color=(-1,-1,-1),mask='circle',units='pix',size=fixSizePix,autoLog=autoLogging)
fixationPoint = visual.Circle(myWin, size=6, fillColor=(1,1,1), units='pix', lineColor=None, autoLog=autoLogging)
fixation.setPos([0,0])
fixationCounterphase.setPos([0,0])

#create noise post-mask
maskDur = 0.5 
individualMaskDurFrames = 5
numChecksAcross = 128 #128
nearestPowerOfTwo = 2**round( log(numChecksAcross,2) ) #Because textures (created on next line) must be a power of 2
noiseMasks = []
numNoiseMasks = int(          ceil(maskDur / ((1/refreshRate)*individualMaskDurFrames))                    )
maskToSpareFixatn = np.ones((19,19)) #needed if doing premask because will happen at same time that fixation is on
maskToSpareFixatn[9,9] = -1 #Draw everywhere except inner, to continue to show fixation point
for i in range(numNoiseMasks): #in python3 xrange was changed to range
    whiteNoiseTexture = np.round( np.random.rand(nearestPowerOfTwo,nearestPowerOfTwo) ,0 )   *2.0-1 #Can counterphase flicker  noise texture to create salient flicker if you break fixation
    noiseMask= visual.PatchStim(myWin, tex=whiteNoiseTexture,
        size=(widthPix,heightPix*.9),pos=[0,heightPix*.05], units='pix', interpolate=False, autoLog=autoLogging) #patchStim is deprecated but used in previous experiments
    if premask:
        noiseMask= visual.GratingStim(myWin, units='pix', tex=whiteNoiseTexture, mask = maskToSpareFixatn, size=(heightPix*.9,heightPix*.9),
                        sf = None)  #only one cycle because no pattern actually repeats
                        #angularRes=angRes, interpolate=antialiasGrating, autoLog=autoLogging)
    noiseMasks.append(noiseMask)
        
respText = visual.TextStim(myWin,pos=(0, -.8),colorSpace='rgb',color = (1,1,1),alignHoriz='center', alignVert='center', units='norm',autoLog=autoLogging)
NextText = visual.TextStim(myWin,pos=(0, 0),colorSpace='rgb',color = (1,1,1),alignHoriz='center', alignVert='center', units='norm',autoLog=autoLogging)
NextRemindPctDoneText = visual.TextStim(myWin,pos=(-.1, -.4),colorSpace='rgb',color= (1,1,1),alignHoriz='center', alignVert='center', units='norm',autoLog=autoLogging)
NextRemindCountText = visual.TextStim(myWin,pos=(.1, -.5),colorSpace='rgb',color = (1,1,1),alignHoriz='center', alignVert='center', units='norm',autoLog=autoLogging)
NextRemindCountText.setText( ' ' )

stimListStationary = []; stimListMoving = []
speedsBesidesStationary = np.array([1])  # np.array([1])   #dont want to go faster than 2 rps because of blur problem
#Set up the factorial design (list of all conditions)
for numCuesEachRing in [ [1] ]:
 for numObjsEachRing in [ [8] ]:#8 #First entry in each sub-list is num objects in the first ring, second entry is num objects in the second ring
  for cueLeadTime in [0.060, 0.125, 0.167, 0.267, 0.467]:  #How long is the cue on prior to the target and distractors appearing
    for durMotionMin in [.4]:   #If speed!=0, how long should cue(s) move before stopping and cueLeadTime clock begins
      durMotion = durMotionMin + random.random()*1.1
      for direction in [-1.0,1.0]:
          for targetOffset in [-1,1]:
            for objToCueQuadrant in [0]: #AHdebug range(4):
                stimListStationary.append( {'numCuesEachRing':numCuesEachRing,'numObjsEachRing':numObjsEachRing,'targetOffset':targetOffset,'decoy':True,
                                            'cueLeadTime':cueLeadTime,'durMotion':durMotion,'speed':0,'objToCueQuadrant':objToCueQuadrant,'direction':direction} )
                
                for baseSpeed in speedsBesidesStationary:
                    speed = baseSpeed + random.random()*.15 #add a random number to the speed so that final position is not predictable
                    stimListMoving.append( {'numCuesEachRing':numCuesEachRing,'numObjsEachRing':numObjsEachRing,'targetOffset':targetOffset,'decoy':False,
                                                'cueLeadTime':cueLeadTime,'durMotion':durMotion,'speed':speed,'objToCueQuadrant':objToCueQuadrant,'direction':direction} )
#set up record of proportion correct in various conditions
trialsStationary = data.TrialHandler(stimListStationary,trialsPerCondition) #constant stimuli method
trialsMoving = data.TrialHandler(stimListMoving,trialsPerCondition) #constant stimuli method
                                #        extraInfo= {'subject':subject} )  #will be included in each row of dataframe and wideText. Not working in v1.82.01
trialHandlerList = [ trialsMoving, trialsStationary ] #To change the order of blocks, change the order in this list
#trialHandlerList = [ trialsStationary, trialsMoving ]
#To do practice trial sets manually then expt making sure its blocked so all stationary or all motion need to have both set to same condition 
#so either [trialsStationary, trialsStationary] or [trialsMoving, trialsMoving]. alex default was
# [ trialsStationary, trialsMoving ] and then reduce no trials from 8 to 4 line 105 now 
#doesn't work causes it to freeze. need another way of having it only give either moving or stationary
random.shuffle(trialHandlerList) #this randomises which one comes first

numRightWrongEachSpeed = np.zeros([ len(speedsBesidesStationary)+1, 2 ]); #summary results to print out at end
#end setup of record of proportion correct in various conditions

timeAndDateStr = time.strftime("%d%b%Y_%H-%M", time.localtime()) 
logging.info(  str('starting exp with name: "'+'MovingCue'+'" at '+timeAndDateStr)   )
print(' nTotal trialsStationary=', trialsStationary.nTotal,' nTotal trialsMoving=', trialsMoving.nTotal)
logging.info( 'nTotal trialsStationary='+ str(trialsStationary.nTotal)+' refreshRate='+str(refreshRate)      )
logging.info( 'nTotal trialsMoving='+ str(trialsMoving.nTotal)    )
#logging.info( 'numtrials='+ str(trials.nTotal)+' refreshRate='+str(refreshRate)      )

logging.info('rampUpDur='+str(rampUpDur)+ ' targetDur='+ str(targetDur) + ' secs')
logging.info('task='+'track'+'   respType='+respType)
logging.info(   'radii=' + str(radii)   )
logging.flush()

#RFcontourAmp= 0.0
#RFcontourFreq = 2.0
#RFcontourPhase = 0
#def RFcontourCalcModulation(angle,freq,phase): 
#    modulation = sin(angle*freq + phase) #radial frequency contour equation, e.g. http://www.journalofvision.org/content/14/11/12.full from Wilkinson et al. 1998
#    return modulation

#ampTemporalRadiusModulation = 0.0 # 1.0/3.0
#ampModulatnEachRingTemporalPhase = np.random.rand(numRings) * 2*np.pi
#def xyThisFrameThisAngle(basicShape, radiiThisTrial, numRing, angle, thisFrameN, speed):
#    #period of oscillation should be in sec
#    periodOfRadiusModulation = 1.0/speed#so if speed=2 rps, radius modulation period = 0.5 s
#    r = radiiThisTrial[numRing]
#    timeSeconds = thisFrameN / refreshRate
#    modulatnPhaseRadians = timeSeconds/periodOfRadiusModulation * 2*pi + ampModulatnEachRingTemporalPhase[numRing]
#    def waveForm(phase,type):
#        if type=='sin':
#            return sin(modulatnPhaseRadians)
#        elif type == 'sqrWave':
#            ans = np.sign( sin(modulatnPhaseRadians) ) #-1 or 1. That's great because that's also sin min and max
#            if ans==0: ans = -1+ 2*round( np.random.rand(1)[0] ) #exception case is when 0, gives 0, so randomly change that to -1 or 1
#            return ans
#        else: print('Error! unexpected type in radiusThisFrameThisAngle')
#        
#    if basicShape == 'circle':
#        rThis =  r + waveForm(modulatnPhaseRadians,'sin') * r * ampTemporalRadiusModulation
#        rThis += r * RFcontourAmp * RFcontourCalcModulation(angle,RFcontourFreq,RFcontourPhase)
#        x = rThis*cos(angle)
#        y = rThis*sin(angle)
#    elif basicShape == 'square': #actual square-shaped trajectory. Could also add all the modulations to this, later
#            #Theta varies from 0 to 2pi. Instead of taking its cosine, I should just pretend it is linear. Map it to 0->1 with triangle wave
#            #Want 0 to pi to be -1 to 1
#            def triangleWave(period, phase):
#                   #triangle wave is in sine phase (starts at 0)
#                   y = -abs(phase % (2*period) - period) # http://stackoverflow.com/questions/1073606/is-there-a-one-line-function-that-generates-a-triangle-wave
#                   #y goes from -period to 0.  Need to rescale to -1 to 1 to match sine wave etc.
#                   y = y/period*2 + 1
#                   #Now goes from -1 to 1
#                   return y
#            x = r * triangleWave(pi,angle)
#            y = r * triangleWave(pi, (angle-pi/2)%(2*pi ))
#            #This will always describe a diamond. To change the shape would have to use vector rotation formula
#    else: print('Unexpected basicShape ',basicShape)
#    return x,y

#highA = sound.Sound('G',octave=5, sampleRate=6000, secs=.3)
#low = sound.Sound('F',octave=3, sampleRate=6000, secs=.3)
def play_high_tone_correct_low_incorrect(correct, passThisTrial=False):
    try:
        highA = sound.Sound('G',octave=5, sampleRate=6000, secs=.3)
    except: #in case file missing, create inferiro click manually
        logging.warn('Could not create the correct! sound')
        print('Could not create the correct! sound')
    try:
        low = sound.Sound('F',octave=3, sampleRate=6000, secs=.3)
    except: #in case file missing, create inferiro click manually
        logging.warn('Could not create the wrong! sound')
        print('Could not create the wrong! sound')        
      
    highA.setVolume(0.9)
    low.setVolume(1.0)
    if correct:
        highA.play()
    elif passThisTrial:
        high= sound.Sound('G',octave=4, sampleRate=2000, secs=.08, bits=8)
        for i in range(2): 
            high.play();  low.play(); 
    else: #incorrect
        low.play()
        
def angleChangeThisFrame(thisTrial, moveDirection, numRing, thisFrameN, lastFrameN):
    #angleMove is deg of the circle
    #speed is in units of revolutions per second
    angleMovePerFrame = moveDirection[numRing]*thisTrial['direction']*thisTrial['speed']*360/refreshRate
    angleMove = angleMovePerFrame*(thisFrameN-lastFrameN)
    #print("angleMovePerFrame = ",angleMovePerFrame,"angleMove=",angleMove)
    return angleMove

def oneFrameOfStim(thisTrial,currFrame,lastFrame,maskBegin,cues,decoyCues,stimRings,targetRings,lines,offsetXYeachRing):
  #a function to draw each frame of stim. Can potentially call it also during tracking task response phase, if you want to use that type of response.
  n=currFrame
  if n<rampUpFrames:
        contrast = cos( -pi+ pi* n/rampUpFrames  ) /2. +.5 #starting from -pi trough of cos, and scale into 0->1 range
  else: contrast = 1
  if n%2:
    fixation.draw()#flicker fixation on and off at framerate to see when skip frame
  else:
    fixationCounterphase.draw()
  fixationPoint.draw()
  
  numRing = 0 #Haven't implemented capability for multiple rings, although started out that way, got rid of it because complexity
  #draw cue
  timeTargetOnset = thisTrial['cueLeadTime']
  cueMovementEndTime = 0
  if thisTrial['speed']>0 or thisTrial['decoy']:  #durMotion encodes durDecoys if it's a decoy experiment and it's the stationary condition (speed=0)
    cueMovementEndTime += thisTrial['durMotion']
    #If motion, that means cue moves for a while and then cueLeadTime starts when cue stops moving. Decoy needs foreperiod matched to that.
    timeTargetOnset += thisTrial['durMotion']

  if n<= cueMovementEndTime*refreshRate: #cue movement interval. Afterwards, cue stationary and cueLeadTime begins
    angleMove = angleChangeThisFrame(thisTrial, moveDirection, numRing, n, lastFrame)
    cues[numRing].setOri(angleMove,operation='+',log=autoLogging)
    decoyCues.setOri(angleMove,operation='+',log=autoLogging)
    for line in lines: #move their (eventual) position along with the cue.  
        eccentricity = sqrt( line.pos[0]**2 + line.pos[1]**2 ) #reverse calculate its eccentricity
        currLineAngle =  atan2(line.pos[1],line.pos[0])    /pi*180  #calculate its current angle
        currLineAngle -= angleMove #subtraction because grating angles go opposite direction to non-gratings
        x = cos(currLineAngle/180*pi) * eccentricity
        y = sin(currLineAngle/180*pi) * eccentricity
        line.setPos( [x,y], log=autoLogging)   
        #line.draw() #shows that it moves wqith the cue
    if thisTrial['decoy']: #draw decoys only until cueLeadTime begins
      decoyCues.draw()
      #print('Drew decoy')
    #print("cueMovementEndTime=",cueMovementEndTime,"n=",n,", in sec=",n/refreshRate, "currLineAngle=",currLineAngle, "cues ori=",cues[numRing].ori) 
  if n == cueMovementEndTime*refreshRate:
    if eyetracking:
        tracker.sendMessage('Cue will stop moving with this upcoming frame.')

  if premask and n < round(timeTargetOnset*refreshRate):
    whichMask = 0 #static mask
    noiseMasks[ int(whichMask) ].draw()
    
  for cue in cues: 
    cue.draw()
  cueCurrAngle = cues[numRing].ori
  #print('Frame = ',n) #AHdebug
    
  #check whether time to draw target (and distractors) 
  if n >= round(timeTargetOnset*refreshRate): #draw target and distractor objects
        #print('Drawing ',n-round(timeTargetOnset*refreshRate),'th frame of target')
        linesInsteadOfArcTargets = True
        #draw distractor objects
        if not linesInsteadOfArcTargets:
            for stimRing in stimRings: 
                stimRing.draw()
        #draw target(s)
        if not linesInsteadOfArcTargets:
            for targetRing in targetRings:
              targetRing.draw()  #Probably just the new background (to replace the displaced target, and the target
        else:
            for line in lines:  
                line.draw()
  if eyetracking and n == round(timeTargetOnset*refreshRate):
        tracker.sendMessage('Target and distractors drawn on next frame.')
  #if n==1:   print("n=",n,"timeTargetOnset = ",timeTargetOnset, "timeTargetOnset frames = ",timeTargetOnset*refreshRate, "cueLeadTime=",thisTrial['cueLeadTime']) 
  if n >= round(maskBegin*refreshRate): #time for mask
    howManyFramesIntoMaskInterval  = round(n - maskBegin*refreshRate)
    whichMask = int( howManyFramesIntoMaskInterval / individualMaskDurFrames ) #increment whichMAsk every maskFramesDur frames
    whichMask = whichMask % numNoiseMasks #restart with first if no more are available
    #print("individualMaskDurFrames=",individualMaskDurFrames,"howManyFramesIntoMaskInterval=",howManyFramesIntoMaskInterval, " whichMask=",whichMask, "numNoiseMasks = ",numNoiseMasks)
    noiseMasks[ int(whichMask) ].draw()
  if eyetracking and n == round(timeTargetOnset*refreshRate):
        tracker.sendMessage('Target and distractors drawn on next frame.')
        
  if blindspotFill:
      blindspotStim.draw()
  return cueCurrAngle
# #######End of function definition that displays the stimuli!!!! #####################################

respPromptText = visual.TextStim(myWin,height=0.04, pos=(0, -.9),colorSpace='rgb',color = (1,1,1),alignHoriz='center', alignVert='center', units='norm',autoLog=autoLogging)
respPromptText.setText('Press G if the cued circle is black, or L if it is white')
#respPromptText.setText('Press G if the line is like the rim, or L if it is oriented like a spoke')

def collectResponses(expStop): #Kristjansson&Holcombe cuing experiment
    #draw the possible stimuli
    #eyeball left, eyeball right, eyeball down, eyeball up
    #draw something that represents clockwise 
    responsesNeeded = 1
    responsesAutopilot = list(['L'])
    for r in range(responsesNeeded):
        responsesAutopilot.append('L')
    respcount =0
    
    while respcount <responsesNeeded:
        respPromptText.draw()
        myWin.flip()
        for key in event.getKeys():       #check if pressed abort-type key
              key = key.upper()
              if key in ['ESCAPE','Q']:
                  expStop = True
                  respcount += 1
                  responses.append('X') #dummy response so dont' get error when try to record in datafile before quitting
              elif key.upper() in ['L','G']: #L for towards edge of screen, G for towards ctr #A for anticlockwise, L for clockwise
                   responses.append( key.upper() )
                   respcount += 1
              else: #flicker response prompt to indicate invalid response
                for f in range(2):
                    myWin.flip(); myWin.flip()
                    respPromptText.draw()
                    myWin.flip()
        if autopilot:
           respCount = responsesNeeded
           break
           
    return responses,responsesAutopilot, expStop

numTrialsCorrect=0; expStop=False; framesSaved=0;
print('Starting experiment of nTotal trialsStationary=', trialsStationary.nTotal,' nTotal trialsMoving=', trialsMoving.nTotal)
myWin.flip()
#I don't need to print a header anymore, because it's done automatically by trialHandler with e.g. trials.saveAsWideText
trialClock = core.Clock()
stimClock = core.Clock()
ts = list();

highA = sound.Sound('G',octave=5, sampleRate=6000, secs=.4) #, bits=8)  latest version of psychopy no bits
highA.setVolume(0.8)
lowD = sound.Sound('E',octave=3, sampleRate=6000, secs=.4) #, bits=8)  latest version of psychopy no bits 
       
if eyetracking:
    if getEyeTrackingFileFromEyetrackingMachineAtEndOfExperiment:
        eyeMoveFile=('EyeTrack_'+subject+'_'+timeAndDateStr+'.EDF')
    tracker=Tracker_EyeLink(myWin,trialClock,subject,1, 'HV5',(255,255,255),(0,0,0),False,(widthPix,heightPix))

totTrialsRun=0; trialNum = 0; blockNum = 0
for trials in trialHandlerList:
    trialNum=0; print('Starting new block of ' + str(trials.nTotal) + ' trials')
    while trialNum < trials.nTotal and expStop==False:  #main trial loop
        if psychopy.__version__ >='3.0.5':
            thisTrial = trials.__next__()
        else:
            thisTrial = trials.next()
        accelerateComputer(1,process_priority, disable_gc) #speed up
        
        waitForKeyPressBetweenTrials = False
        if trialNum< trials.nTotal:
            pctTrialsCompletedForBreak = np.array([.5,.8])  
            breakTrials = np.round(trials.nTotal*pctTrialsCompletedForBreak)
            timeForTrialsRemainingMsg = np.any(trialNum==breakTrials)
            pctDone = round(    (1.0*trialNum) / (1.0*trials.nTotal)*100,  0  )
            if timeForTrialsRemainingMsg and not (pctDone==0 and blockNum==0): #Don't do it for first trial of first block
                if pctDone ==0: #first trial of block
                   NextRemindPctDoneText.setText( 'New block and NEW CUING CONDIION commencing' )
                   NextRemindCountText.setText( ' ' )
                else:
                   NextRemindPctDoneText.setText( str(pctDone) + '% complete' )
                   NextRemindCountText.setText( str(trialNum) + ' of ' + str(trials.nTotal)  + ' in this block.'    )
                for i in range(5):
                    myWin.flip(clearBuffer=True)
                    NextRemindPctDoneText.draw()
                    NextRemindCountText.draw()
            waitingForKeypress = False
            if waitForKeyPressBetweenTrials or timeForTrialsRemainingMsg:
                waitingForKeypress=True
                NextText.setText('Press "SPACE" to continue')
                NextText.draw()
                NextRemindCountText.draw()
                #NextRemindText.draw()
                myWin.flip(clearBuffer=True) 
            else: core.wait(0.15)
            while waitingForKeypress:
               if autopilot:
                    waitingForKeypress=False
               elif expStop == True:
                    waitingForKeypress=False
               for key in event.getKeys():       #check if pressed abort-type key
                     if key in ['space']: 
                        waitingForKeypress=False
                     if key in ['escape','q']:
                        expStop = True
                        waitingForKeypress=False
            myWin.clearBuffer()
        core.wait(.04); time.sleep(.03) 
        
        numObjects = thisTrial['numObjsEachRing'][0] #haven't implemented additional rings yet
        objsPerQuadrant = numObjects / 4
        objToCue = np.array([0] )
        randomiseObjToCue = False
        if randomiseObjToCue:
            if numObjects % 4 != 0:
                msg = 'numObjects not evenly divisible by 4, therefore cannot randomise quadrant. Therefore picking object to cue completely randomly'
                logging.error(msg); print(msg)
                objToCue = np.random.random_integers(0, numObjects-1, size=1) #randomise which object is cued and thus is the target 
            else:
                withinQuadrantObjectToCue =  np.random.random_integers(0, objsPerQuadrant-1, size=1)
                objToCue =  thisTrial['objToCueQuadrant']*objsPerQuadrant + withinQuadrantObjectToCue
        colorRings=list();
        preDrawStimToGreasePipeline = list()
        isReversed= list([1]) * numRings #always takes values of -1 or 1
        reversalNumEachRing = list([0]) * numRings
        moveDirection = list( np.random.random_integers(0,1,size=[numRings]) *2 -1 ) #randomise initial direction
        moveDirection[0] = 1 #always make the 0th ring have the same motion as 'direction' - it gets multiplied by thisTrial['direction']
        durExtra = thisTrial['durMotion'] if (thisTrial['speed'] or thisTrial['decoy']) else 0 #in motion condition, cue moves for awhile before cue lead time clock starts. Decoy has to be matched
        maskBegin = thisTrial['cueLeadTime'] + targetDur + durExtra
        trialDurTotal = maskBegin + maskDur
        trialDurFrames= int( trialDurTotal*refreshRate )
        
        #Task will be to judge which thick wedge has the thin wedge offset within it, or now whether target bright or dark
        
        #Set up parameters to construct the thick (context),thin (target offset relative to context) wedges
        gratingTexPix= 1024
        visibleWedge = [0,360]
        patchAngleThickWedges = 22# 360/numObjects/2   #angular subtense of the circle of the cue (and objects if they are arcs)
        thickWedgeColor = [.85,.85,.85]  
        thinWedgeColor=  [-.75,-.75,-.75] 
        cueColor=[1,-.9,-.9] #
        radialMask = np.array( [0,0,0,0,1,0,0,0,0] ) # [0,0,0,0,0,0,0,1,0,0,0] )
        #This is the sliver that's offset relative to the larger wedge, that you have to judge the offset of
        radialMaskThinWedge =   np.array( [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] ) 
        wedgeRadiusFraction = np.where(radialMask)[0][0]*1.0 / len(radialMask)
        #print('wedgeRadiusFraction = ',wedgeRadiusFraction)
        wedgeThicknessFraction = len( np.where(radialMask)[0] )*1.0 / len(radialMask)
        #print('wedgeThickness = ',wedgeThicknessFraction*radii[0])
        wedgeCenterFraction = wedgeRadiusFraction + wedgeThicknessFraction/2.
        desiredArcDistanceFractionRadius = 0.10   #.23 #Is this what controls how far apart the two arcs of the cue are?
        cueInnerArcDesiredFraction = wedgeCenterFraction - desiredArcDistanceFractionRadius
        cueOuterArcDesiredFraction = wedgeCenterFraction + desiredArcDistanceFractionRadius
        if cueOuterArcDesiredFraction > 1:
            msg='Can"t start outer arc at fraction='+str(cueOuterArcDesiredFraction)
            logging.error(msg); print(msg)
        fractionResolution = .02     #Quantisation of possible positions of cue arc
        binsNeeded = 1.0 / fractionResolution 
        
        #setup cue parameters
        cueRadialMask = np.zeros( int(binsNeeded) )
        #For the cueRadialMask, want everything zero except just inside and outside of the wedges.
        innerArcCenterPos = int( round( binsNeeded*cueInnerArcDesiredFraction ) )
        outerArcCenterPos = int( round( binsNeeded*cueOuterArcDesiredFraction ) )
        cueRadialMask[ innerArcCenterPos ] = 1
        cueRadialMask[ outerArcCenterPos ] = 1
        innerArcActualFraction = innerArcCenterPos*1.0/len(cueRadialMask)
        outerArcActualFraction = outerArcCenterPos*1.0/len(cueRadialMask)
        closeEnough = .02
        if abs(cueInnerArcDesiredFraction - innerArcActualFraction) > closeEnough:
            print('cueInnerArcDesiredFraction of object radius = ',cueInnerArcDesiredFraction, ' actual = ', innerArcActualFraction, ' exceeding tolerance of ',closeEnough )
        if abs(cueOuterArcDesiredFraction - outerArcActualFraction) > closeEnough:
            print('cueOuterArcDesiredFraction of object radius = ',cueOuterArcDesiredFraction, ' actual = ', outerArcActualFraction, ' exceeding tolerance of ',closeEnough)
        initialAngle = random.random()*360.
        thickWedgesRing,thickWedgesRingCopy, thinWedgesRing, targetRing, cueDoubleRing, lines, decoyDoubleRing = constructThickThinWedgeRingsTargetAndCue(myWin, \
                initialAngle,radii[0],radialMask,radialMaskThinWedge,
                cueRadialMask,visibleWedge,numObjects,patchAngleThickWedges,patchAngleThickWedges,
                                bgColor,thickWedgeColor,thinWedgeColor,0,thisTrial['targetOffset'],gratingTexPix,cueColor,objToCue,ppLog=logging)
        #The thickWedgesRing, typically white, are drawn as a radial grating that occupies all 360 deg circular, with a texture to mask out everything else to create a ring
        #The thinWedgesRing, typically black, are centered in the white and one of these wedges will be later displaced to create a target.
        #The targetRing is the displaced black wedge. Actually a full circular radial grating, but visibleWedge set to subtend only the part where the target is.
        #The thickWedgesRingCopy is to draw over the old, undisplaced black wedge, only in the target area. It is thus a copy of the thickWedgesRing, 
        # with visibleWedge set to show only the target part
        #The cueRing is two red arcs to bring attention to the target area.
        core.wait(.1)
        myMouse.setVisible(False)
        if eyetracking: 
            tracker.startEyeTracking(trialNum,True,widthPix,heightPix) #start recording with eyetracker
        event.clearEvents() #clear key and mouseclick buffer
        fixatnPeriodFrames = int(   (np.random.rand(1)/2.+0.8)   *refreshRate)  #random interval between x and x+800ms
        if (fixatnPeriodFrames-1) % 2 ==0:
            fixatnPeriodFrames +=1 #make it odd
        for i in range(fixatnPeriodFrames):
            if i%2:
                fixation.draw()
            else: fixationCounterphase.draw()
            fixationPoint.draw()
            if premask:
                noiseMasks[0].draw() #premask
            myWin.flip() #clearBuffer=True)
        trialClock.reset()
        t0=trialClock.getTime(); t=trialClock.getTime()-t0
        ts = list()
        stimClock.reset()
        offsetXYeachRing=[[0,0],[0,0]]
        lastFrame = 0 #only used if useClock = True
        if eyetracking:
            tracker.sendMessage('Drawing cue for the first time')
        for n in range(trialDurFrames): #this is the loop for this trial's stimulus!
                if useClock: #Don't count on not missing frames. Use actual time.
                    t = stimClock.getTime()
                    currFrame = round(t*refreshRate)
                else: currFrame = n
                cueCurrAngle = oneFrameOfStim(thisTrial,currFrame,lastFrame,maskBegin,[cueDoubleRing],decoyDoubleRing,[thickWedgesRing,thinWedgesRing],
                                                         [thickWedgesRingCopy,targetRing],lines,offsetXYeachRing) #actual drawing of stimuli
                lastFrame = currFrame #only used if useClock=True
                if exportImages:
                    myWin.getMovieFrame(buffer='back') #for later saving
                    framesSaved +=1
                myWin.flip(clearBuffer=True)
                #if n == round(thisTrial['cueLeadTime']*refreshRate): 
                #  event.waitKeys(maxWait=20, keyList=['SPACE','ESCAPE','x'], timeStamped=False) #debugOFF
                t=trialClock.getTime()-t0; ts.append(t);
        myWin.flip()
        if eyetracking:
            tracker.stopEyeTracking()
            print ("Told eye tracker to stop")
        #end of big stimulus loop
        accelerateComputer(0,process_priority, disable_gc) #turn off stuff that sped everything up
        #check for timing problems
        interframeIntervs = np.diff(ts)*1000 #difference in time between successive frames, in ms
        idxsInterframeLong = np.where( interframeIntervs > longFrameLimit ) [0] #frames that exceeded longerThanRefreshTolerance of expected duration
        numCasesInterframeLong = len( idxsInterframeLong )
        if numCasesInterframeLong >0:
           longFramesStr =  'ERROR,'+str(numCasesInterframeLong)+' frames were longer than '+str(longFrameLimit)+' ms'
           if demo: 
             longFramesStr += 'not printing them all because in demo mode'
           else:
               longFramesStr += ' apparently screen refreshes skipped, interframe durs were:'+\
                        str( np.around(  interframeIntervs[idxsInterframeLong] ,1  ) )+ ' and was these frames: '+ str(idxsInterframeLong)
           if longFramesStr != None:
                    msg = 'trialnum=' + str(trialNum) +  longFramesStr
                    print(msg);  logging.info(msg)
                    if not demo:
                        flankingAlso=list()
                        for idx in idxsInterframeLong: #also print timing of one before and one after long frame
                            if idx-1>=0:  flankingAlso.append(idx-1)
                            else: flankingAlso.append(np.NaN)
                            flankingAlso.append(idx)
                            if idx+1<len(interframeIntervs):  flankingAlso.append(idx+1)
                            else: flankingAlso.append(np.NaN)
                        if np.NaN in flankingAlso: #was the first or last frame
                            logging.info('was first or last frame')
                        else:
                            logging.info( 'flankers also=' + str( np.around(interframeIntervs[flankingAlso],1) ))
                #end timing check
        passThisTrial=False
        #print('Collecting responses for trial=',trialNum,' totTrialsRun=',totTrialsRun)
        # ####### set up and collect responses
        responses = list();  responsesAutopilot = list()
        responses,responsesAutopilot, expStop =  \
                collectResponses(expStop)  #collect responses!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#####
        myMouse.setVisible(True)
        core.wait(.1)
        if exportImages:  #maybe catch one frame of response
            myWin.saveMovieFrames('exportedImages/frame.png')    
            expStop=True
        #Handle response, calculate whether correct, ########################################
        if autopilot:
            responses = responsesAutopilot
        #score response
        if thisTrial['targetOffset'] >0:
            answer = 'L'
        else:
            answer = 'G'
        if responses[0] == answer:
            correct = 1
        else: correct = 0            
        if passThisTrial: 
            correct = -1    #indicate for data analysis that observer opted out of this trial, because think they moved their eyes
        
        #header print('trialnum\tsubject\tbasicShape\tnumObjects\tspeed\tdirection\tangleIni
        trials.data.add('subject', subject) #because extraInfo not working
        #figure out color of lines (distractors and target) and record it for data file
        lineI=0
        for line in lines:
            color = line.fillColor
            rounded = np.round(color,0) #because dark or bright grey rather than fully black or fully white
            color = rounded[0] #it's an RGB triple, just reducing it to -1 for dark grey or 1 for white
            #print('lineColor =',line.fillColor, 'rounded=',rounded, 'color = ',color)
            trials.data.add('lineColor'+str(lineI), color)
            lineI +=1
        trials.data.add('objToCueRing0', objToCue[0])
        trials.data.add('numObjsRing0', numObjsEachRing[0])
        trials.data.add('numCuesRing0', numCuesEachRing[0])
        trials.data.add('objToCue0',objToCue[0])
        trials.data.add('initialAngle',initialAngle)
        trials.data.add('cueLastAngle',cueCurrAngle)
        trials.data.add('fixatnPeriodFrames',fixatnPeriodFrames)
        trials.data.add('response', responses[0]) #switching to using psychopy-native ways of storing, saving data 
        trials.data.add('correct', correct) #switching to using psychopy-native ways of storing, saving data 
        trials.data.add('timingBlips', numCasesInterframeLong)
        numTrialsCorrect += (correct >0)  #so count -1 as 0
        #speedIdxs = np.where(thisTrial['speed']==speeds)[0]
        #if len(speedIdxs) ==0:
        #    print('Apparently current speed= ',thisTrial['speed'],' is not in list of speeds=',speeds, '. Please make sure speeds is a numpy array')
        #else: speedIdx = speedIdxs[0]  #extract index, where returns a list with first element array of the indexes
        numRightWrongEachSpeed[ int( thisTrial['speed']>0 ), int(correct >0) ] +=1  #if right, add to 1th column, otherwise add to 0th column count
        
        if feedback and not expStop:
            play_high_tone_correct_low_incorrect(correct, passThisTrial=False)
            #print('correct=',correct) #Sound works now that I recreate the sound objects on each trial
    
        trialNum+=1; totTrialsRun +=1
        core.wait(.05); time.sleep(.08)
        
        if totTrialsRun >0:  #save data
            blockNum = 0
            for trialsSave in trialHandlerList:
                blockNum += 1
                if len(trialHandlerList) > 1: #more than 1 block of trials in this experiment
                    blockFnameText = 'block'+str(blockNum)
                fileNamePP = fileNameWithPath + blockFnameText # + '.txt'
                dfFromPP = None
                dfFromPP = trialsSave.saveAsWideText(fileNamePP, appendFile = False, fileCollisionMethod='overwrite')
                #if dfFromPP is not None:
                #    print("Psychopy wideText has been saved as", fileNamePP)
                saveAsPsydat = False
                if saveAsPsydat:
                    fileNamePickle = fileNameWithPath #.psydat will automatically be appended
                    trialsSave.saveAsPickle(fileNamePickle, fileCollisionMethod='overwrite') #.psydat
                    print("trials trialHandler has been saved as", fileNamePickle+'.psydat', ", which is the most Psychopy-ic method and should include a copy of the code")
                dataFramesWorking = False
                if dataFramesWorking:
                    df = dfFromPP[:trialNum] #delete trials for which don't have response etc. yet, as that will otherwise cause error when averaging, plotting
                    if trialNum < trialsSave.nTotal: #When you abort early, correct and other columns are not numeric because have value of "-"
                        #converting to numeric
                        df = df.to_numeric #deprecated: df.convert_objects(convert_numeric=True)
                        print('df.dtypes=', df.dtypes) #df.dtypes in my case are  "objects". you can't take the mean
                        print('dfFromPP =', df)
        blockNum +=1
        #end trials loop  ###########################################################
if expStop == True:
    msg = 'user aborted experiment on keypress with trials trialNum=' + str(trialNum) + ' totTrialsRun=' + str(totTrialsRun)
    logging.info(msg);  print(msg)
else: 
    print("Experiment finished")

if eyetracking and getEyeTrackingFileFromEyetrackingMachineAtEndOfExperiment:
    tracker.closeConnectionToEyeTracker(eyeMoveFile)
logging.info('finishing at '+timeAndDateStr)
#print('%corr = ', round( correct*1.0/trialNum*100., 2)  , '% of ',trialNum,' trials', end=' ')
nr = numRightWrongEachSpeed[:,1];  nw = numRightWrongEachSpeed[:,0]
print('nr = ',nr,' nw=',nw)
pctCorrEachSpeed = nr / (nr+nw)
print('%corr each speed: ', end=' ')
print( np.around(pctCorrEachSpeed, 2)  )
print('\t\t\t\tnum trials each speed =', numRightWrongEachSpeed[:,0] + numRightWrongEachSpeed[:,1])
logging.flush()
myWin.close()
if quitFinder:
        applescript="\'tell application \"Finder\" to launch\'" #turn Finder back on
        shellCmd = 'osascript -e '+applescript
        os.system(shellCmd)

#Fit and plot data
plotData = False
if trialNum >0 and plotData and dataFramesWorking:
    import plotHelpers
    fig = plotHelpers.plotDataAndPsychometricCurve(df, dataFileName=None)
    figName = 'pythonFig'
    figFnameWithPath = os.path.join('analysis/figs/', figName + '.png')
    import pylab
    pylab.savefig( figFnameWithPath ) #, bbox_inches='tight')
    print('The plot has been saved, as', figFnameWithPath)
    pylab.show() #pauses until window manually closed. Have to save before calling this, because closing the window loses the figure

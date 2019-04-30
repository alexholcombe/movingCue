What is the difference between HolcombeKristjansson_targetFinalCueLocatn.py and HolcombeKristjansson.py

## Lessons learned

Even with moving cue on for a very long time, curve looks same - participant reported target at cue destination.

Transient attnetion is hard to get, unless myabe you train Ss for hours?


## Working on code, notes

What's determining answer location for answer scoring?
targetOffset indicates what the target should be. targetRing drawn when time for target.

The gratings aren't used at all, instead it's a "lines" thing.

* Record origin position, destination position, and brightness in all locations. Destination position can be calculated by taking origin and multiplying thisTrial['durMotion'] by speed.

This is now in data file except destination which has to be calculated by taking initial angle and adding speed*durMotion (it would be risky to use the line angle because it is backwards-calculated)

* Christian: also report the time of 1) cue onset, 2) cue offset (which should be cue-onset + motion duration, I guess) and 3) target onset (which should be cue-offset + SOA). Recording these time points serve as a control of event times to better link events to gaze behavior. 

Done using     `tracker.sendMessage(msg)` but haven't checked whether works.

* Program task to be either destination position or origin position.
That might be jumping the gun because first want to verify there is something transient about all this, and problem with origin position is that it adds a cognitive demand, as the target has moved on.
Should probably start with comparing long-duration stationary position with standard stationary

## Figured out what's determining location of cued object
        objToCue = np.array([0] )
        angleIniEachRing = list( np.random.uniform(0,2*pi,size=[numRings]) )
        initialAngle = random.random()*360.
	randomiseObjToCue = False

Turning all above off gets rid of random variation.
When initialAngle = 0, with 8 objects target is slightly clockwise of vertical and positive angles rotate it clockwise.  initialAngle randomization should be enough


Target color gets determined by targetRadialOffset (because that was equivalent with old task).
Which object number is the target? *lineColor0*

## Setting up new experiment

Speed = 0

Decoy condition. 
* Have cues on in every location
* Make all disappear except the target's

Check timing

#durMotion encodes durDecoys if it's a decoy experiment and it's the stationary condition (speed=0)

durExtra = thisTrial['durMotion'] if (thisTrial['speed'] or thisTrial['decoy']) else 0 #in motion condition, cue moves for awhile before cue lead time clock starts. Decoy has to be matched

This is definitely gonna confuse me in the future that trial length linked to trial-by-trial decoy presence

## Making sure everything randomized right

-l.271 np.array[.2]) changed from .2 to 1 as in previous program
-l.275 cue lead times changed from "467*3" to the actual lead times: 0.02 etc.
-l.285 factor behind "randon.random()" changed from 1 to 2 (was 2 in previous program)
-l.646: changed from "0" back to random starting position
-l.278      for direction in [1.0]: # [-1.0,1.0]:
-l.302 random.shuffle(trialHandlerList) #this randomises which one comes first

        thickWedgeColor = [.7,.7,.7]  
        thinWedgeColor=  [-.7,-.7,-.7] 

Could randomize obj to cue with         randomiseObjToCue = False
But then would have to combine that with randomization over narrow range of the orientation of the whole thing. Probably simpler is to have objToCue always equal 0 and objToCue constant.


How should practice trials work?

## Expected results

At the minimal delay of .06 you can't hardly even see where the cue is after the decoys disappear, so there will be a delayed liftoff. But then what will this experiment mean, because then it's for certain that there will be a gradual increase. In part I wanted to do this experiment to show that the gradual increase was not due to masking by local transient of the appearance of the cue. But I guess it still means that if the motion condition shows a steeper slope, that's still kind of impressive that offset of motion can do that.

## Trying both a premask and a postmark

I seem to be near chance with these parameters:
        thickWedgeColor = [.85,.85,.85]  
        thinWedgeColor=  [-.75,-.75,-.75] 
cueLeadTime = .04

I think the motion condition may be easier because you can get your attention to more easily include the region inside the cue.
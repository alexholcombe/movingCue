What is the difference between HolcombeKristjansson_targetFinalCueLocatn.py and HolcombeKristjansson.py

## Lessons learned

Even with moving cue on for a very long time, curve looks same - participant reported target at cue destination.

Transient attnetion is hard to get, unless myabe you train Ss for hours?


## Working on code, notes

What's determining answer location for answer scoring?
targetOffset indicates what the target should be. targetRing drawn when time for target.

I guess to make target be at the cue destination, I just add to the targetRing orientation however far the cue has travelled.  Maybe don't draw distractors to visualize easily where target is.
Actually the gratings don't seem to be used at all, instead it's a "lines" thing.

* Record origin position, destination position, and brightness in all locations. Destination position can be calculated by taking origin and multiplying thisTrial['durMotion'] by speed.

This is now in data file except destination which 

* Christian: also report the time of 1) cue onset, 2) cue offset (which should be cue-onset + motion duration, I guess) and 3) target onset (which should be cue-offset + SOA). Recording these time points serve as a control of event times to better link events to gaze behavior. 

Done using     `tracker.sendMessage(msg)` but haven't checked whether works.

* Program task to be either destination position or origin position.
That might be jumping the gun because first want to verify there is something transient about all this, and problem with origin position is that it adds a cognitive demand, as the target has moved on.
Should probably start with comparing long-duration stationary position with standard stationary

## Figure out what's determining location of cued object
        objToCue = np.array([0] )

        angleIniEachRing = list( np.random.uniform(0,2*pi,size=[numRings]) )
        initialAngle = random.random()*360.
Turning both above off gets rid of random variation.
When initialAngle = 0, with 8 objects target is slightly clockwise of vertical and positive angles rotate it clockwise.

moveDirection randomized 

        randomiseObjToCue = False

Target color gets determined by targetRadialOffset (because that was equivalent with old task).
Which object number is the target? *lineColor0*

## Setting up new experiment

Speed = 0


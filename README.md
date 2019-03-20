What is the difference between HolcombeKristjansson_targetFinalCueLocatn.py and HolcombeKristjansson.py

## Lessons learned

Even with moving cue on for a very long time, curve looks same - participant reported target at cue destination.

Transient attnetion is hard to get, unless myabe you train Ss for hours?


## Working on code, notes

What's determining answer location for answer scoring?
targetOffset indicates what the target should be. targetRing drawn when time for target.

I guess to make target be at the cue destination, I just add to the targetRing orientation however far the cue has travelled.  Maybe don't draw distractors to visualize easily where target is.
Actually the gratings don't seem to be used at all, instead it's a "lines" thing.

* Record origin position, destination position, and brightness in all locations.

* Christian: also report the time of 1) cue onset, 2) cue offset (which should be cue-onset + motion duration, I guess) and 3) target onset (which should be cue-offset + SOA). Recording these time points serve as a control of event times to better link events to gaze behavior. 

* Program task to be either destination position or origin position. And fix auditory feedback.

* If auditory feedback can’t be fixed, add visual feedback message.

## Figure out what's determining location of cued object
        objToCue = np.array([0] )

        angleIniEachRing = list( np.random.uniform(0,2*pi,size=[numRings]) )
Turning that off, see if that gets rid of random variation.

        initialAngle = random.random()*360.
Turning that off. It seems to control initial angle of the cue within the grating.

moveDirection randomized 

        randomiseObjToCue = False

The lines are visual.Cirlces and I need to add their colors to data so they get printed out.
Target color gets determined by targetRadialOffset (because that was equivalent with old task).

## Setting up new experiment

Speed = 0


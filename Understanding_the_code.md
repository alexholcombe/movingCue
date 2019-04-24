What draws the cue(s) when not grating?

## Blocks

trialHandlerList = [ trialsStationary, trialsMoving ] #To change the order of blocks, change the order in this list

## Decoy ring programming

constructThickThinWedgeRingsTargetAndCue draws the cue, which is drawn as a radial grating with visibleWedge set to show only the portion of the radial grating that surrounds the future target position.
So I guess I'll need to change this up pretty dramatically to have the radial grating also have angular cycles, and somehow show only the peaks (the bits around the objects), perhaps by using a luminance pedestal if there is a way to do that. Is there a way to do that?

It looks like it can work by first making sure the cueTex is drawn perfectly so don't have to rely on visibleWedge to get angle right, and then making the trough the screen background which it is by default, and setting cycles to number of objects.



What draws the cue(s) when not grating?

## Blocks

trialHandlerList = [ trialsStationary, trialsMoving ] #To change the order of blocks, change the order in this list

## Decoy ring programming

constructThickThinWedgeRingsTargetAndCue draws the cue, which is drawn as a radial grating with visibleWedge set to show only the portion of the radial grating that surrounds the future target position.
So I guess I'll need to change this up pretty dramatically to have the radial grating also have angular cycles, and somehow show only the peaks (the bits around the objects), perhaps by using a luminance pedestal if there is a way to do that. Is there a way to do that?

It looks like it can work by first making sure the cueTex is drawn perfectly so don't have to rely on visibleWedge to get angle right, and then making the trough the screen background which it is by default, and setting cycles to number of objects.

Need to either have different tex for cue ring and decoy ring or need to figure out which angle is visible wedge.  But the cueRing is normally just drawn with one cycle, whereas the decoy ring has numObjects cycles, so they'll never map on. 

Try setting cueRing to numObjects cycles. *Big risk of no longer mapping onto visibleAngle used in previous experiments*, which could screw I-dont-know-what up. Therefore, create a separate decoyTex. Then the only issue should be ensuring that the visible wedge maps directly onto the decoy cue, so that there's no local luminance transient when all the decoys disappear.
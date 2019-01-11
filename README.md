# Programming an experiment on bin colour detection

## MOTIVATION OF THE PROJECT AND DESCRIPTION OF THE TASK:
My goal is to show that subjects better detect red trash bags than grey ones in pictures taken in the streets of Paris, in order to change the mind of the Mairie de Paris regarding the colour choice of trash bags. I am doing an internship with a PhD student who works on this theme. However, she has programmed her experiment on Qualtrics to be exportable to UK participants. My goal is to program it using Python and especially the Expyriment module.

The experiment consists in a succession of trials in which a picture with either a red bin, a grey bin or no bin is flashed (750ms) on the screen and the participant must indicate, by pressing one of two response buttons (A: absent, P: present), if a bin was present or not. The response time is recorded. There is a training block and then 3 identical blocks, to allow for participants to take pauses. Pictures are randomized so that there are pictures of the three types in each block. I am then comparing the hit rates and false alarm rates of pictures with red bins and of those with grey bins. I calculate a d' (see Signal Detection Theory) and I wish to obtain that d'(red) > d'(grey) thus proving that subjects more correctly detect red bins than grey bins.

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Bin Detection Experiment]
    - [Renaming the stimuli]
    - [Loading and randomizing the stimuli]
    - [Preparing the experiment]
    - [Data analysis: signal detection theory]
    - [CONCLUSION]

<!-- markdown-toc end -->

# titre premier
## titre second, etc
_italique_  *italique*
__gras__  **gras**

<pre><code>
insertion de code
</code></pre>


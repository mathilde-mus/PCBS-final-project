# Programming an experiment on bin colour detection

## Motivation for the project and general description of the task

My goal is to show that subjects better detect red trash bags than grey ones in pictures taken in the streets of Paris, in order to change the mind of the Mairie de Paris regarding the colour choice of trash bags. I am doing an internship with a PhD student who works on this theme. However, she has programmed her experiment on Qualtrics to be exportable to UK participants. My goal is to program it using Python and especially the Expyriment module.

The experiment consists in a succession of trials in which a picture with either a red bin, a grey bin or no bin is flashed (750ms) on the screen and the participant must indicate, by pressing one of two response buttons (A: absent, P: present), if a bin was present or not. The response time is recorded. There is a training block and then 3 identical blocks, to allow for participants to take pauses. Pictures are randomized so that there are pictures of the three types in each block. I am then comparing the hit rates and false alarm rates of pictures with red bins and of those with grey bins. I calculate a d' (see Signal Detection Theory) and I wish to obtain that d'(red) > d'(grey) thus proving that subjects more correctly detect red bins than grey bins.


**Table of Contents**

    1. Necessary imports and chosen path
    2.Renaming the stimuli
    3.Loading and randomizing the stimuli
    4.Preparing the experiment
    5.Data analysis: signal detection theory
    6.Conclusion and further analyses

## Necessary imports and chosen path
Here are the imports necessary to the running of the program. The only specific one is norm.ppf from the scipy module. It allows to calculate the d', a discriminability index from Signal Detection Theory estimating the strength of a signal, here that of red bins and grey bins. A big d' for red bin pictures means they are very well detected compared to pictures with no bins.

<pre><code>
import os
import numpy as np
import random
from scipy.stats import norm
import expyriment
from  expyriment.stimuli import Picture, FixCross, BlankScreen
z = norm.ppf

path = "C:/Python_travail/Final_project/"
os.chdir(path)
</code></pre>

## Renaming the stimuli

To simplify further treatment and not to have complex names for the used picture, I first rename my stimuli in a lexicographic order, starting with the initial of the colour of the bin (R for red, G for grey) and N for pictures with no bins.

_italique_  *italique*
__gras__  **gras**

<pre><code>
insertion de code
</code></pre>


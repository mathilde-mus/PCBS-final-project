# Programming an experiment on bin colour detection

## Motivation for the project and general description of the task

My goal is to show that subjects better detect red trash bags than grey ones in pictures taken in the streets of Paris, in order to change the mind of the Mairie de Paris regarding the colour choice of trash bags. I am doing an internship with a PhD student who works on this theme. However, she has programmed her experiment on Qualtrics to be exportable to UK participants. My goal is to program it using Python and especially the Expyriment module.

The experiment consists in a succession of trials in which a picture with either a red bin, a grey bin or no bin is flashed (750ms) on the screen and the participant must indicate, by pressing one of two response buttons (A: absent, P: present), if a bin was present or not. The response time is recorded. There is a training block and then 3 identical blocks, to allow for participants to take pauses. Pictures are randomized so that there are pictures of the three types in each block. I am then comparing the hit rates and false alarm rates of pictures with red bins and of those with grey bins. I calculate a d' (see Signal Detection Theory) and I wish to obtain that d'(red) > d'(grey) thus proving that subjects more correctly detect red bins than grey bins.


**Table of Contents**

    1.Necessary imports and chosen path
    2.Renaming the stimuli
    3.Loading and randomizing the stimuli
    4.Preparing the experiment
    5.Data analysis: signal detection theory
    6.Program execution
    7.Conclusion and further possible analyses

## Necessary imports and chosen path
Here are the imports necessary to the running of the program. The only specific one is norm.ppf from the scipy module. It allows to calculate the d', a discriminability index from Signal Detection Theory estimating the strength of a signal, here that of red bins and grey bins. A big d' for red bin pictures means they are very well detected compared to pictures with no bins.

<pre><code>
import os
import numpy as np
import random
from scipy.stats import norm
import expyriment
from  expyriment.stimuli import Picture, FixCross, BlankScreen
z = norm.ppf  #z is the usual name used in the formula of the d'

path = "C:/Python_travail/Final_project/"
os.chdir(path)
</code></pre>

## Renaming the stimuli

To simplify further treatment and not to have complex names for pictures, I first rename my stimuli in a lexicographic order, starting with the initial of the colour of the bin (R for red, G for grey) and N for pictures with no bins using the following function:

<pre><code>
def rename():
    """ Renames pictures in the form R_000, R_001, ... G_000, G_001, ... N_000,... to simplify further treatment """
    path_stim = "Stimuli/"
    for dossier in ["Red/","Grey/", "Null/"]:
        prefix = dossier[0]+"_"   #gives R,G,N
        count = 0
        path_now = path_stim+dossier
        for filename in os.listdir(path_now):
            suffix = ""
            if count < 10:
                suffix += "0"
            if count < 100:   #Around 150 pictures will be used.
                suffix += "0"
            suffix += str(count)
            count+=1
            os.rename(path_now+filename, path_now+prefix+suffix+".jpg")
</code></pre>

## Loading and randomizing the stimuli

The following functions prepare the pictures that are going to be displayed to participants. 
The first one returns 4 lists: one containing pictures for the training block, one with all pictures with red bins, one with all pictures with grey bins and one with pictures with no bins. 
The second simply returns a randomized version of a list.

<pre><code>
def loading_stim():
    """Preparation of 4 lists that will be used in the experiment: pictures with red bins, pictures with grey bins, pictures with no bins and a training list with all types of pictures for the training block."""
    path_stim = "Stimuli/"
    list_R, list_G, list_N, list_T = [],[],[], []
    for dossier in ["Red/","Grey/", "Null/", "Training/"]:
        path_now = path_stim+dossier
        for filename in os.listdir(path_now):
            if dossier[0] == 'R':
                list_R.append(path_now+filename)
            elif dossier[0] == 'G':
                list_G.append(path_now+filename)
            elif dossier[0] == 'N':
                list_N.append(path_now+filename)
            else:
                list_T.append(path_now+filename)
    return list_R,list_G,list_N, list_T
    
def randomize(list_stim):
    """Randomizes the pictures in a given list"""
    return list(np.random.permutation(list_stim))
</code></pre>

## Preparing the experiment

Here I use the Expyriment module to create an experiment with a training block and three identical treatment blocks, in which the trials are flashed pictures:

<pre><code>
## Preparing the experiment
def setup_trial(filename):
    """Creates a trial that displays a given picture on the screen."""
    trial = expyriment.design.Trial()
    stim = expyriment.stimuli.Picture(filename)
    stim.preload()
    trial.add_stimulus(stim)
    return trial

def setup_block(list_stim, name):
    """Creates a block with trials."""
    block = expyriment.design.Block(name=name)
    for filename in list_stim:
        trial = setup_trial(filename)
        block.add_trial(trial)
    return block

def setup_training(list_stim):
    """Creates the training block."""
    block_training = setup_block(list_stim, "Training Block")
    return block_training


def setup_experiment(list_stim_training,list_stim):
    """Creates an experiment with a training block and then 3 blocks to allow for pauses."""
    exp = expyriment.design.Experiment(name="Bin Detection Experiment")
    expyriment.control.initialize(exp)
    exp.add_block(setup_training(list_stim_training))
    NTRIALS = len(list_stim)//3    
    list1 = list_stim[0:NTRIALS]
    list2 = list_stim[NTRIALS:2*NTRIALS]
    list3 = list_stim[2*NTRIALS:]
    list_tot = [list1, list2, list3]
    
    for i in range(3):
        block = setup_block(list_tot[i], "Block "+str(i+1))  #creating Block 1, Block 2, Block 3
        exp.add_block(block)
    return exp
 </code></pre>
 
 There are three identical blocks to allow participants to take pauses. Thus, the blocks are of identical length and all contain red bin pictures, grey bin ones and no bin ones. I simply divided the set of trials by three.
 
 ## Data analysis: signal detection theory
 
 Here are a set of functions allowing to analyze the data to finally arrive at the difference of dprime between red bin and grey bin pictures.
<pre><code>
## Data analysis
def savetxt(filename,data,delimiter=","):
    """Creates a writing file with string elements seperated by a delimiter."""
    with open(filename,"w") as f:
        for line in data:
            max = len(line) - 1
            count = 0
            for element in line:
                f.write(str(element))
                if count != max: #For the last element, we don't add the delimiter.
                    f.write(delimiter)
                count+=1
            f.write("\n")

def get_ID(filename):
    """Returns the name of a given picture file, thus excluding the extension. For example 'R_001'"""
    return filename[-9:-4] 
    
def get_separate_ID(Picture_ID):
    """Returns the first letter of the colour (R,G,N) of the picture and then the number name of the photo (0,1,2, ...)"""
    return Picture_ID[0], str(int(Picture_ID[-3:]))
        
def answer_data():
    """Returns two dictionaries, one for red bins one for grey bins, with both information on the presence or absence of a bin in the picture and subjects' answers, in the format 1Y-1N-0Y-0N."""
    path_data = "Data_before_treatment/"
    list_files = os.listdir(path_data)
    dic_data_R = {}
    dic_data_G = {}
    
    for filename in list_files:
        with open(path_data+filename, 'r', encoding='UTF-8') as data:
            for line in data:
                Block_name, Picture_ID, Answer, RT = line.split(",")
                if Block_name != "Training Block":   #not analyzing the training block, by definition.
                    couleur, ID = get_separate_ID(Picture_ID)
                    if couleur == "R":
                        dic_data_R[ID] = dic_data_R.get(ID,"")+"1"+Answer+","  #creating a key 'ID' if not existing. 1 or 0 code for the presence or absence of a bin in the picture. The answer is Y or N depending on the subject's answer.
                    elif couleur == "G":
                        dic_data_G[ID] = dic_data_G.get(ID,"")+"1"+Answer+","
                    else:
                        dic_data_R[ID] = dic_data_R.get(ID,"")+"0"+Answer+","
                        dic_data_G[ID] = dic_data_G.get(ID,"")+"0"+Answer+","
    return dic_data_R, dic_data_G
            
def hit_false_rate(data):
    """ Returns hit and false alarm rates of a string of results for one picture."""
    hit = 0
    miss = 0
    rej = 0
    false = 0
    for x in data.split(","):
        if x == "1Y":
            hit += 1
        elif x == "1N" :
            miss +=1
        elif x == "0N":
            rej += 1
        elif x == "0Y":
            false +=1
    return([hit/(hit+miss), false/(false+rej)])

  
def hit_false_rate_multi_data():
    """Returns the mean hit and false alarm rates for red bin pictures and grey bin ones.""" 
    list_hit_R = []
    list_hit_G = []
    list_false_R = []
    list_false_G = []
    dic_data_R, dic_data_G = answer_data()  #creating anwswer dictionnaries.
    for i in range(len(dic_data_R)):  #dic_data_R and dic_data_G have the same length.
        hit_rate_R, false_rate_R = hit_false_rate(dic_data_R[str(i)][:-1]) #not to count the last comma in the data.
        hit_rate_G, false_rate_G = hit_false_rate(dic_data_G[str(i)][:-1])
        list_hit_R.append(hit_rate_R)
        list_hit_G.append(hit_rate_G)
        list_false_R.append(false_rate_R)
        list_false_G.append(false_rate_G)
    return np.mean(list_hit_R), np.mean(list_hit_G), np.mean(list_false_R), np.mean(list_false_G)

def dprime():
    """Returning the difference between the d prime of red bin pictures and grey bin ones."""
    mean_hit_rate_R, mean_hit_rate_G, mean_false_rate_R, mean_false_rate_G = hit_false_rate_multi_data()
    dprime_R = z(mean_hit_rate_R)-z(mean_false_rate_R)  #cf Signal Detection Theory: d' is a discriminability index estimating the strength of a signal, here of red bins.
    dprime_G = z(mean_hit_rate_G)-z(mean_false_rate_G)  
    return dprime_R - dprime_G 
  </code></pre>
  
  ## Program execution
  Here I just run the experiment, that will call all the above created functions:
  <pre><code>
  ## Program execution
if __name__ == "__main__":
    rename()
    list_R, list_G, list_N, list_T = loading_stim()
    list_stim_training = randomize(list_T)
    list_stim = randomize(list_R+list_G+list_N) #randomization accross conditions
    exp = setup_experiment(list_stim_training, list_stim)
    
    cross = FixCross(size=(25, 25), line_width=4)
    blankscreen = BlankScreen()
    
    data = []
    expyriment.control.start(skip_ready_screen = True)
    
    expyriment.stimuli.TextScreen("Welcome in this bin detection experiment.",
        "Your task is to answer P as quickly as possible if you see a bin,red or grey, in the flashed picture and A if you do not. There will be N trials. Press any key to continue.").present()
    exp.keyboard.wait()
    blankscreen.present()
    
    count = 0
    for block in exp.blocks:
        if block.name == 'Training Block':
            expyriment.stimuli.TextScreen("Let us start by a training block."," Press P if you see a bin, A if you do not. Press any key to continue.").present()
            exp.keyboard.wait()
            blankscreen.present()
        if block.name == 'Block 1':
            count = 0  #for knowing which picture is displayed, and not counting those in the training block.
        for trial in block.trials:
            cross.present()
            waitingtime = 1000
            exp.clock.wait(waitingtime)
            trial.stimuli[0].present()
            key, rt = exp.keyboard.wait([expyriment.misc.constants.K_q,
                                        expyriment.misc.constants.K_p], duration=750) #QWERTY keyboard. Case where the subject pressed a key during the display of the image
            if key == None:   #if the subject didn't press a key during the display of the picture
                blankscreen.present()
                key, rt = exp.keyboard.wait([expyriment.misc.constants.K_q,
                                            expyriment.misc.constants.K_p])
                rt+=750  #the picture is displayed for 750ms so it needs to be added to the reaction time
                
            if key == expyriment.misc.constants.K_q:
                Answer = 'N'  #the subject didn't see a bin
            else:
                Answer = 'Y'
            
            Picture_ID = get_ID(list_stim[count])   #eg R_001.jpg -> R_001
            data.append([block.name, Picture_ID, Answer, rt])
            count +=1
        
        if block.name == 'Training Block':
            expyriment.stimuli.TextScreen("You have completed the training block!"," Press any key to start the experiment.").present()
            exp.keyboard.wait()
            blankscreen.present()
       
        if block.name == 'Block 1' or block.name == 'Block 2':
            expyriment.stimuli.TextScreen(
                "You have completed %s !" %block.name,"You may take a break and press any key to continue").present()
            exp.keyboard.wait()
            blankscreen.present()
    
    expyriment.control.end()
    
    savetxt("Data_before_treatment/" + str(exp.subject)+".csv", data, delimiter = ",")  #creating a CSV file for each subject with the 4 measured variables.
    dprime()
  </code></pre>
  
  ## Conclusion and further possible analyzes
 
 


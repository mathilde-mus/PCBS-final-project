""" A series of trials where a picture with either a red bin, a grey bin or no bin is presented at the center of the screen and the participant must press a key if he saw a bin and another if he didn't. A CSV file containing block name, picture ID, participant's answer and reaction time is created at the end of the experiment. Then an analysis using the Signal Detection Theory framework is done, calculating hit and false alarm rates and d primes to see if red bins are better detected than grey ones. """

## Imports et path
import os
import numpy as np
import random
from scipy.stats import norm
import expyriment
from  expyriment.stimuli import Picture, FixCross, BlankScreen
z = norm.ppf  #method calculating a dprime (signal detection theory), and z is the usual name for it in formulas.

path = "C:/Python_travail/Final_project/"
os.chdir(path)

## Rename stimuli (photos)
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

## Loading and randomizing the stimuli
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
    """Returns a randomized version of a given list"""
    return list(np.random.permutation(list_stim))
    
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
    """Creates an experiment with a training block and then 3 identical blocks to allow for pauses."""
    exp = expyriment.design.Experiment(name="Bin Detection Experiment")
    expyriment.control.initialize(exp)
    exp.add_block(setup_training(list_stim_training))
    NTRIALS = len(list_stim)//3    #trials are divided into 3 groups so that the subject can rest, but it is independent of the condition (red/grey/null): all blocks possess all types of pictures.
    list1,list2, list3  = list_stim[0:NTRIALS], list_stim[NTRIALS:2*NTRIALS], list_stim[2*NTRIALS:]
    list_tot = [list1, list2, list3]
    for i in range(3):
        block = setup_block(list_tot[i], "Block "+str(i+1))  #creating Block 1, Block 2, Block 3
        exp.add_block(block)
    return exp

## Data analysis
def get_colour_ID(Picture_ID):
    """Returns the first letter of the colour (R,G,N) of the picture and then the number name of the photo (0,1,2, ...)"""
    return Picture_ID[-9], str(int(Picture_ID[-7:-4]))
        
def answer_data():
    """Returns two dictionaries, one for red bins one for grey bins, with both information on the presence or absence of a bin in the picture and subjects' answers, in the format 1Y-1N-0Y-0N."""
    path_data = "Data_before_treatment/"
    list_files = os.listdir(path_data)
    dic_data_R, dic_data_G = {}, {}
    for filename in list_files:
        with open(path_data+filename, 'r', encoding='UTF-8') as data:
            for line in data:
                Block_name, couleur, ID, Answer, RT = line.split(",")
                if Block_name != "Training Block":   #not analyzing the training block, by definition.
                    if colour == "R":
                        dic_data_R[ID] = dic_data_R.get(ID,"")+"1"+Answer+","  #creating a key 'ID' if not existing. 1 or 0 code for the presence or absence of a bin in the picture. The answer is Y or N depending on the subject's answer.
                    elif colour == "G":
                        dic_data_G[ID] = dic_data_G.get(ID,"")+"1"+Answer+","
                    else:
                        dic_data_R[ID] = dic_data_R.get(ID,"")+"0"+Answer+","
                        dic_data_G[ID] = dic_data_G.get(ID,"")+"0"+Answer+","
    return dic_data_R, dic_data_G
            
def hit_false_rate(data):
    """ Returns hit and false alarm rates of a string of results for one picture."""
    hit, miss, rej, false = 0, 0, 0, 0
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
    list_hit_R, list_hit_G, list_false_R, list_false_G = [], [], [], []
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
    dprime_R, dprime_G  = z(mean_hit_rate_R)-z(mean_false_rate_R), z(mean_hit_rate_G)-z(mean_false_rate_G) #cf Signal Detection Theory: d' is a discriminability index estimating the strength of a signal, here of red bins and grey ones respectively.
    return dprime_R - dprime_G 
   

## Program execution
if __name__ == "__main__":
    rename()
    list_R, list_G, list_N, list_T = loading_stim()
    list_stim_training, list_stim = randomize(list_T), randomize(list_R+list_G+list_N) #randomization accross conditions
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
            count = 0  #to know which picture is displayed, and not counting those in the training block.
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
            colour, ID = get_colour_ID(list_stim[count])   #eg R_001.jpg -> R,1
            data.append([block.name, colour, ID, Answer, rt])
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
    
    np.savetxt("Data_before_treatment/" + str(exp.subject)+".csv",data,delimiter = ",",fmt="%s") #creates a CSV file for each subject with the measured variables in a string format.
    print("\nd'(red bins) - d'(grey bins) = ", dprime())  #if positive, our research hypothesis is true
   

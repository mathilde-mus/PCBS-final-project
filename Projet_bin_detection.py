""" Explanation of project"""

## Imports et path
import os
import numpy as np
import random
from scipy.stats import norm
import expyriment
from  expyriment.stimuli import Picture, FixCross, BlankScreen
z = norm.ppf

path = "C:/Python_travail/Final_project/"
os.chdir(path)

## Rename stimuli (photos)
""" explanation """

def rename(path):
    """explanation"""
    path_stim = path + "Stimuli/"
    for dossier in ["Red/","Grey/", "Null/"]:
        prefix = dossier[0]+"_"   #donne R,G,N
        count = 0
        path_now = path_stim+dossier
        for filename in os.listdir(path_now):
            suffix = ""
            if count < 10:
                suffix += "0"
            if count < 100:
                suffix += "0"
            suffix += str(count)
            count+=1
            os.rename(path_now+filename, path_now+prefix+suffix+".jpg")   #R000, R001, ... N000, N001, ...

## Loading and randomizing the stimuli
"""explanation"""
 
def loading_stim(path):
    """explanation"""
    path_stim = path + "Stimuli/"
    list_R, list_G, list_N = [],[],[]
    for dossier in ["Red/","Grey/", "Null/"]:
        path_now = path_stim+dossier
        for filename in os.listdir(path_now):
            if dossier[0] == 'R':
                list_R.append(path_now+filename)
            elif dossier[0] == 'G':
                list_G.append(path_now+filename)
            else:
                list_N.append(path_now+filename)
    return list_R,list_G,list_N
    
def loading_training(path):
    path_stim = path + "Stimuli/Training/"
    list_training = []
    for filename in os.listdir(path_stim):
        list_training.append(path_stim+filename)
    return list_training
    
    
def randomize(list_stim):
    """herie"""
    return list(np.random.permutation(list_stim))
    
## Preparing the experiment
"""heheh"""

def setup_trial(filename):
    trial = expyriment.design.Trial()
    stim = expyriment.stimuli.Picture(filename)
    stim.preload()
    trial.add_stimulus(stim)
    return trial

def setup_block(list_stim, name):
    block = expyriment.design.Block(name=name)
    for filename in list_stim:
        trial = setup_trial(filename)
        block.add_trial(trial)
    return block

def setup_training(list_stim):
     block_training = setup_block(list_stim, "Training Block")
     return block_training


def setup_experiment(list_stim_training,list_stim):
    exp = expyriment.design.Experiment(name="Bin Detection Experiment")
    expyriment.control.initialize(exp)
    exp.add_block(setup_training(list_stim_training))
    NTRIALS = len(list_stim)//3
    list1 = list_stim[0:NTRIALS]
    list2 = list_stim[NTRIALS:2*NTRIALS]
    list3 = list_stim[2*NTRIALS:]
    list_tot = [list1, list2, list3]
    
    for i in range(3):
        block = setup_block(list_tot[i], "Block "+str(i+1))
        exp.add_block(block)
    return exp

## Data analysis
def savetxt(filename,data,delimiter=","):
    with open(filename,"w") as f:
        for line in data:
            max = len(line) - 1
            count = 0
            for element in line:
                f.write(str(element))
                if count != max: #Dans le cas du dernier élément, on ajoute pas la ','
                    f.write(delimiter)
                count+=1
            f.write("\n")

def get_ID(filename):
    return filename[-9:-4] 
    
def get_separate_ID(Picture_ID):
    return Picture_ID[0], str(int(Picture_ID[-3:]))
        
def answer_data(path):
    path_data = path+"Data_before_treatment/"
    list_files = os.listdir(path_data)
    dic_data_R = {}
    dic_data_G = {}
    
    for filename in list_files:
        with open(path_data+filename, 'r', encoding='UTF-8') as data:
            for line in data:
                Block_name, Picture_ID, Answer, RT = line.split(",")
                if Block_name != "Training Block":
                    couleur, ID = get_separate_ID(Picture_ID)
                    if couleur == "R":
                        dic_data_R[ID] = dic_data_R.get(ID,"")+"1"+Answer+","
                    elif couleur == "G":
                        dic_data_G[ID] = dic_data_G.get(ID,"")+"1"+Answer+","
                    else:
                        dic_data_R[ID] = dic_data_R.get(ID,"")+"0"+Answer+","
                        dic_data_G[ID] = dic_data_G.get(ID,"")+"0"+Answer+","
    return dic_data_R, dic_data_G
            
def hit_false_rate(data):
    """ Prints the hit rate and the false rate of a string of results in a detecton task"""
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

  
def hit_false_rate_multi_data(path):
    """Prints the mean and standard deviations of hit and false alarm rates on all participants and draws the graph (false alarm rate, hit rate) where each participant is a dot""" 
    list_hit_R = []
    list_hit_G = []
    list_false_R = []
    list_false_G = []
    dic_data_R, dic_data_G = answer_data(path)
    for i in range(len(dic_data_R)):
        hit_rate_R, false_rate_R = hit_false_rate(dic_data_R[str(i)][:-1]) #pour ne pas compter la dernière virgule
        hit_rate_G, false_rate_G = hit_false_rate(dic_data_G[str(i)][:-1])
        list_hit_R.append(hit_rate_R)
        list_hit_G.append(hit_rate_G)
        list_false_R.append(false_rate_R)
        list_false_G.append(false_rate_G)
    return np.mean(list_hit_R), np.mean(list_hit_G), np.mean(list_false_R), np.mean(list_false_G)

def dprime(path):
    mean_hit_rate_R, mean_hit_rate_G, mean_false_rate_R, mean_false_rate_G = hit_false_rate_multi_data(path)
    dprime_R = z(mean_hit_rate_R)-z(mean_false_rate_R)
    dprime_G = z(mean_hit_rate_G)-z(mean_false_rate_G)  
    return dprime_R - dprime_G 
   

## Program execution
if __name__ == "__main__":
    rename(path)
    list_R, list_G, list_N = loading_stim(path)
    list_stim_training = randomize(loading_training(path))
    list_stim = randomize(list_R+list_G+list_N)
    exp = setup_experiment(list_stim_training, list_stim)
    
    cross = FixCross(size=(25, 25), line_width=4)
    blankscreen = BlankScreen()
    
    data = []
    
    
    expyriment.control.start(skip_ready_screen = True)
    
    expyriment.stimuli.TextScreen(
        "Your task is to answerY",
        "Press a key as quickly as possible in case you see a bin. There will be N trials ").present()
    exp.keyboard.wait()
    blankscreen.present()
    
    count = 0
    for block in exp.blocks:
        if block.name == 'Training block':
            expyriment.stimuli.TextScreen("hreihrie").present()
        
        if block.name == 'Block 1':
            count = 0
        for trial in block.trials:
            cross.present()
            waitingtime = 500 + int(1000 * random.expovariate(1))
            exp.clock.wait(waitingtime)
            trial.stimuli[0].present()
            key, rt = exp.keyboard.wait([expyriment.misc.constants.K_a,
                                        expyriment.misc.constants.K_p], duration=500)
            if key == None:
                blankscreen.present()
                key, rt = exp.keyboard.wait([expyriment.misc.constants.K_a,
                                            expyriment.misc.constants.K_p])
                rt+=500
                
            if key == expyriment.misc.constants.K_a:
                Answer = 'N'
            else:
                Answer = 'Y'
            
            Picture_ID = get_ID(list_stim[count])   
            data.append([block.name, Picture_ID, Answer, rt])
            count +=1
        
        if block.name == 'Training block':
            expyriment.stimuli.TextScreen("hreihrie").present()
       
        if block.name == 'Block 1' or block.name == 'Block 2':
            expyriment.stimuli.TextScreen(
                "You have completed %s !" %block.name,"You may take a break and press any key to continue").present()
            exp.keyboard.wait()
            blankscreen.present()
    
    expyriment.control.end()
    
    savetxt("Data_before_treatment/" + str(exp.subject)+".csv", data, delimiter = ",")
    

    
    



                
    
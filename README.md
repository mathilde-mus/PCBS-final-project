# Programming an experiment on bin colour detection

## Motivation for the project and general description of the task

My goal is to show that subjects are better at detecting red trash bags than grey ones in pictures taken in the streets of Paris, in order to change the mind of the Mairie de Paris regarding the colour choice of trash bags. I am doing an internship with a PhD student who works on this theme. However, she has programmed her experiment on Qualtrics to be exportable to UK participants. My goal is to program it using Python and especially the Expyriment module.

The experiment consists in a succession of trials in which a picture containing either a red bin, a grey bin or no bin is flashed (750ms) on the screen and the participant must indicate, by pressing one of two response buttons (A: absent, P: present), if a bin was present or not. The response time is recorded. There is a training block and then 3 identical blocks, to allow for breaks. Pictures are randomized so that there are pictures of the three types in each block. I am then comparing the hit rates and false alarm rates of pictures with red bins and of those with grey bins. I calculate a d' (see Signal Detection Theory) and I wish to obtain that d'(red) > d'(grey), thus proving that subjects more correctly detect red bins than grey bins on average.


**Table of Contents**

    1.Renaming the stimuli
    2.Loading and randomizing the stimuli
    3.Preparing the experiment
    4.Data analysis: signal detection theory
    5.Program execution
    6.Further possible analysis
    7.Feedback
    

## Renaming the stimuli

To simplify further treatment and not to have complex names for pictures, I first created a function that renames the stimuli in a lexicographic order, starting with the initial of the colour of the bin (R for red, G for grey) and N for pictures with no bins: R_000, R_001, ..., G_000, G_001, ..., N_000, N_001, etc. Around 150 pictures will be flashed (hence the double 0).

## Loading and randomizing the stimuli

I choose to preload pictures in order not to add delay in the experiment. I thus create a first function that returns 4 lists: one containing pictures for the training block, one with all pictures with red bins, one with all pictures with grey bins and one with pictures with no bins. Here it is:
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
</code></pre>

I then create a function that randomizes a list of stimuli, so that no influence of order appears in the results.

## Preparing the experiment

I then use the Expyriment module to create an experiment with a training block and three identical treatment blocks, in which the trials are flashed pictures. The first function creates trials, the second treatment blocks, the third the training block and the last one creates the experiment:
<pre><code>
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
 
There are three identical blocks to allow participants to take breaks. Thus, the blocks are of identical length and all contain red bin pictures, grey bin ones and no bin ones. I simply divided the set of trials by three.
 
## Data analysis: signal detection theory
 
 Here are several functions useful for encoding the data and treating it. I want to encode participants' answers as a string with answers for each picture delimitated by commas. Answers per picture would write as two strings, one stating if a bin was present (red or grey) or not encoded as 1 or 0, and the other giving the participant's anwser (Y if he said he detected a bin, N otherwise). It will thus look as the folowing "1Y,0N,1N,1Y,0Y, ...". The answers are encoded separately depending on bin colour:
<pre><code>       
def answer_data():
    """Returns two dictionaries, one for red bin pictures one for grey bin ones, with both information on the presence or absence of a bin in the picture (1 or 0) and subjects' answers (Y or N) in the format '1Y,1N,0Y,0N'."""
    path_data = "Data_before_treatment/"
    list_files = os.listdir(path_data)
    dic_data_R, dic_data_G = {}, {}
    for filename in list_files:
        with open(path_data+filename, 'r', encoding='UTF-8') as data:
            for line in data:
                Block_name, colour, ID, Answer, RT = line.split(",")
                if Block_name != "Training Block":   #not analyzing the training block, by definition.
                    if colour == "R":
                        dic_data_R[ID] = dic_data_R.get(ID,"")+"1"+Answer+","  #creating a key 'ID' if not existing. 1 or 0 code for the presence or absence of a bin in the picture. The answer is Y or N depending on the subject's answer.
                    elif colour == "G":
                        dic_data_G[ID] = dic_data_G.get(ID,"")+"1"+Answer+","
                    else:
                        dic_data_R[ID] = dic_data_R.get(ID,"")+"0"+Answer+","
                        dic_data_G[ID] = dic_data_G.get(ID,"")+"0"+Answer+","
    return dic_data_R, dic_data_G
  </code></pre>
            
I then use the function that we already wrote in class to calculate hit and false alarm rates (hit_false_rate(data)) from a data string and an adapted version of the function calculating them on average for all subjects:
<pre><code> 
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
  </code></pre>
I finally compute the d' of pictures with red bins and substract from it that of pictures with grey bins, hoping to obtain a positive difference. I use the norm.ppf (called z here, as in the literature) function of the scipy module to do so:
<pre><code> 
def dprime():
    """Returning the difference between the d prime of red bin pictures and grey bin ones."""
    mean_hit_rate_R, mean_hit_rate_G, mean_false_rate_R, mean_false_rate_G = hit_false_rate_multi_data()
    dprime_R, dprime_G  = z(mean_hit_rate_R)-z(mean_false_rate_R), z(mean_hit_rate_G)-z(mean_false_rate_G) #cf Signal Detection Theory: d' is a discriminability index estimating the strength of a signal, here of red bins and grey ones respectively.
    return dprime_R - dprime_G 
  </code></pre>
  
## Program execution
  The last part is about running the experiment, that will call all the above created functions:
  <pre><code>
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
    print("\nd'(red bins) - d'(grey bins) = ", dprime()) #if positive, our research hypothesis is right   
  </code></pre>
  
## Further possible analysis
  With more time, it would have been interesting to do a second version of the data analysis using R for example, to easily run significance tests (for the difference of d' especially).
  
  Also, reaction times are measured but not analyzed here. It would be interesting to see if on average, participants respond faster for pictures with red bins than for pictures with grey bins, an information that would support our hypothesis that red bins are better detected.
  
## Feedback
### My level in programming
I started coding in *classe préparatoire*, on Python. I learnt how to write functions, loops, how to manipulate lists, use imported modules, and debug easy bugs. So I had simply the basics before this class. I had no notion of prompts nor text editors such as Markdown for instance.

### What I learnt from this class/project
 During classes, I learnt to write an organized code (for example, use the "if name == main" and run the execution afterwards), to use paths, to open and write files, etc. I discovered useful modules for coding in cognitive science such as Expyriment and Pygame.
  In this project particularly, I learnt to code more clearly, with identifiable steps just like in an essay: prepare the stimuli, prepare the trials, the blocks, the data analysis functions, etc and end with the execution. I feel more confident in coding psychological experiments, even though the one I wrote was quite basic but it allowed me to master better the Expyriment module that I didn't know at all before. It also allowed me master better dictionnaries (used to encode data here) and lists. I also learnt to work more rigorously with paths: in an experiment with different types of pictures, with data saving, etc. organization saves time and trouble! I finally learnt to use Markdown and its basic commands, and to create an html page.
  
### Suggested improvements
I think that basic exercises on functions, lists, etc. should be mandatory each week (it was great when we had to do it). Many people start this class without any background in programming (maybe a test could be done in the first class and exercises of different difficulty should be proposed to different level groups). I also think that the lesson should be more structured: we see one module and have a couple of exercises associated to it, then we see another notion, etc. with a growing difficulty, but I know it is hard due to the heterogeneity of the class.
  
 
 


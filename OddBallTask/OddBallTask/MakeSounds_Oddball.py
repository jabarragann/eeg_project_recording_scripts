import numpy as np
import random

def create_sequence_of_deviant(num_s,ratio_deviant,seed):
    if seed is not None:
        random.seed(seed)

    l =  list(range(5, num_s))
    deviants = []

    nu_deviants = int(num_s * ratio_deviant)

    while len(deviants) < nu_deviants:
        x = random.sample(l,1)[0]
        if not any([i in deviants for i in range(x-3,x+4)]):
            deviants.append(x)
            try:
                [l.remove(j) for j in range(x-2,x+3)]
            except Exception as e:
                pass
    deviants = np.sort(np.array(deviants))
    return deviants

def create_sequence_of_deviant_with_multiple(num_s,ratio_deviant,seed):
    if seed is not None:
        random.seed(seed)

    l =  list(range(5, num_s))


    deviants = []
    type_of_alarm = []

    nu_deviants = int(num_s * ratio_deviant)
    random.random()
    while len(deviants) < nu_deviants:
        x = random.sample(l,1)[0]
        type = random.random()

        if not any([i in deviants for i in range(x-1,x+2)]):
            deviants.append(x)
            type_of_alarm.append("a" if type > 0.5 else "b")
            # type_of_alarm.append("a")
            try:
                [l.remove(j) for j in range(x-1,x+2)]
            except Exception as e:
                pass
    deviants = np.sort(np.array(deviants))
    type_of_alarm = np.array(type_of_alarm)

    return deviants, type_of_alarm

def create_sounds(freq, duration):
    #Sounds parameters
    Fs = 44100
    dt = 1 / Fs
    duration = duration / 1000  # in seconds
    t_simple = np.arange(dt, duration, dt)
    fade = 0.01
    amplification_f = 16383
    ramp = np.linspace(0, 1, int(fade / dt))
    pad_l = 300  # zero padding at the end of sound
    sound_len = int(Fs * duration + pad_l - 1)

    # create sounds:
    S = np.zeros((len(freq), sound_len))
    for sind in range(S.shape[0]):

        sound_temp = np.sin(2 * np.pi * freq[sind] * t_simple) * amplification_f
        sound_temp = np.multiply(sound_temp, np.concatenate([ramp, np.ones(len(t_simple) - 2 * len(ramp)), ramp[::-1]]))
        S[sind] = np.concatenate([sound_temp, np.zeros(pad_l)])

    return S
def MakeSounds_Oddball(nu_sounds, nu_blocks, duration, freq,ratio_deviant, p_id):

    Fs = 44100
    dt = 1/Fs
    duration = duration/1000 # in seconds
    t_simple = np.arange(dt, duration, dt)
    fade = 0.01
    amplification_f = 16383
    ramp = np.linspace(0,1,int(fade/dt))
    pad_l = 300 # zero padding at the end of sound
    sound_len = int(Fs*duration+pad_l-1)

    #initialize the block order. For reproducibility, reset the seed according to P_ID:
    np.random.seed(p_id)
    rind = np.arange(2)
    np.random.shuffle(rind)

    # create sounds:
    S = np.zeros((len(freq), sound_len))
    for sind in range(S.shape[0]):
        sound_temp = np.zeros(sound_len-pad_l-1)
        sound_temp = np.sin(2*np.pi*freq[rind[sind]]*t_simple)*amplification_f
        sound_temp = np.multiply(sound_temp, np.concatenate([ramp, np.ones(len(t_simple) - 2*len(ramp)), ramp[::-1]]))
        S[sind] = np.concatenate([sound_temp, np.zeros(pad_l)])

    Sounds = np.zeros((nu_blocks, nu_sounds, sound_len))
    Dev = np.zeros((nu_blocks, int(nu_sounds*ratio_deviant)))
    Freq_Dev = np.zeros(nu_blocks)

    for bl in range(nu_blocks):
        print(bl)
        Sounds_prep = np.zeros((nu_sounds, sound_len))
        #randomize position of deviants:
        iind = np.sort(np.array(random.sample(range(0,nu_sounds),int(nu_sounds*ratio_deviant))))
        # make sure that we don't have consecutive deviants:
        while any(np.diff(iind) <= 1) or iind[0] < 2:
            iind = np.sort(np.array(random.sample(range(0,nu_sounds),int(nu_sounds*ratio_deviant))))

        Sounds_prep[::] = S[bl%S.shape[0]] # alternate the role of standard/deviants in each block
        Sounds_prep[np.array(iind)] = S[~bl%S.shape[0]] # replace the deviant sounds now
        Dev[bl][::] = iind # keep track of deviant indexes
        Freq_Dev[bl] = freq[bl%S.shape[0]] # and of deviant frequencies
        Sounds[bl] = Sounds_prep

    return [Dev, Freq_Dev, Sounds]

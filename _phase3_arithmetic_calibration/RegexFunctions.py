import re

def get_information(file):
    uid = re.findall('.+(?=_S[0-9]+_T[0-9]+_)', file.name)[0]
    session = int(re.findall('(?<=_S)[0-9]+(?=_T[0-9]+)', file.name)[0])
    trial = int(re.findall('(?<=_S[0-9]{2}_T)[0-9]+(?=_)', file.name)[0])
    task = re.findall('(?<=_S[0-9]{2}_T[0-9]{2}_).+(?=_raw\.xdf)', file.name)[0]

    return uid, session, trial, task

def get_information2(file):
    uid = re.findall('.+(?=_SRE+_T[0-9]{3}_)', file.name)[0]
    session = "RE"
    trial = int(re.findall('(?<=_SRE_T)[0-9]{3}(?=_)', file.name)[0])
    task = re.findall('(?<=_SRE_T[0-9]{3}_).+(?=\.xdf)', file.name)[0]

    return uid, 99, trial, task


def get_information3(file):
    uid = re.findall('.+(?=_S[0-9]+_T[0-9]+_)', file.name)[0]
    session = int(re.findall('(?<=_S)[0-9]+(?=_T[0-9]+)', file.name)[0])
    trial = int(re.findall('(?<=_S[0-9]{1}_T)[0-9]+(?=_)', file.name)[0])
    task = re.findall('(?<=_S[0-9]{1}_T[0-9]{3}_).+(?=\.xdf)', file.name)[0]

    return uid, session, trial, task

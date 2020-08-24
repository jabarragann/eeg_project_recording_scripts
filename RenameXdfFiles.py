from pathlib import Path
import re
from shutil import copyfile

experiment = 2
task_dict = {1:'pegNormal',
             2:'pegNback',
             3:'pegCount',
             4:'sutureNormal',
             5:'sutureNback',
             6:'sutureCount',
             7: 'pegNormal',
             8: 'pegNback',
             9: 'pegCount',
             10: 'sutureNormal',
             11: 'sutureNback',
             12: 'sutureCount'}

# experiment = 1
# task_dict = {1:'pegNormal',
#              2:'pegInversion',
#              3:'pegNormal',
#              4:'pegInversion',
#              5:'pegNormal',
#              6:'pegInversion'}

if __name__ == '__main__':

    srcP  = Path('./data-to-rename/')
    dstP  = Path('./data/')
    for idx, file in enumerate(srcP.glob('*.xdf')):

        # Rename files --> remove identifiers
        uid = re.findall('.+(?=_S[0-9]+_T0[0-9][0-9]_)', file.name)[0]
        session = re.findall('(?<=_S)[0-9]+(?=_T0[0-9][0-9]_)', file.name)[0]
        trial = re.findall('(?<=_S[0-9]{2}_T)[0-9]{3}(?=_)', file.name)[0]
        task = re.findall('(?<=_S[0-9]{2}_T[0-9]{3}_).+(?=.xdf)', file.name)[0]

        if task != 'Baseline':
            task = task_dict[int(trial)]

        uid_number =  re.findall('[0-9]+', uid)[0]
        new_file_name = "EX{:d}U{:02d}_S{:02d}_T{:02d}_{:}_raw.xdf".format(experiment, int(uid_number),int(session),int(trial),task)
        copyfile(file,dstP/new_file_name)

        # print(idx, 'U{:02d}'.format(int(uid_number)), session, trial, task)
        # print(file.name)
        # print(new_file_name)
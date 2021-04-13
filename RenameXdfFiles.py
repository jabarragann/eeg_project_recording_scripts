from pathlib import Path
import re
from shutil import copyfile

# experiment = 6
# task_dict = {1:'PickingWithBlood',
#              2:'P1cking',
#              3:'PickingWithBlood',
#              4:'P1cking',
#              5:'PickingWithBlood',
#              6:'P1cking',
#              }


# experiment = 6
# task_dict = {1:'PickingWithBlood',
#              2:'CloseEyes',
#              3:'OpenEyes',
#              4:'CloseEyes',
#              5:'OpenEyes',
#              6:'CloseEyes',
#              }

experiment = 5
task_dict = {1:'NeedlePassing',
             2:'BloodNeedle',
             3:'NeedlePassing',
             4:'BloodNeedle',
             5: 'NeedlePassing',
             6: 'BloodNeedle',
             7: 'NeedlePassing',
             8: 'BloodNeedle',
             9:'NeedlePassing',
             10:'BloodNeedle',
             }

# experiment = 4
# task_dict = {1:'PegTransfer',
#              2:'RunningSuture',
#              3:'KnotTying',
#              4:'PegTransfer',
#              5:'RunningSuture',
#              6:'KnotTying',
#              7: 'PegTransfer',
#              8: 'RunningSuture',
#              9: 'KnotTying',
#              10: 'PegTransfer',
#              11: 'RunningSuture',
#              12: 'KnotTying',
#              13: 'PegTransfer',
#              15: 'KnotTying'}

# experiment = 3
# task_dict = {1:'EasyAdd',
#              2:'HardMult',
#              3:'EasyAdd',
#              4:'HardMult',
#              5:'EasyAdd',
#              6:'HardMult',
#              7: 'EasyAdd',
#              8: 'HardMult',
#              9: 'EasyAdd',
#              10: 'HardMult',
#              11: 'EasyAdd',
#              12: 'HardMult'}

# experiment = 2
# task_dict = {1:'pegNormal',
#              2:'pegNback',
#              3:'pegCount',
#              4:'sutureNormal',
#              5:'sutureNback',
#              6:'sutureCount',
#              7: 'pegNormal',
#              8: 'pegNback',
#              9: 'pegCount',
#              10: 'sutureNormal',
#              11: 'sutureNback',
#              12: 'sutureCount'}

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
        trial = re.findall('(?<=_S[0-9]{1}_T)[0-9]{3}(?=_)', file.name)[0]
        task = re.findall('(?<=_S[0-9]{1}_T[0-9]{3}_).+(?=.xdf)', file.name)[0]

        if task != 'Baseline':
            task = task_dict[int(trial)]

        uid_number = None
        assert experiment in [1,2,3,4,5,6], "Incorrect experiment number"
        if experiment == 1:
            uid_number = re.findall('[0-9]+', uid)[0]
            new_file_name = "UI{:02d}_S{:d}_T{:d}_{:}_raw.xdf".format( int(uid_number), int(session), int(trial), task)
        elif experiment == 2:
            uid_number = re.findall('[0-9]+', uid)[0]
            new_file_name = "U{:02d}_S{:d}_T{:02d}_{:}_raw.xdf".format( int(uid_number), int(session), int(trial), task)
        elif experiment == 3 or experiment == 4 or experiment == 5 or experiment == 6 :
            new_file_name = "{:}_S{:02d}_T{:02d}_{:}_raw.xdf".format( uid, int(session), int(trial), task)

        copyfile(file,dstP/new_file_name)

        # print(idx, 'U{:02d}'.format(int(uid_number)), session, trial, task)
        print(idx, '{:}'.format(uid, session, trial, task))
        print(uid, session, trial, task)
        # print(file.name)
        # print(new_file_name)
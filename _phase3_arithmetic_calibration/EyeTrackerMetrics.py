import traceback
from pathlib import Path
import pandas as pd
import numpy as np
from scipy.spatial import KDTree


class fixation_dector:
    def __init__(self, eyeright, eyeleft, time):
        self.eyeleft = np.array(eyeleft)
        self.eyeright = np.array(eyeright)
        self.time = np.array(time)

    def remove_missing(self, missing=0):
        mx = np.array(np.array(self.eyeleft) == missing, dtype=int)
        my = np.array(np.array(self.eyeright) == missing, dtype=int)
        self.eyeleft = self.eyeleft[(my + mx) != 2]
        self.eyeright = self.eyeright[(my + mx) != 2]
        self.time = self.time[(mx + my) != 2]
        return self.eyeleft, self.eyeright, self.time

    def fixation_dection(self, mindur=85):
        x, y, time = self.remove_missing(missing=0)
        Sfix = []
        Efix = []
        si = 0
        fixationstart = False
        for i in range(1, len(x)):
            try:
                gap = np.abs(int((time[i - 1] - time[i])))
                if gap <= mindur and not fixationstart:
                    fixationstart = True
                    Sfix.append(time[i])
                if gap > mindur and fixationstart:
                    fixationstart = False
                    Efix.append([Sfix[-1], time[i - 1], int(time[i - 1] - Sfix[-1]), x[i], y[i]])
            except KeyError:
                traceback.print_exc()
            except Exception:
                traceback.print_exc()

        return Efix

    def fixation_distance(self, a, b):
        dis = np.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)
        return dis

    def sp_calculation(self, fixationposition):
        scanpth = 0
        for i in range(0, len(fixationposition) - 1):
            scanpth = self.fixation_distance(fixationposition[i + 1], fixationposition[i]) + scanpth
        return scanpth

    def scanpath_eye(self, mindur=85):
        fixation = self.fixation_dection(mindur)
        df = pd.DataFrame(data=fixation, columns=['starttime', 'endtime', 'duration',
                                                  'posx', 'posy'])
        sp = self.sp_calculation(np.array(df[['posx', 'posy']]))
        return sp

class NNI:
    def __init__(self,fixation_array,screen_dimension):
        #super().__init__(fixation_array)
        self.screen_dm = screen_dimension
        self.fixation_array=fixation_array

    def compute(self):
        """Computes the nni metric
        Returns
        -------
        float
            NNI value
        """
        temp_fixation_array = np.copy(self.fixation_array)
        dist_list = []

        for pos,(x,y) in enumerate(self.fixation_array):
            #remove point from array
            temp_fixation_array = np.delete(temp_fixation_array,pos,0)
            pt = [x,y]
            #find the distance to the nearest neighbor
            dist = self._find_neighbor_distance(temp_fixation_array,pt)

            dist_list.append(dist)

            #restoring the list with all the points
            temp_fixation_array = np.copy(self.fixation_array)

        dNN = np.mean(dist_list)
        dran = 0.5 * np.sqrt((self.screen_dm[0]*self.screen_dm[1]) /len(dist_list))

        return dNN/dran


    def _find_neighbor_distance(self,A,pt):
        """find the distance between a point and its nearest neighbor

        Parameters
        ----------
        A : numpy array
            array containing the X,Y positions
        pt : list
            list representing a point[X,Y]

        Returns
        -------
        distance
            euclidean distance
        """
        if len(pt) > 2 or len(pt) < 2:
            raise Exception('List must have length of 2')

        if A.shape[1] > 2 or  A.shape[1] < 2 :
            raise Exception('A must have a dim of shape (n,2)')

        distance,index = KDTree(A).query(pt)
        return distance

def create_feature(df):
    detector = fixation_dector(df['gpx'].values, df['gpy'].values, df['LSL_TIME'].values * 1000)
    fix_array = detector.fixation_dection(mindur=85)
    fix_array = np.array(fix_array)

    fix_pos = fix_array[:, [3, 4]]
    nni = NNI(fix_pos, (1, 1))

    nni_value = nni.compute()
    ssp = detector.scanpath_eye(mindur=85)
    numb_of_fixations = fix_array.shape[0]
    average_fix = fix_array[:, 2].mean()

    results = pd.DataFrame(np.array([numb_of_fixations,average_fix,ssp,nni_value]).reshape(1,4)
                           ,columns=["number_of_fix","average_fix","ssp","nni_value"])
    return results

def split_into_epochs(df):
    df['NORMAL_TIME'] = df['LSL_TIME'] - df['LSL_TIME'].values[0]
    event = [12.5]
    count = 12.5
    epochs = []
    while event[-1] < df['NORMAL_TIME'].values[-1]:
        event.append(count)
        e = df.loc[(df['NORMAL_TIME'] > count-12.5) & (df['NORMAL_TIME'] < count+12.5)]
        epochs.append(e)
        count += 12.5
    return epochs

if __name__ == "__main__":

    path = Path(r'C:\Users\asus\PycharmProjects\EEG-recording-lsl\_phase3_arithmetic_calibration\eye_tracker_txt')
    path = path / 'UJing_S02_T01_NeedlePassing_gaze_position.txt'
    df = pd.read_csv(path, index_col=[0])

    epochs = split_into_epochs(df)
    df = df.loc[(df['LSL_TIME'] - df['LSL_TIME'].values[0]) < 25]

    results = []
    for i in range(len(epochs)):
        e = epochs[i]
        r = create_feature(e)
        results.append(r)
    results = pd.concat(results)

    x = 0
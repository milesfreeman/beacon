
import sqlite3 as lite
import glob
import datetime as dt
import zipfile
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
# coding: utf-8

cursor = None
num_entries = 0
dict = {}

def process_entry(entry):
    global num_entries, cursor,
    num_entries += 1
    if cursor:
        command = """ INSERT INTO Entries (Id, SrcIP, SrcPort, DestIP, DestPort)
                  VALUES """
        command += '(' + str(num_entries) + ', '
        command += '"' + entry[19][6:] + '", '
        command += str(entry[20][8:]) + ', '
        command += '"' + entry[22][6:] + '", '
        command += str(entry[23][8:]) + ');'
        cursor.execute(command)
    else :
        destip = entry[27][11:]
        srcip = entry[19][6:]
        sentbyte = entry[34][9:]
        entry_date = map(int, entry[4][5:].split('-'))
        entry_time = map(int, entry[5][5:].split(':'))
        date = dt.datetime(entry_date[0], entry_date[1], entry_date[2], entry_time[0], entry_time[1], entry_time[2])
        if destip in dict:
            if srcip in dict[destip]:
                (dict[destip])[srcip].append((num_entries, (dict[destip])[srcip][0][0] - date, sentbyte))
                (dict[destip])[srcip][0] = (date, (dict[destip])[srcip][0][1] + 1)
            else:
                (dict[destip])[srcip] = [(date, 1), (num_entries, dt.timedelta(), sentbyte)]
        else:
            dict[destip] = {srcip: [(date, 1), (num_entries, dt.timedelta(), sentbyte)]}


def process_file(path):
    try:
        f = open(path, "r")
        try:
            f.readline()
            f.readline()
            while 1 :
                line = f.readline()
                if not line: break
                process_entry(line.split())
        finally:
            f.close()
    except IOError:
        pass

def analyse_keys():
    global dict
    keys = dict.keys()
    plotted = 0
    for key in keys:
        srckeys = dict[key].keys()
        for srckey in srckeys:
            if dict[key][srckey][0][1] > 100:
                x = np.array(range(dict[key][srckey][0][1]))
                y = [np.abs(z[1].total_seconds()) for z in dict[key][srckey][1:]]
                try:
                    r = [float(t[2]) / 1000 for t in dict[key][srckey][1:]]
                except ValueError :
                    print('Type Conversion Error')
                    break;
                coeff = 1.0 / (1.005 ** (len(np.unique(y)) * len(np.unique(r))))
                if coeff < 0.9 : continue
                m = np.matrix([r,x,y])
                m_x = []
                for i in range(len(x)):
                    if not y[i] : m_x.append(i)
                m = np.delete(m, m_x, axis=1)
                fig = plt.figure()
                ax = fig.add_subplot(111, projection='3d')
                [a,b,c] = [np.array(m[0]).flatten(),np.array(m[1]).flatten(),np.array(m[2]).flatten()]
                ax.plot(a,b,c)
                ax.set_xlabel('B_t = Packet size (kb)')
                ax.set_ylabel('T = Instance: t')
                ax.set_zlabel('\lambda_T = Waiting time (sec)')
                fig.suptitle('Src: ' + 'xxx.xxx.' + srckey[8:] + ', Dst: ' + key + ', Coeff: {:.3f}'.format(coeff))
                fig.savefig('analysis/' + str(plotted) + '.png')
                plotted += 1

def main(folder, database):
    global dict
    if database:
        try:
            global cursor
            connection = lite.connect(database)
            cursor = connection.cursor()
            cursor.execute("CREATE TABLE Entries(Id INT, SrcIP VARCHAR(15), SrcPort INT, DestIP VARCHAR(15), DestPort INT)")
        except lite.Error, e:
            print('failed to connect to' + database)
    zips = glob.glob(folder + '/*.zip')
    for zip in zips:
        with ZipFile(zip) as z:
            logs = z.namelist()
            for log in logs:
                print('Reading ' + log)
                process_file(log)
            z.close()
    if !database:
        analyse_keys()
    else:
        connection.commit()
        connection.close()

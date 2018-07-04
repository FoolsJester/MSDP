import pickle
import csv
import pandas as pd
import numpy as np

def prediction(line, startID, endID, targetTime):
    '''
	- input value:
		line: bus route, such as 39A, 46A, etc.
		startID: start station ID
                endID: end station ID
                targetTime: the o'clock time when taking bus
				from start station, it is seconds
                                to midnight
        - Return Value:
		The seconds taken from start station to end station,
                based on ANN prediction
    '''
    model_file_a = "{}_a_2017_06.clf".format(line)
    model_file_b = "{}_b_2017_06.clf".format(line)

    time_table_file_a = "{}_a_timeTable.csv".format(line) 
    time_table_file_b = "{}_b_timeTable.csv".format(line) 

    df_a = pd.read_csv(time_table_file_a, index_col=0)
    df_b = pd.read_csv(time_table_file_b, index_col=0)


    stops_a = []
    inputFeatures_a = []
    for column in df_a.columns:
        stops_a.append(df_a[column].loc[0])
        inputFeatures_a.append(df_a[column].iloc[1])
    stops_b = []
    inputFeatures_b = []
    for column in df_b.columns:
        stops_b.append(df_b[column].loc[0])
        inputFeatures_b.append(df_b[column].iloc[1])

    sequence_a = 0
    sequence_b = 0
    if startID in stops_a and endID in stops_a:
        stop_location = stops_a.index(endID)
        start_location = stops_a.index(startID)
        sequence_a = stop_location - start_location
    if startID in stops_b and endID in stops_b:
        stop_location = stops_b.index(endID)
        start_location = stops_b.index(startID)
        sequence_b = stop_location - start_location

    def get_mean_timetable(df, start_location, target_time):
        station_column = '{}_P'.format(str(start_location).zfill(3))
        mean_array = df[abs(df[station_column]-target_time) == min(abs(df[station_column]-target_time))].mean()
        return mean_array.values

    if sequence_a > sequence_b:
        pairs = sequence_a
        model_file = model_file_a
        station_number = len(stops_a)
        inputFeatures = inputFeatures_a
        plannedTimeArray = get_mean_timetable(df_a, start_location, targetTime)

        if len(plannedTimeArray) == station_number:
            plannedTime_first = plannedTimeArray[0]
            plannedTime_end = plannedTimeArray[-1]
            plannedTime_start = plannedTimeArray[start_location]
            plannedTime_stop = plannedTimeArray[stop_location]
        else:
            print("Can not get mean planned arrival time from time table!")
            plannedTime_first = df_a[df_a.columns[0]].iloc[1]
            plannedTime_end = df_a[df_a.columns[-1]].iloc[1]
            plannedTime_start = df_a[df_a.columns[start_location]].iloc[1]
            plannedTime_stop = df_a[df_a.columns[stop_location]].iloc[1]
    elif sequence_b > sequence_a:
        pairs = sequence_b
        model_file = model_file_b
        station_number = len(stops_b)
        inputFeatures = inputFeatures_b
        plannedTimeArray = get_mean_timetable(df_b, start_location, targetTime)

        if len(plannedTimeArray) == station_number:
            plannedTime_first = plannedTimeArray[0]
            plannedTime_end = plannedTimeArray[-1]
            plannedTime_start = plannedTimeArray[start_location]
            plannedTime_stop = plannedTimeArray[stop_location]
        else:
            print("Can not get mean planned arrival time from time table!")
            plannedTime_first = df_b[df_b.columns[0]].iloc[1]
            plannedTime_end = df_b[df_b.columns[-1]].iloc[1]
            plannedTime_start = df_b[df_b.columns[start_location]].iloc[1]
            plannedTime_stop = df_b[df_b.columns[stop_location]].iloc[1]
    else:
        return 0

    pkl_file = open(model_file, 'rb')
    new_clf = pickle.load(pkl_file)
    predictions = new_clf.predict([inputFeatures])
    
    pred_full_time = predictions[0][1] - predictions[0][0]
    planned_full_time = plannedTime_end - plannedTime_first
    planned_pairs_time = plannedTime_stop - plannedTime_start
    #pair_time = (predictions[0][1]-predictions[0][0])/(station_number-1)
    #print("end/first: {}/{}".format(predictions[0][1],predictions[0][0]))
    #print("stop/start: {}/{}".format(plannedTime_stop, plannedTime_start))
    #print(pair_time, pairs)
    #return pair_time * pairs
    # planned_full_time/planned_pairs_time = pred_full_time/pred_pairs_time
    pred_pairs_time = pred_full_time * planned_pairs_time / planned_full_time
    return pred_pairs_time

def main():
    print(prediction('39A', 1913, 1660, 34200))
    print(prediction('39A', 1864, 335, 34200))
    print(prediction('39A', 6112, 1867, 24200))

if __name__ == '__main__':
    main()

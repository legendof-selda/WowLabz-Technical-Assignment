import numpy as np
import pickle
from sklearn import svm
from sklearn.preprocessing import StandardScaler

def predict_sleep(app, sleep_hrs):
    filename = 'sleep_model'
    model = pickle.load(app.open_resource('static\\models\\'+filename+'.pkl'))
    scalerX = pickle.load(app.open_resource('static\\models\\'+filename+'_scalerX'+'.pkl'))
    scalerY = pickle.load(app.open_resource('static\\models\\'+filename+'_scalerY'+'.pkl'))
    predict = model.predict(scalerX.transform([[sleep_hrs]]))
    return scalerY.inverse_transform(predict)[0]
import keras
import pandas as pd
import numpy as np
from numpy.random import randint
from keras.models import Sequential
from keras.layers import *

import pdb


def evaluate_metrics(Yt, Yp):
    tp = Yt.sum()
    tn = Yt.size - tp
    fp = Yp[Yt == 0].sum()
    fn = (1 - Yp[Yt == 1]).sum()
    prec = tp / (tp + fp)
    recall = tp / (fn + tp)
    return {'precision': prec, 'recall': recall, 'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn}


dataset = pd.read_pickle('data/processed/training_v3.pkl')
dataset = dataset[
    ['DayOfWeek',
     'UniqueCarrier',
     'Origin',
     'Dest',
     'CRSDepTime',
     'DepDel15',
     'Distance',
     'lon',
     'lat',
     'tmpf',
     'drct',
     'sknt',
     'vsby',
     'skyc1',
     'skyl1']
]
dataset.dropna(axis=0, inplace=True)
interesting = dataset[
    ['DepDel15',
     'DayOfWeek',
     # 'UniqueCarrier',
     # 'Origin',
     # 'Dest',
     # 'CRSDepTime',
     'Distance',
     'lon',
     'lat',
     'tmpf',
     'drct',
     'sknt',
     'vsby',
     # 'skyc1',
     'skyl1']
].astype(np.float32)


# interesting = interesting.dropna(axis = 0)

def make_onehot(col):
    global interesting
    global dataset
    dataset[col] = dataset[col].astype('category')
    unique = dataset[col].unique()
    df = pd.DataFrame({col + str(u): (dataset[col] == u).astype(np.int8) for u in unique})
    interesting = pd.concat([interesting, df], axis=1, ignore_index=True)
    print('appended', col)


def make_onehot_multiple(l):
    for v in l:
        make_onehot(v)


make_onehot_multiple(['UniqueCarrier', 'Origin', 'Dest', 'skyc1'])

interesting = interesting.sample(frac=1).reset_index(drop=True)
n = interesting.shape[0]
m = interesting.shape[1] - 1

interesting[0] = interesting[0].astype(np.int8)

train_percent = 0.7


def batch_generator(X, Y, batch_size):
    positive = X[Y == 1]
    negative = X[Y == 0]
    n_pos = positive.shape[0]
    n_neg = negative.shape[0]
    batch_n_pos = batch_size // 8
    batch_n_neg = batch_size - batch_n_pos
    while True:
        batch_positive = positive[randint(n_pos, size=batch_n_pos), :]
        batch_negative = negative[randint(n_neg, size=batch_n_neg), :]
        yield (np.vstack((batch_positive, batch_negative)), np.hstack((np.zeros(batch_n_pos), np.ones(batch_n_neg))))


train, test = interesting.iloc[:int(n * train_percent)], interesting.iloc[int(n * train_percent):]
X_train, X_test = train.drop(0, axis=1).values, test.drop(0, axis=1).values
Y_train, Y_test = train[0].values.astype(np.int8), test[0].values.astype(np.int8)

model = Sequential()
model.add(Dense(100, input_dim=m, init='uniform', activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(100, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(1, activation='sigmoid'))

model.compile(loss='binary_crossentropy',
              optimizer='sgd',
              metrics=['accuracy'])

checkpointer = keras.callbacks.ModelCheckpoint(filepath="weights.hdf5", monitor='val_loss', verbose=1,
                                               save_best_only=True)


class LossHistory(keras.callbacks.Callback):
    def on_train_begin(self, logs={}):
        self.losses = []

    def on_batch_end(self, batch, logs={}):
        Y_pred = model.predict_classes(X_test, batch_size=64, verbose=1)
        print(evaluate_metrics(Y_test, Y_pred))
        self.losses.append(logs.get('loss'))


# history = LossHistory()
# model.fit(X_train, Y_train, nb_epoch=20, batch_size=32, callbacks=[checkpointer], validation_data=(X_test, Y_test))
model.fit_generator(
    batch_generator(X_train, Y_train, 64),
    samples_per_epoch=2 ** 17,
    nb_epoch=100,
    callbacks=[checkpointer],
    validation_data=batch_generator(X_test, Y_test, 64),
    nb_val_samples=2 ** 15
)

Y_pred = model.predict_classes(X_test, batch_size=32)
print(evaluate_metrics(Y_test, Y_pred))

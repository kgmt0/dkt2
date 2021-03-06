#!/usr/bin/env python3
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import csv
import numpy as np
from os.path import isfile
from keras.models import Model, load_model
from keras.layers import Input, GRU, LSTM, SimpleRNN, Dense
from functools import reduce

def read_data_from_csv_file(fileName, n_params=8):

    rows = []

    with open(fileName, "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            rows.append(row)

    row_skip = 1
    col_skip = 2
    index = row_skip

    print("the number of rows is " + str(len(rows)))
    n_students = int((len(rows)-row_skip)/(n_params+1))
    print("the number of students is " + str(n_students))
    n_items = int(rows[row_skip][col_skip])
    for n in range(n_students): 
        if (int(rows[row_skip + n*(n_params + 1)][col_skip]) > n_items): 
            n_items = int(rows[row_skip + n*(n_params + 1)][col_skip])
    print("the number of items is " + str(n_items))

    inputs = np.zeros((n_students, n_items, n_params - 1))
    target = np.zeros((n_students, n_items, 1))

    for i in range(n_students):
        index = (n_params + 1)*i + row_skip
        num_items = int(rows[index][col_skip])
        for j in range(num_items):
            target[i][j][0] = int(rows[index + 1][j + col_skip])
        for k in range(n_params-1):
            for j in range(num_items):
                inputs[i][j][k] = float(rows[index + 2 + k][j + col_skip])

    print("finished reading data")
    return inputs, target

def compose2(f, g):
    return lambda x: f(g(x))

def compose(*args):
    return reduce(compose2, args)

def make_model(input_shape, rnn_layer=GRU, units=64):
    inputs = Input(input_shape)
    x = rnn_layer(units, return_sequences=True)(inputs)
    x = Dense(1)(x)
    return Model(inputs=inputs, outputs=x)

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("data")
    argparser.add_argument(     "-n",
                                "--epochs",
                                type=int,
                                default=150,
                                help="number of epochs to train" )
    argparser.add_argument(     "-s",
                                "--split",
                                type=float,
                                default=0.2,
                                help="fraction of data to use for training" )
    argparser.add_argument(     "-t",
                                "--type",
                                type=str.lower,
                                default="gru",
                                choices=["gru", "lstm", "simplernn"],
                                help="type of RNN layer to use" )
    argparser.add_argument(     "-u",
                                "--units",
                                type=int,
                                default=64,
                                help="number of units per RNN cell" )
    argparser.add_argument(     "-m",
                                "--model-file",
                                type=str,
                                default="dkt2.h5",
                                help="model file to use" )
    args = argparser.parse_args()

    rnn_layer = {"gru": GRU, "lstm": LSTM, "simplernn": SimpleRNN}[args.type];
    x, y = read_data_from_csv_file(args.data)

    if isfile(args.model_file):
        model = load_model(args.model_file)
    else:
        model = make_model( x.shape[1:], rnn_layer=rnn_layer, units=args.units)
        model.compile("Adam", "binary_crossentropy", metrics=["accuracy"]);

    model.summary()

    model.fit(x=x, y=y, epochs=args.epochs, validation_split=args.split)
    model.save(args.model_file)

if __name__ == "__main__":
    main()

#!/bin/sh
# Copyright (c) lingff(ling@stu.pku.edu.cn),
# School of Software & Microelectronics, Peking University.
# A-Tune is licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# Create: 2021-04-22

"""
This program is used as tensorflow train benchmark.
This program builds a Fully Connected Neural Network to train MNIST dataset using tensorflow 2.1.

We get 3 parameters to optimize:
    batch size, optimizer(Adam, SGD, Adagrad, Adadelta) and its learning rate,
according to categorical accuracy(90%) and time consuming(10%) after one epoch training.

For details, please refer to tensorflow_train_client.yaml and tensorflow_train_server.yaml.
"""

import tensorflow as tf
import time

BATCH_SIZE = 32
OPTIMIZER = "adam"
LEARNING_RATE = 1e-3

mnist = tf.keras.datasets.mnist
(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train, x_test = x_train / 255.0, x_test / 255.0

model = tf.keras.models.Sequential([
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(10, activation='softmax')
])

if OPTIMIZER == "adam":
    model.compile(optimizer= tf.keras.optimizers.Adam(lr = LEARNING_RATE),
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
                  metrics=['sparse_categorical_accuracy'])
elif OPTIMIZER == "sgd":
    model.compile(optimizer= tf.keras.optimizers.SGD(lr = LEARNING_RATE),
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
                  metrics=['sparse_categorical_accuracy'])
elif OPTIMIZER == "adagrad":
    model.compile(optimizer= tf.keras.optimizers.Adagrad(lr = LEARNING_RATE),
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
                  metrics=['sparse_categorical_accuracy'])
elif OPTIMIZER == "adadelta":
    model.compile(optimizer= tf.keras.optimizers.Adadelta(lr = LEARNING_RATE),
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
                  metrics=['sparse_categorical_accuracy'])

start = time.time()
history = model.fit(x_train, y_train, batch_size=BATCH_SIZE, epochs=1,
                    validation_data=(x_test, y_test), verbose=0)
end = time.time()

print("accuracy = %f" % history.history['sparse_categorical_accuracy'][0])
print("time = %f" % (end - start))

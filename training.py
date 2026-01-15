import os
import json
import pickle
import random
import nltk
import numpy as np
from nltk.stem import WordNetLemmatizer
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import SGD

lemmatizer = WordNetLemmatizer()

words = []
classes = []
documents = []
ignore_words = ['?', '!', '.', ',']

base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "data.json")

with open(data_path, encoding="utf-8") as file:
    intents = json.load(file)

for intent in intents['intents']:
    for pattern in intent['patterns']:
        w = nltk.word_tokenize(pattern)
        words.extend(w)
        documents.append((w, intent['tag']))
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]
words = sorted(list(set(words)))
classes = sorted(list(set(classes)))

pickle.dump(words, open(os.path.join(base_dir, "texts.pkl"), 'wb'))
pickle.dump(classes, open(os.path.join(base_dir, "labels.pkl"), 'wb'))

training = []
output_empty = [0] * len(classes)

for doc in documents:
    bag = []
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in doc[0]]
    for w in words:
        bag.append(1 if w in pattern_words else 0)

    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1
    training.append([bag, output_row])

random.shuffle(training)
training = np.array(training, dtype=object)

train_x = np.array(list(training[:, 0]))
train_y = np.array(list(training[:, 1]))

model = Sequential()
model.add(Dense(128, activation='relu', input_shape=(train_x.shape[1],)))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(train_y.shape[1], activation='softmax'))

sgd = SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

model.fit(train_x, train_y, epochs=200, batch_size=5, verbose=1)

model.save(os.path.join(base_dir, "model.h5"))
print("Model created and saved")

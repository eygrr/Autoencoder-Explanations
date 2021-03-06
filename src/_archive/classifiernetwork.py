# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import numpy as np
import data as dt
from keras.regularizers import l2
from keras.optimizers import SGD, Adagrad, Adam, RMSprop, Adadelta, Adamax, Nadam
from sklearn.metrics import f1_score, accuracy_score
from keras.models import Sequential
from keras.layers.core import Dense, Dropout
import cluster
import rank
import finetune_outputs as fto
import svm
import tree
import hierarchy
import ndcg
from sklearn.model_selection import KFold
from sklearn.preprocessing import MultiLabelBinarizer

class NeuralNetwork:

    # Shared variables
    training_data = None
    class_path = None
    learn_rate = None
    epochs = None
    loss = None
    batch_size = None
    hidden_activation = None
    layer_init = None
    output_activation = None
    hidden_layer_size = None
    file_name = None
    vector_path = None
    optimizer = None
    dropout_noise = None
    reg = 0.0
    activity_reg = 0.0
    finetune_size = 0
    save_outputs = False
    amount_of_hidden = 0
    identity_swap = None
    deep_size = None
    from_ae = None
    is_identity = None
    randomize_finetune_weights = None
    corrupt_finetune_weights = None
    deep_size = None
    fine_tune_weights_fn = None
    finetune_weights = None
    past_weights = None

    def __init__(self,  class_path=None, get_scores=False,  randomize_finetune_weights=False, dropout_noise = None,
                 amount_of_hidden=0,
                 epochs=1,  learn_rate=0.01, loss="mse", batch_size=1, past_model_bias_fn=None, identity_swap=False,
                 reg=0.0, amount_of_finetune=1, output_size=25,
                 hidden_activation="tanh", layer_init="glorot_uniform", output_activation="tanh", deep_size = None,
                 corrupt_finetune_weights = False, split_to_use=-1,
                   hidden_layer_size=100, file_name="unspecified_filename", vector_path=None, is_identity=False,
                  finetune_size=0, data_type="movies",
                 optimizer_name="rmsprop", noise=0.0, fine_tune_weights_fn=None, past_model_weights_fn=None,
                 from_ae=True, save_outputs=False, label_names_fn="",
                 rewrite_files=False, cv_splits=1,cutoff_start=0.2, development=False,
                 class_weight=None, csv_fn=None):

        total_file_name = "../data/" + data_type + "/nnet/spaces/" + file_name
        space_fn = total_file_name + "L0.txt"
        weights_fn = "../data/" + data_type + "/nnet/weights/" + file_name + "L0.txt"
        bias_fn = "../data/" + data_type + "/nnet/bias/" + file_name +"L0.txt"
        rank_fn = "../data/" + data_type + "/nnet/clusters/" + file_name + ".txt"

        all_fns = [space_fn, weights_fn, bias_fn, rank_fn]
        if dt.allFnsAlreadyExist(all_fns) and not rewrite_files:
            print("Skipping task", "nnet")
            return
        else:
            print("Running task", "nnet")

        self.class_path = class_path
        self.learn_rate = learn_rate
        self.epochs = epochs
        self.loss = loss
        self.batch_size = batch_size
        self.hidden_activation = hidden_activation
        self.layer_init = layer_init
        self.output_activation = output_activation
        self.hidden_layer_size = hidden_layer_size
        self.file_name = file_name
        self.vector_path = vector_path
        self.dropout_noise = dropout_noise
        self.finetune_size = finetune_size
        self.get_scores = get_scores
        self.reg = reg
        self.amount_of_finetune = amount_of_finetune
        self.amount_of_hidden = amount_of_hidden
        self.output_size = output_size
        self.identity_swap = identity_swap
        self.deep_size = deep_size
        self.from_ae = from_ae
        self.is_identity = is_identity
        self.randomize_finetune_weights = randomize_finetune_weights
        self.corrupt_finetune_weights = corrupt_finetune_weights
        self.deep_size = deep_size
        self.fine_tune_weights_fn = fine_tune_weights_fn

        print(data_type)

        if optimizer_name == "adagrad":
            self.optimizer = RMSprop()
        else:
            self.optimizer = SGD(lr=learn_rate, momentum=0.0, decay=0.0, nesterov=False)

        entity_vectors = np.asarray(dt.import2dArray(self.vector_path))
        print("Imported vectors", len(entity_vectors), len(entity_vectors[0]))
        entity_classes = np.asarray(dt.import2dArray(self.class_path))
        print("Imported classes", len(entity_classes), len(entity_classes[0]))


        if len(entity_vectors) != len(entity_classes):
            entity_vectors = entity_vectors.transpose()
            print("Transposed vectors, now in form", len(entity_vectors), len(entity_vectors[0]))

        self.input_size = len(entity_vectors[0])
        self.output_size = len(entity_classes[0])


        model_builder = self.classifierNetwork

        models = []
        x_train = []
        y_train = []
        x_test = []
        y_test = []
        x_dev = []
        y_dev = []


        c = 0
        for i in range(cv_splits):
            if split_to_use > -1:
                if c != split_to_use:
                    c += 1
                    continue

            models.append(model_builder())
            c+=1

        # Converting labels to categorical


        f1_scores = []
        accuracy_scores = []
        f1_averages = []
        accuracy_averages = []
        if cv_splits == 1:
            k_fold = KFold(n_splits=3, shuffle=False, random_state=None)
        else:
            k_fold = KFold(n_splits=cv_splits, shuffle=False, random_state=None)
        c = 0
        for train, test in k_fold.split(entity_vectors):
            if split_to_use > -1:
                if c != split_to_use:
                    c += 1
                    continue
            x_train.append(entity_vectors[train[int(len(train) * 0.2):]])
            y_train.append(entity_classes[train[int(len(train) * 0.2):]])
            x_test.append(entity_vectors[test])
            y_test.append(entity_classes[test])
            x_dev.append(entity_vectors[train[:int(len(train) * 0.2)]])
            y_dev.append(entity_classes[train[:int(len(train) * 0.2)]])

            hist = models[0].fit(entity_vectors[train[int(len(train) * 0.2):]], entity_classes[train[int(len(train) * 0.2):]], nb_epoch=self.epochs,
                          batch_size=self.batch_size, verbose=1, class_weight=class_weight)
            print(hist.history)
            if cv_splits == 1 or split_to_use == c:
                break

        original_fn = file_name
        for m in range(len(models)):
            if development:
                x_test[m] = x_dev[m]
                y_test[m] = y_dev[m]

            if get_scores:

                vals_to_try = np.arange(start=cutoff_start, stop=1, step=0.01)
                test_pred = models[m].predict(x_train[m]).transpose()
                y_train_m = np.asarray(y_train[m]).transpose()
                highest_f1 = [0]*len(test_pred)
                highest_vals = [0.5]*len(test_pred)


                for c in range(len(test_pred)):
                    for val in vals_to_try:
                        test_pred_c = np.copy(test_pred[c])
                        test_pred_c[test_pred_c >= val] = 1
                        test_pred_c[test_pred_c< val] = 0
                        acc = accuracy_score(y_train_m[c], test_pred_c)
                        f1 = f1_score(y_train_m[c], test_pred_c, average="binary")
                        f1 = (f1 + acc) / 2
                        if f1 > highest_f1[c]:
                            highest_f1[c] = f1
                            highest_vals[c] = val
                print("optimal f1s", highest_f1 )
                print("optimal vals", highest_vals )
                y_pred = models[m].predict(x_test[m]).transpose()
                y_test[m] = np.asarray(y_test[m]).transpose()
                for y in range(len(y_pred)):
                    y_pred[y][y_pred[y] >= highest_vals[y]] = 1
                    y_pred[y][y_pred[y] < highest_vals[y]] = 0
                f1_array = []
                accuracy_array = []
                for y in range(len(y_pred)):
                    accuracy_array.append(accuracy_score(y_test[m][y], y_pred[y]))
                    f1_array.append(f1_score(y_test[m][y], y_pred[y], average="binary"))
                    print(f1_array[y])
                y_pred = y_pred.transpose()
                y_test[m] = np.asarray(y_test[m]).transpose()
                micro_average = f1_score(y_test[m], y_pred, average="macro")
                cv_f1_fn = "../data/" + data_type + "/nnet/scores/F1 " + file_name + ".txt"
                cv_acc_fn = "../data/" + data_type + "/nnet/scores/ACC " + file_name + ".txt"
                dt.write1dArray(f1_array, cv_f1_fn)
                dt.write1dArray(accuracy_array, cv_acc_fn)
                f1_scores.append(f1_array)
                accuracy_scores.append(accuracy_array)
                f1_average = np.average(f1_array)
                accuracy_average = np.average(accuracy_array)
                f1_averages.append(f1_average)
                accuracy_averages.append(accuracy_average)
                print("Average F1 Binary", f1_average, "Acc", accuracy_average)
                print("Micro Average F1", micro_average)

                f1_array.append(f1_average)
                f1_array.append(micro_average)
                accuracy_array.append(accuracy_average)
                accuracy_array.append(0.0)

                scores = [accuracy_array, f1_array]

                csv_fn = "../data/"+data_type+"/nnet/csv/"+csv_fn+".csv"

                file_names = [file_name + "ACC", file_name + "F1"]
                label_names = dt.import1dArray(label_names_fn)
                if dt.fileExists(csv_fn):
                    print("File exists, writing to csv")
                    try:
                        dt.write_to_csv(csv_fn, file_names, scores)
                    except PermissionError:
                        print("CSV FILE WAS OPEN, WRITING TO ANOTHER FILE")
                        dt.write_to_csv(csv_fn[:len(csv_fn) - 4] + str(random.random()) + "FAIL.csv", [file_name],
                                        scores)
                else:
                    print("File does not exist, recreating csv")
                    key = []
                    for l in label_names:
                        key.append(l)
                    key.append("AVERAGE")
                    key.append("MICRO AVERAGE")
                    dt.write_csv(csv_fn, file_names, scores, key)

            if save_outputs:
                self.output_clusters = models[m].predict(entity_vectors)
                dt.write2dArray(self.output_clusters.transpose(), rank_fn)


            for l in range(0, len(models[m].layers) - 1):
                if dropout_noise is not None and dropout_noise > 0.0:
                    if l % 2 == 1:
                        continue
                print("Writing", l, "layer")
                truncated_model = Sequential()
                for a in range(l+1):
                    truncated_model.add(models[m].layers[a])
                truncated_model.compile(loss=self.loss, optimizer="sgd")
                self.end_space = truncated_model.predict(entity_vectors)
                total_file_name = "../data/" + data_type + "/nnet/spaces/" + file_name
                dt.write2dArray(self.end_space, total_file_name + "L" + str(l) + ".txt")

            for l in range(len(models[m].layers)):
                try:
                    dt.write2dArray(models[m].layers[l].get_weights()[0],
                                    "../data/" + data_type + "/nnet/weights/" + file_name + "L" + str(l) + ".txt")
                    dt.write1dArray(models[m].layers[l].get_weights()[1],
                                    "../data/" + data_type + "/nnet/bias/" + file_name + "L" +  str(l) + ".txt")
                except IndexError:
                    print("Layer ", str(l), "Failed")

        if cv_splits > 1:
            class_f1_averages = []
            class_accuracy_averages = []
            f1_scores = np.asarray(f1_scores).transpose()
            accuracy_scores = np.asarray(accuracy_scores).transpose()

            for c in range(len(f1_scores)):
                class_f1_averages.append(np.average(f1_scores[c]))
                class_accuracy_averages.append(np.average(accuracy_scores[c]))

            f1_fn = "../data/" + data_type + "/nnet/scores/F1 " + file_name + ".txt"
            acc_fn = "../data/" + data_type + "/nnet/scores/ACC " + file_name + ".txt"
            dt.write1dArray(class_f1_averages, f1_fn)
            dt.write1dArray(class_accuracy_averages, acc_fn)
            overall_f1_average = np.average(f1_averages)
            overall_accuracy_average = np.average(accuracy_averages)

    def classifierNetwork(self):
        print("CLASSIFIER")
        model = Sequential()
        print(self.input_size, self.hidden_layer_size, self.finetune_size, self.output_size)

        print(0, "Deep layer", self.input_size, self.deep_size[0], self.hidden_activation)
        model.add(Dense(output_dim=self.deep_size[0], input_dim=self.input_size, init=self.layer_init,
                        activation=self.hidden_activation, W_regularizer=l2(self.reg)))

        if self.dropout_noise is not None and self.dropout_noise != 0.0:
            print("Dropout layer")
            model.add(Dropout(self.dropout_noise))

        for a in range(1, len(self.deep_size)):
            print(a, "Deep layer", self.deep_size[a - 1], self.deep_size[a], self.hidden_activation)
            model.add(Dense(output_dim=self.deep_size[a], input_dim=self.deep_size[a - 1], init=self.layer_init,
                            activation=self.hidden_activation, W_regularizer=l2(self.reg)))
            if self.dropout_noise is not None and self.dropout_noise != 0.0:
                print("Dropout layer")
                model.add(Dropout(self.dropout_noise))

        print("Class outputs", self.deep_size[len(self.deep_size) - 1], self.output_size,
              self.output_activation)
        model.add(
            Dense(output_dim=self.output_size, input_dim=self.deep_size[len(self.deep_size) - 1],
                  activation=self.output_activation,
                  init=self.layer_init))

        print("Compiling")
        model.compile(loss=self.loss, optimizer=self.optimizer)

        return model

    def fineTuneNetwork(self):
        print("FINETUNER")
        model = Sequential()
        print(self.input_size, self.hidden_layer_size, self.finetune_size, self.output_size)

        #self.model.add(GaussianNoise(0.0, input_shape=(input_size,)))

        # If we want to swap the identity layer to before the hidden layer
        if self.identity_swap:
            print("Identity swapped layer", self.input_size, self.hidden_layer_size, self.hidden_activation)
            for a in range(self.amount_of_finetune):
                model.add(Dense(output_dim=self.hidden_layer_size, input_dim=self.input_size,
                                     activation=self.hidden_activation,
                                     init="identity"))


        if self.from_ae:
            for p in range(len(self.past_weights)):
                print(p, "Past AE layer", self.input_size, self.hidden_layer_size, self.hidden_activation)
                model.add(Dense(output_dim=self.hidden_layer_size, input_dim=self.input_size, activation=self.hidden_activation,
                                     weights=self.past_weights[p], W_regularizer=l2(self.reg)))
            if self.dropout_noise is not None:
                print("Dropout layer")
                model.add(Dropout(self.dropout_noise))

        # Add an identity layer that has equal values to the input space to find some more nonlinear relationships
        if self.is_identity:
            print("Identity layer", self.hidden_layer_size, self.hidden_layer_size, self.hidden_activation)
            for a in range(self.amount_of_finetune):
                model.add(Dense(output_dim=self.hidden_layer_size, input_dim=self.hidden_layer_size, activation=self.hidden_activation,
                          init="identity"))

        if self.randomize_finetune_weights:
            print("Randomize finetune weights", self.hidden_layer_size, self.finetune_size, "linear")
            model.add(Dense(output_dim=self.finetune_size, input_dim=self.hidden_layer_size, activation="linear",
                                 init=self.layer_init))
        elif self.corrupt_finetune_weights:
            print("Corrupt finetune weights", self.hidden_layer_size, self.finetune_size, "linear")
            model.add(Dense(output_dim=self.finetune_size, input_dim=self.hidden_layer_size, activation="linear",
                                 weights=self.fine_tune_weights))
        else:
            print("Fine tune weights", self.hidden_layer_size, len(self.fine_tune_weights[0][0]), "linear")
            model.add(Dense(output_dim=len(self.fine_tune_weights[0][0]), input_dim=self.hidden_layer_size, activation="linear",
                                 weights=self.fine_tune_weights))
        if self.get_scores:
            if self.randomize_finetune_weights or self.corrupt_finetune_weights or len(self.fine_tune_weights_fn) > 0:
                print("Class outputs", self.finetune_size, self.output_size, self.output_activation)
                model.add(
                    Dense(output_dim=self.output_size, input_dim=self.finetune_size, activation=self.output_activation,
                          init=self.layer_init))

        print("Compiling")
        model.compile(loss=self.loss, optimizer=self.optimizer)

        return model

import random
import sys
def main(loss, output_activation, optimizer_name, hidden_activation, ep, dropout_noise, cs, splits, cv_splits):
    for splits in range(cv_splits):
        print(deep_size, init_vector_path)
        loss = loss
        output_activation = output_activation
        optimizer_name = optimizer_name
        hidden_activation = hidden_activation
        classification_path = "../data/" + data_type + "/classify/" + classification_task + "/class-all"
        label_names_fn = "../data/" + data_type + "/classify/" + classification_task + "/names.txt"
        lr = 0.01
        fine_tune_weights_fn = None
        ep = ep
        amount_of_finetune = 0
        batch_size = 200
        save_outputs = True
        dropout_noise = dropout_noise
        is_identity = False
        identity_swap = False
        from_ae = False
        past_model_weights_fn = None
        past_model_bias_fn = None
        randomize_finetune_weights = False
        hidden_layer_size = 100
        output_size = 10
        randomize_finetune_weights = False
        corrupt_finetune_weights = False
        get_scores = True

        SDA = NeuralNetwork(noise=0, fine_tune_weights_fn=fine_tune_weights_fn, optimizer_name=optimizer_name,
            get_scores=get_scores, past_model_bias_fn=past_model_bias_fn, deep_size=deep_size,  cutoff_start=cs,
            randomize_finetune_weights=randomize_finetune_weights, amount_of_finetune=amount_of_finetune,
            vector_path=init_vector_path, hidden_layer_size=hidden_layer_size, class_path=classification_path,
            identity_swap=identity_swap, dropout_noise=dropout_noise, save_outputs=save_outputs,
            hidden_activation=hidden_activation, output_activation=output_activation, epochs=ep,
            learn_rate=lr, is_identity=is_identity, output_size=output_size, split_to_use=splits, label_names_fn=label_names_fn,
            batch_size=batch_size, past_model_weights_fn=past_model_weights_fn, loss=loss, cv_splits=cv_splits, csv_fn = file_name,
            file_name=file_name, from_ae=from_ae, data_type=data_type, rewrite_files=rewrite_files, development=development, class_weight=class_weight)

        new_file_names = []


    """
data_type = "wines"
classification_task = "types"
file_name = "wines ppmi"
lowest_amt = 50
highest_amt = 10
init_vector_path = "../data/"+data_type+"/nnet/spaces/wines100trimmed.txt"
deep_size = [100,100,100]
"""
data_type = "movies"
classification_task = "genres"
file_name = "movies ppmi"
lowest_amt = 100
highest_amt = 10
init_vector_path = "../data/"+data_type+"/nnet/spaces/films200-genres.txt"
deep_size = [200,200,200]

"""
data_type = "placetypes"
classification_task = "foursquare"
file_name = "placetypes ppmi"
lowest_amt = 50
highest_amt = 10
init_vector_path = "../data/"+data_type+"/nnet/spaces/places100-"+classification_task+".txt"
deep_size = [100]
"""
hidden_activation = "relu"
dropout_noise = 0.5
output_activation = "sigmoid"
cutoff_start = 0.2
size = 200
ep=200
"""
hidden_activation = "tanh"
dropout_noise = 0.5
output_activation = "sigmoid"
cutoff_start = 0.2
deep_size = [500,400,300,200]
init_vector_path = "../data/"+data_type+"/bow/ppmi/class-all-"+str(lowest_amt)+"-"+str(highest_amt)+"-"+classification_task
ep =300
"""
class_weight = None
trainer = "adagrad"
loss="binary_crossentropy"


is_identity = True
amount_of_finetune = 1

breakoff = True
score_limit = 0.9
cluster_multiplier = 1
epochs=3000
learn_rate=0.001
kappa = True
development = False
add_all_terms = True
average_ppmi = True
amount_to_start = 1000

cross_val = 5

rewrite_files = False

threads=3




variables = [data_type, classification_task, file_name, init_vector_path, hidden_activation,
                               is_identity, amount_of_finetune, breakoff, kappa, score_limit, rewrite_files,
                               cluster_multiplier, threads, dropout_noise, learn_rate, epochs, cross_val, ep,
                               output_activation, cutoff_start, deep_size, classification_task, highest_amt,
                               lowest_amt, loss, development, add_all_terms, average_ppmi, trainer, class_weight,
                               amount_to_start]
for v in variables:
    if isinstance(v, str):
        v = '"' + v + '"'
    sys.stdout.write(str(v) + " ")


args = sys.argv[1:]
if len(args) > 0:
    data_type = args[0]
    classification_task = args[1]
    file_name = args[2]
    init_vector_path = args[3]
    hidden_activation = args[4]
    is_identity = args[5]
    amount_of_finetune = args[6]
    breakoff = args[7]
    kappa = args[8]
    score_limit = args[9]
    rewrite_files = args[10]
    cluster_multiplier = args[11]
    threads = args[12]
    dropout_noise = args[13]
    learn_rate = args[14]
    epochs = args[15]
    cross_val = args[16]
    ep = args[17]
    output_activation = args[18]
    cutoff_start = args[19]
    deep_size = args[20]
    classification_task = args[21]
    highest_amt = args[22]
    lowest_amt = args[23]
    loss = args[24]
    development = args[25]
    add_all_terms = args[26]
    average_ppmi = args[27]
    trainer = args[28]
    class_weight = args[29]
    amount_to_start = args[30]


if  __name__ =='__main__':main(data_type, classification_task, file_name, init_vector_path, hidden_activation,
                               is_identity, amount_of_finetune, breakoff, kappa, score_limit, rewrite_files,
                               cluster_multiplier, threads, dropout_noise, learn_rate, epochs, cross_val, ep,
                               output_activation, cutoff_start, deep_size, classification_task, highest_amt,
                               lowest_amt, loss, development, add_all_terms, average_ppmi, trainer, class_weight,
                               amount_to_start)

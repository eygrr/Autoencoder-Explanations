
from sklearn import svm
import numpy as np
from sklearn.metrics import cohen_kappa_score, f1_score, accuracy_score
import data as dt
from keras.metrics import categorical_accuracy
from sklearn.cross_validation import train_test_split

from sklearn.model_selection import cross_val_score
import multiprocessing
import math
from functools import partial
from multiprocessing.dummy import Pool as ThreadPool
from sys import exit
import scipy.sparse as sp
from sklearn.multiclass import OneVsRestClassifier


from sklearn import linear_model
from sklearn.metrics import cohen_kappa_score, f1_score, accuracy_score

def perf_measure(self, y_actual, y_hat): # Get the true positives etc
    TP = 0
    FP = 0
    TN = 0
    FN = 0

    for i in range(len(y_hat)):
        if y_actual[i] == 1 and y_hat[i] == 1:
            TP += 1
        if y_hat[i] == 1 and y_actual[i] == 0:
            FP += 1
        if y_actual[i] == 0 and y_hat[i] == 0:
            TN += 1
        if y_hat[i] == 0 and y_actual[i] == 1:
            FN += 1

    return TP, FP, TN, FN



import tensorflow as tf
def multiClassLinearSVM(x_train, y_train, x_test, y_test):
    clf = OneVsRestClassifier(svm.LinearSVC(class_weight="balanced", dual=False))
    clf.fit(x_train, y_train)
    y_pred = clf.predict(x_test)
    f1 = f1_score(y_test, y_pred, average="micro")
    f12 = f1_score(y_test, y_pred, average="macro")
    acc = accuracy_score(y_test, y_pred)
    return (f1, acc, f12, 0, 0, 0)

def multiClassGaussianSVM(x_train, y_train, x_test, y_test):
    clf = OneVsRestClassifier(svm.LinearSVC(class_weight="balanced", dual=False))
    clf.fit(x_train, y_train)
    y_pred = clf.predict(x_test)
    f1 = f1_score(y_test, y_pred, average="micro")
    f12 = f1_score(y_test, y_pred, average="macro")
    acc = accuracy_score(y_test, y_pred)
    return (f1, acc, f12, 0, 0, 0)

def linearSVMScore(x_train, y_train, x_test, y_test):
    clf = svm.LinearSVC(class_weight="balanced", dual=False)
    clf.fit(x_train, y_train)
    y_pred = clf.predict(x_test)
    f1 = f1_score(y_test, y_pred)
    acc = accuracy_score(y_test, y_pred)
    TP, FP, TN, FN = perf_measure(y_test, y_pred)
    return (f1, acc, TP, FP, TN, FN)


class SVM:

    def runGaussianSVM(self, y_test, y_train, x_train, x_test, get_kappa, get_f1):
        clf = svm.SVC(kernel='rbf', class_weight='balanced')
        if get_f1:
            cross_val = cross_val_score(clf, x_train, y_train, scoring="f1", cv=5)
            f1 = np.average(cross_val)
        else:
            f1 = 0
        clf.fit(x_train, y_train)
        direction = clf.dual_coef_.tolist()[0]
        y_pred = clf.predict(x_test)
        y_pred = y_pred.tolist()
        if get_kappa:
            kappa_score = cohen_kappa_score(y_test, y_pred)
        else:
            kappa_score = 0

        ktau = 0
        #ppmi_score, ppmi_ratio = get_ppmi_score(y_pred, property_name)
        return kappa_score, direction, f1, 0, 0

    def perf_measure(self, y_actual, y_hat):
        TP = 0
        FP = 0
        TN = 0
        FN = 0

        for i in range(len(y_hat)):
            if y_actual[i] == 1 and y_hat[i] == 1:
                TP += 1
            if y_hat[i] == 1 and y_actual[i] == 0:
                FP += 1
            if y_actual[i] == 0 and y_hat[i] == 0:
                TN += 1
            if y_hat[i] == 0 and y_actual[i] == 1:
                FN += 1

        return TP, FP, TN, FN

    x_train, x_test, get_kappa, get_f1, data_type, classification, lowest_amt, higher_amt, y_train, y_test = None, None, False, False, "", "", 0, 0, None, None
    def runSVM(self, property_name, y=None):
        if y is None:
            y = dt.import1dArray("../data/" + self.data_type + "/bow/binary/phrases/class-" + property_name + "-" + str(
            self.lowest_amt) + "-" + str(self.higher_amt) + "-" + self.classification, file_type="i")
        else:
            y = y[0]
        for i in range(len(y)):
            if y[i] >= 1:
                y[i] = 1
        #x_train, y_train = dt.balanceClasses(x_train, y_train)
        clf = svm.LinearSVC(class_weight="balanced", dual=False)
        #if len(self.x_train) !=
        clf.fit(self.x_train, y)
        direction = clf.coef_.tolist()[0]
        y_pred = clf.predict(self.x_test)
        y_pred = y_pred.tolist()
        f1 = f1_score(y[:len(y_pred)], y_pred)
        kappa_score = cohen_kappa_score(y[:len(y_pred)], y_pred)
        acc = accuracy_score(y[:len(y_pred)], y_pred)

        TP, FP, TN, FN = self.perf_measure(y, y_pred)
        print("TP", TP, "FP", FP, "TN", TN, "FN", FN)

        return kappa_score, f1, direction,  acc, 0, TP, FP, TN, FN


    def runLR(self, property_name, y=None):
        if y is None:
            y = dt.import1dArray("../data/" + self.data_type + "/bow/binary/phrases/class-" + property_name + "-" + str(
            self.lowest_amt) + "-" + str(self.higher_amt) + "-" + self.classification, file_type="i")
        else:
            y = y[0]
        for i in range(len(y)):
            if y[i] >= 1:
                y[i] = 1
        #x_train, y_train = dt.balanceClasses(x_train, y_train)
        clf = linear_model.LogisticRegression(class_weight="balanced", dual=False)
        clf.fit(self.x_train, y)
        direction = clf.coef_.tolist()[0]
        y_pred = clf.predict(self.x_test)
        y_pred = y_pred.tolist()
        f1 = f1_score(y[:len(y_pred)], y_pred)
        kappa_score = cohen_kappa_score(y[:len(y_pred)], y_pred)
        acc = accuracy_score(y[:len(y_pred)], y_pred)
        TP, FP, TN, FN = self.perf_measure(y, y_pred)

        #ppmi_score, ppmi_ratio = get_ppmi_score(y_pred, property_name)

        return kappa_score, f1, direction,  acc, 0, TP, FP, TN, FN



    def runClassifySVM(self, y_test, y_train):
        clf = svm.LinearSVC(class_weight="balanced")

        clf.fit(self.x_train, y_train)
        y_pred = clf.predict(self.x_test)
        y_pred = y_pred.tolist()
        f1 = f1_score(y_test, y_pred, average="binary")
        acc = accuracy_score(y_test, y_pred)
        return f1, acc

    def runAllSVMs(self, y_test, y_train, property_names, file_name, svm_type, getting_directions, threads, logistic_regression, sparse_array):

        kappa_scores = [0.0] * len(property_names)
        directions = [None] * len(property_names)
        f1_scores = [0.0] * len(property_names)
        accs = [0.0] * len(property_names)
        TPs = [0.0] * len(property_names)
        FPs = [0.0] * len(property_names)
        TNs = [0.0] * len(property_names)
        FNs = [0.0] * len(property_names)

        saved_x_trans = None
        saved_test_x_trans = None
        indexes_to_remove = []
        threads_indexes_to_remove = []
        for y in range(0, len(property_names), threads):
            property_names_a = [None] * threads
            sparse_selection = [None] * threads
            get_kappa_a = [None] * threads
            for t in range(threads):
                try:
                    property_names_a[t] = property_names[y+t]
                    if sparse_array is not None:
                        sparse_selection[t] = sparse_array[y+t]
                except IndexError as e:
                    break
            for p in range(len(property_names_a)):
                if property_names_a[p] is None:
                    indexes_to_remove.append(y+p)
                    threads_indexes_to_remove.append(p)

            kappa_scores = np.delete(np.asarray(kappa_scores), indexes_to_remove, axis=0)
            directions = np.delete(np.asarray(directions), indexes_to_remove, axis=0)
            f1_scores = np.delete(np.asarray(f1_scores), indexes_to_remove, axis=0)
            TPs = np.delete(np.asarray(TPs), indexes_to_remove, axis=0)
            FPs = np.delete(np.asarray(FPs), indexes_to_remove, axis=0)
            TNs = np.delete(np.asarray(TNs), indexes_to_remove, axis=0)
            FNs = np.delete(np.asarray(FNs), indexes_to_remove, axis=0)
            property_names = np.delete(np.asarray(property_names), indexes_to_remove, axis=0)
            property_names_a = np.delete(np.asarray(property_names_a), threads_indexes_to_remove, axis=0)

            sparse_selection = np.delete(sparse_selection, threads_indexes_to_remove, axis=0)

            pool = ThreadPool(threads)
            if logistic_regression:
                if sparse_array is None:
                    kappa = pool.starmap(self.runLR, zip(property_names_a))
                else:
                    kappa = pool.starmap(self.runLR, zip(property_names_a, zip(sparse_selection)))

            else:
                if sparse_array is None:
                    kappa = pool.starmap(self.runSVM, zip(property_names_a))
                else:
                    kappa = pool.starmap(self.runSVM, zip(property_names_a, zip(sparse_selection)))

            pool.close()
            pool.join()
            for t in range(len(kappa)):
                kappa_scores[y+t] = kappa[t][0]
                f1_scores[y+t] = kappa[t][1]
                directions[y+t] = kappa[t][2]
                accs[y+t] = kappa[t][3]
                TPs[y+t] = kappa[t][5]
                FPs[y+t] = kappa[t][6]
                TNs[y+t] = kappa[t][7]
                FNs[y+t] = kappa[t][8]
                print(y, "/", len(property_names), "Score", kappa[t][0], "f1", kappa[t][1], "acc", kappa[t][3], property_names_a[t])



        return kappa_scores, directions, f1_scores, property_names, accs, TPs, FPs, TNs, FNs

    def __init__(self, vector_path, class_path, property_names_fn, file_name, svm_type, training_size=10000,  lowest_count=200,
                      highest_count=21470000, get_kappa=True, get_f1=True, single_class=True, data_type="movies",
                      getting_directions=True, threads=1, chunk_amt = 0, chunk_id = 0,
                     rewrite_files=False, classification="all", loc ="../data/", logistic_regression=False, sparse_array_fn=None,
                 only_these_fn=None):

        self.get_kappa = True
        self.get_f1 = get_f1
        self.data_type = data_type
        self.classification = classification
        self.lowest_amt = lowest_count
        self.higher_amt = highest_count

        if chunk_amt > 0:
            file_name = file_name + " CID" + str(chunk_id) + " CAMT" + str(chunk_amt)

        directions_fn = loc + data_type + "/svm/directions/" + file_name + ".txt"
        ktau_scores_fn = loc + data_type + "/svm/f1/" + file_name + ".txt"
        kappa_fn = loc + data_type + "/svm/kappa/" + file_name + ".txt"
        acc_fn = loc + data_type + "/svm/acc/" + file_name + ".txt"
        TP_fn = loc + data_type + "/svm/stats/TP " + file_name + ".txt"
        FP_fn = loc + data_type + "/svm/stats/FP " + file_name + ".txt"
        TN_fn = loc + data_type + "/svm/stats/TN " + file_name + ".txt"
        FN_fn = loc + data_type + "/svm/stats/FN " + file_name + ".txt"

        all_fns = [directions_fn, kappa_fn]
        if dt.allFnsAlreadyExist(all_fns) and not rewrite_files:
            print("Skipping task", "getSVMResults")
            return
        else:
            print("Running task", "getSVMResults")

        y_train = 0
        y_test = 0
        vectors = np.asarray(dt.import2dArray(vector_path))
        print("imported vectors")
        if not getting_directions:
            classes = np.asarray(dt.import2dArray(class_path))
            print("imported classes")



        property_names = dt.import1dArray(property_names_fn)
        print("imported propery names")
        if chunk_amt > 0:
            if chunk_id == chunk_amt-1:
                chunk = int(len(property_names) / chunk_amt)
                multiply = chunk_amt-1
                property_names = property_names[chunk*multiply:]
            else:
                property_names = dt.chunks(property_names, int((len(property_names) / chunk_amt)))[chunk_id]

        if sparse_array_fn is not None:
            sparse_array = dt.import2dArray(sparse_array_fn)
        else:
            sparse_array = None

        if sparse_array is not None:
            for s in range(len(sparse_array)):
                if len(np.nonzero(sparse_array[s])[0]) <= 1:
                    print("WILL FAIL", s, len(np.nonzero(sparse_array[s])[0]))
                else:
                    print(len(np.nonzero(sparse_array[s])[0]))

        if not getting_directions:
            x_train, x_test, y_train, y_test = train_test_split(vectors, classes, test_size=0.3, random_state=0)
        else:
            x_train = vectors
            x_test = vectors

        if get_f1:
            y_train = y_train.transpose()
            y_test = y_test.transpose()
            print("transpoosed")
        self.x_train = x_train
        self.x_test = x_test
        self.y_train = y_train
        self.y_test = y_test

        if only_these_fn is not None:
            only_these = dt.import1dArray(only_these_fn, "s")
            inds = []
            for s in range(len(property_names)):
                for o in only_these:
                    if property_names[s] == o:
                        inds.append(s)
                        break
            sparse_array = sparse_array[inds]
            property_names = property_names[inds]

        if self.get_f1 is False:
            print("running svms")
            kappa_scores, directions, f1_scores, property_names, accs, TPs, FPs, TNs, FNs = self.runAllSVMs(y_test, y_train,property_names, file_name,
                                                               svm_type, getting_directions, threads, logistic_regression, sparse_array)

            dt.write1dArray(kappa_scores, kappa_fn)
            dt.write2dArray(directions, directions_fn)
            dt.write1dArray(f1_scores, ktau_scores_fn)
            dt.write1dArray(accs, acc_fn)
            dt.write1dArray(TPs, TP_fn)
            dt.write1dArray(FPs, FP_fn)
            dt.write1dArray(TNs, TN_fn)
            dt.write1dArray(FNs, FN_fn)
            dt.write1dArray(property_names, property_names_fn + file_name + ".txt")
        else:
            final_f1 = []
            final_acc = []
            for y in range(len(y_train)):
                f1, acc = self.runClassifySVM(y_test[y], y_train[y])
                print(f1, acc)
                final_f1.append(f1)
                final_acc.append(acc)
            dt.write1dArray(final_f1, ktau_scores_fn)
            dt.write1dArray(final_acc, acc_fn)


def createSVM(vector_path, class_path, property_names_fn, file_name, svm_type, training_size=10000,  lowest_count=200,
                      highest_count=21470000, get_kappa=True, get_f1=True, single_class=True, data_type="movies",
                      getting_directions=True, threads=1, chunk_amt=0, chunk_id=0,
                     rewrite_files=False, classification="genres", lowest_amt=0, loc="../data/", logistic_regression=False,
              sparse_array_fn=None, only_these_fn=None):
    svm = SVM(vector_path, class_path, property_names_fn, file_name, svm_type, training_size=training_size,  lowest_count=lowest_count,
                      highest_count=highest_count, get_kappa=get_kappa, get_f1=get_f1, single_class=single_class, data_type=data_type,
                      getting_directions=getting_directions, threads=threads, chunk_amt=chunk_amt, chunk_id=chunk_id,
                     rewrite_files=rewrite_files, classification=classification, loc=loc, logistic_regression=logistic_regression,
              sparse_array_fn=sparse_array_fn, only_these_fn=only_these_fn)


def main(vectors_fn, classes_fn, property_names, training_size, file_name, lowest_count, largest_count):
    SVM(vectors_fn, classes_fn, property_names, lowest_count=lowest_count,
        training_size=training_size, file_name=file_name, largest_count=largest_count)



"""
data_type = "newsgroups"
classify = "newsgroups"
file_name = "/class-all-1-1"
vector_path = "../data/"+data_type+"/nnet/spaces/" + file_name + ".txt"
classification_path = "../data/"+data_type+"/classify/" + classify + "/class-All"
class_names_fn = "../data/"+data_type+"/classify/" + classify + "/names.txt"
lowest_amt = 50
highest_count = 10
svm_type = "svm"
rewrite_files = True
classification = classify
chunk_amt = 0
chunk_id = 0

createSVM(vector_path, classification_path, class_names_fn, file_name, lowest_count=lowest_amt,
                                  highest_count=highest_count, data_type=data_type, get_kappa=False,
                                  get_f1=True, single_class=True,svm_type=svm_type, getting_directions=False, threads=1,
                                  rewrite_files=rewrite_files,
                                  classification=classification, lowest_amt=lowest_amt, chunk_amt=chunk_amt,
                                  chunk_id=chunk_id)
"""
"""
data_type = "wines"
file_name = "winesppmirankE500DS[1000, 500, 250, 100, 50]L0DN0.3reluSFT0L050ndcgSimilarityClusteringIT3000"
class_name = "types"
# Get SVM scores
svm_type = "svm"
lowest_count = 200
highest_count = 10000
cluster_amt = 200
split = 0.9
vector_path = "../data/" + data_type + "/rank/numeric/"+file_name+".txt"
class_path = "../data/" + data_type + "/classify/"+class_name+"/class-all"
property_names_fn = "../data/" + data_type + "/classify/"+class_name+"/names.txt"
file_name = file_name + "genre"
#getSVMResults(vector_path, class_path, property_names_fn, file_name, lowest_count=lowest_count, data_type=data_type, get_kappa=False, get_f1=True, highest_count=highest_count, svm_type=svm_type, rewrite_files=True)
"""

"""
ppmi = np.asarray(dt.import2dArray("../data/movies/bow/ppmi/class-all")).transpose()

from sklearn import decomposition

pca = decomposition.PCA(n_components=100)
pca.fit(ppmi)
pca = pca.transform(ppmi)

dt.write2dArray(pca, "../data/movies/nnet/spaces/pca.txt")

file_name = "pca"

# Get SVM scores
lowest_count = 200
highest_count = 10000
vector_path = "../data/movies/nnet/spaces/"+file_name+".txt"
class_path = "../data/movies/bow/binary/phrases/class-all-200"
property_names_fn = "../data/movies/bow/names/" + str(lowest_count) + ".txt"
getSVMResults(vector_path, class_path, property_names_fn, file_name, lowest_count=lowest_count, highest_count=highest_count)


property_names_fn = "../data/movies/classify/keywords/names.txt"
class_path = "../data/movies/classify/keywords/class-All"
file_name = "filmsPPMIDropoutL1100DNNonerelusoftplusadagradkullback_leibler_divergence"
vector_path = "../data/movies/nnet/spaces/"+file_name+".txt"
file_name = "films100"
vector_path = "../data/movies/nnet/spaces/"+file_name+".txt"
getSVMResults(vector_path, class_path, property_names_fn, "LinearGenre"+file_name)
getSVMResults(vector_path, class_path, property_names_fn, "LinearGenre"+file_name)

path="newdata/spaces/"
#path="filmdata/films200.mds/"
#array = ["700", "400", "100"]
filenames = ["films100N0.6H75L1", "films100N0.6H50L2", "films100N0.6H25L3",
             "films100N0.6H50L4", "films100N0.6H75L5", "films100N0.6H100L6"]

"""

"AUTOENCODER0.2tanhtanhmse15tanh[1000]4SDA1","AUTOENCODER0.2tanhtanhmse60tanh[200]4SDA2","AUTOENCODER0.2tanhtanhmse30tanh[1000]4SDA3",
"AUTOENCODER0.2tanhtanhmse60tanh[200]4SDA4"
"""
cut = 100
for f in range(len(filenames)):
    newSVM = SVM(vector_path=path+filenames[f]+".mds", class_path="filmdata/classesPhrases/class-All", lowest_count=cut, training_size=10000, file_name=filenames[f]+"LS", largest_count=9999999999)
"""
"""
if  __name__ =='__main__':main(vectors, classes, property_names, file_name, training_size,  lowest_count, largest_count)
"""
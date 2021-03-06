
from gensim.corpora import Dictionary
from gensim.utils import deaccent
import data as dt
from gensim.models.phrases import Phraser
from nltk.corpus import stopwords
import numpy as np
from keras.utils import to_categorical
import string
from sklearn.datasets import fetch_20newsgroups
import re
from os.path import expanduser
from keras.datasets import imdb
from sklearn.feature_extraction.text import CountVectorizer
from gensim.matutils import corpus2csc
import scipy.sparse as sp
import data as dt
from sklearn.decomposition import TruncatedSVD
from test_representations import testAll
import sparse_ppmi
from nltk.corpus import reuters
from collections import defaultdict
#import nltk
#nltk.download()

# Has batch processing (haven't figured out how to use it yet)
# Retains punctuation e.g. won't -> "won't"
# Has many additional options
# Seems hard to get vocab, tokens (maybe misunderstanding)
# Retains brackets, etc , e.g. ["(i", "think", "so)"]
# Can make vocab from your own corpus, but has different quirks
def spacyTokenize(corpus):  # Documentation unclear
    tokenized_corpus = np.empty(len(corpus), dtype=np.object)
    tokenized_ids = np.empty(len(corpus), dtype=np.object)
    processed_corpus = np.empty(len(corpus), dtype=np.object)
    for i in range(len(corpus)):
        corpus[i] = corpus[i].replace("\n", " ")
    # vocab_spacy = Vocab(strings=corpus)
    tokenizer_spacy = Tokenizer(nlp.vocab)
    for i in range(len(corpus)):
        spacy_sent = tokenizer_spacy(corpus[i])
        processed_corpus[i] = spacy_sent.text
        tokenized_corpus[i] = list(spacy_sent)
        for j in range(len(tokenized_corpus[i])):
            tokenized_corpus[i][j] = tokenized_corpus[i][j].text
        tokenized_ids[i] = spacy_sent.to_array([spacy.attrs.ID])
        sd = 0
    return processed_corpus, tokenized_corpus, tokenized_ids, [None]


def tokenizeNLTK1(corpus): # This is prob better than current implementation - look into later
    processed_corpus = np.empty(len(corpus), dtype=np.object)
    tokenized_corpus = np.empty(len(corpus), dtype=np.object)
    tokenized_ids = np.empty(len(corpus), dtype=np.object)
    for i in range(len(corpus)):
        i = 0
    return processed_corpus, tokenized_corpus, tokenized_ids

def tokenizeNLTK2(corpus):
    processed_corpus = np.empty(len(corpus), dtype=np.object)
    tokenized_corpus = np.empty(len(corpus), dtype=np.object)
    tokenized_ids = np.empty(len(corpus), dtype=np.object)
    return processed_corpus, tokenized_corpus, tokenized_ids

#PAT_ALPHABETIC = re.compile(r'(((?![\d])\w)+)', re.UNICODE) # stolen from gensim
PAT_ALPHANUMERIC = re.compile(r'((\w)+)', re.UNICODE) # stolen from gensim, but added numbers included
def tokenize(text):
    for match in PAT_ALPHANUMERIC.finditer(text):
        yield match.group()

# Removes punctuation "won't be done, dude-man." = ["wont", "be", "done", "dudeman"]
# Lowercase and deaccenting "cYkět" = ["cyket"]
# Converting to ID's requires separate process using those vocabs. More time
# Finds phrases using gensim, e.g. "mayor" "of" "new" "york" -> "mayor" "of" "new_york"
def naiveTokenizer(corpus):
    tokenized_corpus = np.empty(len(corpus), dtype=np.object)
    for i in range(len(corpus)):
        tokenized_corpus[i] = list(tokenize(corpus[i]))
        for j in reversed(range(len(tokenized_corpus[i]))):
            if len(tokenized_corpus[i][j]) == 1:
                del tokenized_corpus[i][j]
    return tokenized_corpus

def getVocab(tokenized_corpus):
    dct = Dictionary(tokenized_corpus)
    vocab = dct.token2id
    id2token = dct.id2token
    return vocab, dct, id2token

def doc2bow(tokenized_corpus, dct, bowmin):
    dct.filter_extremes(no_below=bowmin) # Most occur in at least 2 documents
    bow = [dct.doc2bow(text) for text in tokenized_corpus]
    bow = corpus2csc(bow)
    vocab = dct.token2id
    return bow, vocab

def filterBow_sklearn(processed_corpus, no_below, no_above): #sklearn is slightly worse here
    tf_vectorizer = CountVectorizer(max_df=no_above, min_df=no_below, stop_words=None)
    print("completed vectorizer")
    tf = tf_vectorizer.fit(processed_corpus)
    feature_names = tf.get_feature_names()
    tf = tf_vectorizer.transform(processed_corpus)
    return tf.transpose(), feature_names

def filterBow(tokenized_corpus, dct, no_below, no_above):
    dct.filter_extremes(no_below=no_below, no_above=no_above)
    filtered_bow = [dct.doc2bow(text) for text in tokenized_corpus]
    filtered_bow = corpus2csc(filtered_bow)
    filtered_vocab = dct.token2id
    return filtered_bow, list(dct.token2id.keys()), filtered_vocab

def removeEmpty(processed_corpus, tokenized_corpus, classes):
    remove_ind = []
    for i in range(len(processed_corpus)):
        if len(tokenized_corpus[i]) < 0:
            print("DEL", processed_corpus[i])
            remove_ind.append(i)
    processed_corpus = np.delete(processed_corpus, remove_ind)
    tokenized_corpus = np.delete(tokenized_corpus, remove_ind)
    classes = np.delete(classes, remove_ind, axis=0)
    return processed_corpus, tokenized_corpus, remove_ind, classes

def preprocess(corpus):
    preprocessed_corpus = np.empty(len(corpus), dtype=np.object)

    table = str.maketrans(dict.fromkeys("\n\r", " ")) # Remove new line characters
    for i in range(len(preprocessed_corpus)):
        preprocessed_corpus[i] = corpus[i].translate(table)

    table = str.maketrans(dict.fromkeys(string.punctuation))
    for i in range(len(corpus)):
        # Lowercase
        preprocessed_corpus[i] = preprocessed_corpus[i].lower()
        # Remove all punctuation
        preprocessed_corpus[i] = preprocessed_corpus[i].translate(table)
        # Replace all whitespace with single whitespace
        preprocessed_corpus[i] = re.sub(r'\s+', ' ', preprocessed_corpus[i])
        # Deaccent
        preprocessed_corpus[i] = deaccent(preprocessed_corpus[i])
        # Strip trailing whitespace
        preprocessed_corpus[i] = preprocessed_corpus[i].strip()

    return preprocessed_corpus

def removeStopWords(tokenized_corpus):
    new_tokenized_corpus = np.empty(len(tokenized_corpus), dtype=np.object)
    stop_words_corpus = np.empty(len(tokenized_corpus), dtype=np.object)
    stop_words = set(stopwords.words('english'))
    for i in range(len(tokenized_corpus)):
        new_tokenized_corpus[i] = [w for w in tokenized_corpus[i] if w not in stop_words]
        stop_words_corpus[i] = " ".join(new_tokenized_corpus[i])
    return new_tokenized_corpus, stop_words_corpus

def tokensToIds(tokenized_corpus, vocab):
    tokenized_ids = np.empty(len(tokenized_corpus), dtype=np.object)
    for i in range(len(tokenized_corpus)):
        ids = np.empty(len(tokenized_corpus[i]), dtype=np.object)
        for t in range(len(tokenized_corpus[i])):
            ids[t] = vocab[tokenized_corpus[i][t]]
        tokenized_ids[i] = ids
    return tokenized_ids

# This causes OOM error. Need to rework
def ngrams(tokenized_corpus):  # Increase the gram amount by 1
    processed_corpus = np.empty(len(tokenized_corpus), dtype=np.object)
    phrases = Phrases(tokenized_corpus)
    gram = Phraser(phrases)
    for i in range(len(tokenized_corpus)):
        tokenized_corpus[i] = gram[tokenized_corpus[i]]
        processed_corpus[i] = " ".join(tokenized_corpus[i])
    return processed_corpus, tokenized_corpus

def getPCA(tf, depth):
    svd = TruncatedSVD(n_components=depth) # use the scipy algorithm "arpack"
    pos = svd.fit_transform(tf)
    return pos

def averageWV(tokenized_corpus, depth):

    print("")

def averageWVPPMI(tokenized_corpus, ppmi):
    print("")

# For sentiment etc
def makeCorpusFromIds(tokenized_ids, vocab):
    vocab = {k:(v+0) for k,v in vocab.items()}
    vocab["<UNK>"] = 0
    vocab["<START>"] = 1
    vocab["<OOV>"] = 2
    id_to_word = {value:key for key,value in vocab.items()}

    processed_corpus = np.empty(shape=(len(tokenized_ids)), dtype=np.object)  # Have to recreate original word vectors
    for s in range(len(tokenized_ids)):
        word_sentence = []
        for w in range(len(tokenized_ids[s])):
            word_sentence.append(id_to_word[tokenized_ids[s][w]])
        processed_corpus[s] = " ".join(word_sentence)

    return processed_corpus



def main(data_type, output_folder, grams,  no_below, no_above, bowmin):
    if data_type == "newsgroups":
        newsgroups = fetch_20newsgroups(subset='all', shuffle=False, remove=("headers", "footers", "quotes"))
        corpus = newsgroups.data
        classes = newsgroups.target
        encoding_type = "utf8"
    elif data_type == "sentiment":
        (x_train, y_train), (x_test, y_test) = imdb.load_data(num_words=0, skip_top=0, index_from=0, seed=113)
        corpus = np.concatenate((x_train, x_test), axis=0)
        classes = np.concatenate((y_train, y_test), axis=0)
        corpus = makeCorpusFromIds(corpus, imdb.get_word_index())
        encoding_type = "utf8"
    else:
        corpus = dt.import1dArray(output_folder + "duplicate_removed_docs.txt")
        classes = dt.import2dArray(output_folder + "duplicate_removed_classes.txt", "i")
        encoding_type = "utf8"

    file_name = "simple_numeric"
    processed_corpus = preprocess(corpus)
    tokenized_corpus = naiveTokenizer(processed_corpus)
    vocab, dct, id2token = getVocab(tokenized_corpus)
    processed_corpus, tokenized_corpus, remove_ind, classes = removeEmpty(processed_corpus, tokenized_corpus, classes)
    bow, bow_vocab = doc2bow(tokenized_corpus, dct, bowmin)
    print(bowmin, len(list(bow_vocab.keys())), "|||", bow.shape)
    filtered_bow, word_list, filtered_vocab = filterBow(tokenized_corpus, dct, no_below, no_above)
    tokenized_ids = tokensToIds(tokenized_corpus, vocab)
    print(output_folder + file_name + "_remove.npy")
    np.save(output_folder + file_name + "_remove.npy", remove_ind)
    np.save(output_folder + file_name + "_corpus.npy", tokenized_corpus)
    np.save(output_folder + file_name + "_tokenized_corpus.npy", tokenized_ids)
    np.save(output_folder + file_name + "_vocab " + str(bowmin) + ".npy", bow_vocab)
    np.save(output_folder + file_name + "_filtered_vocab.npy", filtered_vocab)
    dt.write1dArray(processed_corpus, output_folder + file_name + "_corpus_processed.txt", encoding=encoding_type)
    np.save(output_folder + file_name + "_classes.npy", classes)
    if data_type != "reuters":
        np.save(output_folder + file_name + "_classes_categorical.npy", to_categorical(classes))
    sp.save_npz(output_folder + file_name + ".npz", bow)
    dt.write1dArray(word_list, output_folder + file_name + "_words.txt", encoding=encoding_type)
    dt.write1dArray(list(bow_vocab.keys()), output_folder + file_name + "_all_words_2.txt", encoding=encoding_type)


    """
    if grams > 0:
        for i in range(2, grams):  # Up to 5-length grams
            processed_corpus, tokenized_corpus = ngrams(tokenized_corpus)
            vocab, dct, id2token = getVocab(tokenized_corpus)
            bow = doc2bow(tokenized_corpus, dct, 100, 10)
            tokenized_ids = tokensToIds(tokenized_corpus, vocab)
            np.save(output_folder + file_name + "_corpus " + str(i) + "-gram" + ".npy", tokenized_corpus)
            np.save(output_folder + file_name + "_tokenized_corpus " + str(i) + "-gram" + ".npy", tokenized_ids)
            np.save(output_folder + file_name + "_vocab " + str(i) + "-gram" + ".npy", vocab)
            dt.write1dArray(processed_corpus, output_folder + file_name + "_corpus_processed " + str(i) + "-gram" + ".txt")
            sp.save_npz(output_folder + file_name + "_bow " + str(i) + "-gram" + ".npz", bow)
            dt.write1dArray(word_list, output_folder + file_name + "_words.txt")
    """

    file_name += "_stopwords"

    filtered_ppmi_fn = "../data/"+data_type+"/bow/ppmi/" + file_name + "_ppmi " + str(no_below) + "-" + str(
        no_above) + "-all.npz"
    ppmi_fn = "../data/"+data_type+"/bow/ppmi/" + file_name + "_ppmi " + str(bowmin) + "-all.npz"
    bow_fn = "../data/"+data_type+"/bow/frequency/phrases/" + file_name + "_bow " + str(bowmin) + "-all.npz"
    filtered_bow_fn = "../data/"+data_type+"/bow/frequency/phrases/" + file_name + "_bow "  + str(
        no_below) +  "-" + str(no_above) + "-all.npz"

    # Re-intialize so that we don't start with an already filtered corpus

    tokenized_corpus, processed_corpus = removeStopWords(tokenized_corpus)
    processed_corpus, tokenized_corpus, remove_ind, classes = removeEmpty(processed_corpus, tokenized_corpus, classes)
    vocab, dct, id2token = getVocab(tokenized_corpus)
    bow, bow_vocab = doc2bow(tokenized_corpus, dct, bowmin)
    print(bowmin, len(list(bow_vocab.keys())), "|||", bow.shape)
    filtered_bow, word_list, filtered_vocab = filterBow(tokenized_corpus, dct, no_below, no_above)
    tokenized_ids = tokensToIds(tokenized_corpus, vocab)

    print(output_folder + file_name + "_remove.npy")
    print(output_folder + file_name + "_corpus.npy")
    print(output_folder + file_name + "_tokenized_corpus.npy")
    print(output_folder + file_name + "_id2token.npy")
    print(output_folder + file_name + "_vocab " + str(bowmin) + ".npy")
    print(output_folder + file_name + "_corpus_processed.txt")
    print(output_folder + file_name + "_classes.npy")
    print(output_folder + file_name + "_classes_categorical.npy")
    np.save(output_folder + file_name + "id2token.npy", id2token)
    np.save(output_folder + file_name + "_remove.npy", remove_ind)
    np.save(output_folder + file_name + "_vocab " + str(bowmin) + ".npy", bow_vocab)
    np.save(output_folder + file_name + "_filtered_vocab.npy", filtered_vocab)
    np.save(output_folder + file_name + "_corpus.npy", tokenized_corpus)
    np.save(output_folder + file_name + "_tokenized_corpus.npy", tokenized_ids)
    dt.write1dArray(processed_corpus, output_folder + file_name + "_corpus_processed.txt", encoding=encoding_type)
    np.save(output_folder + file_name + "_classes.npy", classes)
    if data_type != "reuters":
        np.save(output_folder + file_name + "_classes_categorical.npy", to_categorical(classes))

    print("------------------- Saved most, moving to PPMI etc", file_name)

    print(bow_fn)
    print(filtered_bow_fn)
    sp.save_npz(bow_fn, bow)
    sp.save_npz(filtered_bow_fn, filtered_bow)

    dt.write1dArray(word_list, "../data/"+data_type+"/bow/names/" + file_name + "_words " +
                    str(no_below) + "-" + str(no_above) + "-all.txt", encoding=encoding_type)

    dt.write1dArray(list(bow_vocab.keys()), "../data/"+data_type+"/bow/names/" + file_name + "all_words_2_no_sw.txt", encoding=encoding_type)
    filtered_bow = filtered_bow.transpose()
    ppmi = sparse_ppmi.convertPPMISparse(filtered_bow)
    filtered_ppmi_sparse = sp.csr_matrix(ppmi).transpose()

    print(filtered_ppmi_fn)
    sp.save_npz(filtered_ppmi_fn, filtered_ppmi_sparse)

    if data_type == "reuters":
        testAll(["filtered_freq_bow", "filtered_ppmi_bow"],
                [filtered_ppmi_sparse.transpose().todense(), filtered_bow.todense()],
                [classes, classes],
                data_type)
    else:
        testAll(["filtered_freq_bow", "filtered_ppmi_bow"], [filtered_ppmi_sparse.transpose().todense(), filtered_bow.todense()], [to_categorical(classes), to_categorical(classes)],
                data_type)

    # Create PCA
    #classes = dt.import2dArray("../data/movies/classify/genres/class-all", "i")
    #bow = sp.csr_matrix(dt.import2dArray("../data/movies/bow/frequency/phrases/class-all-15-5-genres", "i")).transpose()
    ppmi = sparse_ppmi.convertPPMISparse(bow)
    ppmi_sparse = sp.csr_matrix(ppmi).transpose()

    print(ppmi_fn)
    sp.save_npz(ppmi_fn, ppmi_sparse)

    pca_size = [50, 100, 200]
    for p in pca_size:
        pca_fn = "../data/"+data_type+"/nnet/spaces/" + file_name + "_ppmi " + str(
            bowmin) + " S" + str(p) +  "-all.npy"
        PCA_ppmi = getPCA(ppmi_sparse, p)
        np.save(pca_fn, PCA_ppmi)
    """
    if grams > 0:
        for i in range(2, grams+1):  # Up to 5-length grams

            filtered_ppmi_fn = "../data/"+data_type+"/bow/ppmi/" + file_name + "_ppmi " + str(
                grams) + "-gram" + str(no_below) + "-" + str(
                no_above) + "-all.npz"
            ppmi_fn = "../data/"+data_type+"/bow/ppmi/" + file_name + "_ppmi " + str(
                grams) + "-gram2" + "-all.npz"
            bow_fn = "../data/"+data_type+"/bow/frequency/phrases/" + file_name + "_bow " + str(
                grams) + "-gram2" + "-all.npz"
            filtered_bow_fn = "../data/"+data_type+"/bow/frequency/phrases/" + file_name + "_bow " + str(
                grams) + "-gram" + str(
                no_below) + \
                              "-" + str(no_above) + "-all.npz"

            processed_corpus, tokenized_corpus = ngrams(tokenized_corpus)
            vocab, dct = getVocab(tokenized_corpus)
            bow = doc2bow(tokenized_corpus, dct, 0)
            filtered_bow, word_list = filterBow(tokenized_corpus, dct, no_below-bowmin, no_above)
            tokenized_ids = tokensToIds(tokenized_corpus, vocab)
            np.save(output_folder + file_name + "_corpus " + str(i) + "-gram" + ".npy", tokenized_corpus)
            np.save(output_folder + file_name + "_tokenized_corpus " + str(i) + "-gram" + ".npy", tokenized_ids)
            np.save(output_folder + file_name + "_vocab " + str(i) + "-gram" + ".npy", vocab)
            dt.write1dArray(processed_corpus, output_folder + file_name + "_corpus_processed " + str(i) + "-gram" + ".txt")

            sp.save_npz(bow_fn, bow)
            sp.save_npz(filtered_bow_fn, filtered_bow)

            dt.write1dArray(word_list, "../data/"+data_type+"/bow/names/" + file_name + "_words "  + str(i) + "-gram"  +
                            str(no_below) + "-" + str(no_above) + "-all.txt")
            filtered_bow = filtered_bow.transpose()
            ppmi = sparse_ppmi.convertPPMISparse(filtered_bow)
            filtered_ppmi_sparse = sp.csr_matrix(ppmi).transpose()
            sp.save_npz(filtered_ppmi_fn, filtered_ppmi_sparse)
            # Create PCA

            bow = bow.transpose()
            ppmi = sparse_ppmi.convertPPMISparse(bow)
            ppmi_sparse = sp.csr_matrix(ppmi).transpose()
            sp.save_npz(ppmi_fn, ppmi_sparse)
            pca_fn = "../data/"+data_type+"/nnet/spaces/" + file_name + "_ppmi " + str(grams) + "-gram" + str(
                no_below) + "-" + str(
                no_above) + "-all.npy"

            PCA_ppmi = getPCA(ppmi_sparse, 100)
            np.save(pca_fn, PCA_ppmi)

    """
    """
    file_name += "_stopwords"
    filtered_ppmi_fn = "../data/"+data_type+"/bow/ppmi/" + file_name + "_ppmi " + str(no_below) + "-" + str(
        no_above) + "-all.npz"
    filtered_bow_fn = "../data/"+data_type+"/bow/frequency/phrases/" + file_name + "_bow " + str(
        no_below) + "-" + str(no_above) + "-all.npz"
    pca_fn = "../data/"+data_type+"/nnet/spaces/" + file_name + "_ppmi " +  str(
        no_below) + "-" + str(
        no_above) + "-all.npy"
    filtered_ppmi_sparse = sp.load_npz(filtered_ppmi_fn)
    PCA_ppmi = np.load(pca_fn)
    filtered_bow = sp.load_npz(filtered_bow_fn)
    """
    # Create averaged word vectors
    if data_type == "reuters":
        testAll(["ppmi_pca"], [ PCA_ppmi],
                [classes], data_type)
    else:
        testAll(["ppmi_pca"], [ PCA_ppmi],
                [to_categorical(classes)], data_type)

data_type = "reuters"
if __name__ == '__main__': main(data_type, "../data/raw/"+data_type+"/", 0, 10, 0.95, 2)
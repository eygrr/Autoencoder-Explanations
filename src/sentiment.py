# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import FunctionTransformer
from sklearn.model_selection import train_test_split
import data as dt
import numpy as np
import MovieTasks as mt
import scipy.sparse as sp
# Import the sentiment
from keras.datasets import imdb

def getSplits(vectors, classes, dev=0.8):
    if len(vectors) != 50000 or len(classes) != 50000:
        print("This is not the standard size of 20NG, expected 50000")
        return False

    x_train = vectors[:25000]
    x_test = vectors[25000:]
    y_train = classes[:25000]
    y_test = classes[25000:]

    print("Returning development splits", dev)

    x_dev = x_train[int(len(x_train) * 0.8):]
    y_dev = y_train[int(len(y_train) * 0.8):]
    x_train = x_train[:int(len(x_train) * 0.8)]
    y_train = y_train[:int(len(y_train) * 0.8)]

    print(len(x_test), len(x_test[0]), "x_test")
    print(len(y_test),  "y_test")
    print(len(x_train), len(x_train[0]), "x_train")
    print(len(y_train),  "y_train")

    return x_train, y_train, x_test, y_test, x_dev, y_dev

def everythingElse():
    np.random.seed(1337)
    # Get frequencies, PPMI's, classes. Everything needed for directions
    skip_top = 0
    lowest_amt = skip_top
    highest_amt = 0
    index_from = 2
    classification = "all"
    bigrams = True

    if bigrams is False:
        (x_train, y_train), (x_test, y_test) = imdb.load_data(num_words=highest_amt, skip_top=skip_top, index_from=index_from)
    else:
        (x_train, y_train), (x_test, y_test) = imdb.load_data(num_words=0, skip_top=0, index_from=index_from)

    train_len = len(x_train)
    test_len = len(y_train)

    vectors = np.concatenate((x_train, x_test), axis=0)
    classes = np.concatenate((y_train, y_test), axis=0)
        #vectors = x_train[:int(len(x_train) * 0.8)]
        #classes = y_train[:int(len(y_train) * 0.8)]


    word_to_id = imdb.get_word_index()
    word_to_id = {k:(v+index_from) for k,v in word_to_id.items()}
    word_to_id["<UNK>"] = 0
    word_to_id["<START>"] = 1
    word_to_id["<OOV>"] = 2
    id_to_word = {value:key for key,value in word_to_id.items()}

    word_vectors = np.empty(shape=(len(vectors)), dtype=np.object) # Have to recreate original word vectors
    for s in range(len(vectors)):
        word_sentence = []
        for w in range(len(vectors[s])):
            word_sentence.append(id_to_word[vectors[s][w]])
        word_vectors[s] = word_sentence

    import gensim.models.phrases

    phrases = gensim.models.Phrases(word_vectors)
    bigram = gensim.models.phrases.Phraser(phrases)
    phrase_vectors = [bigram[sentence] for sentence in word_vectors]

    from gensim import corpora
    dictionary = corpora.Dictionary(phrase_vectors)
    dictionary.filter_extremes(no_below=highest_amt)

    dfs_list = []
    words = []
    for i in range(len(dictionary.keys())):
        words.append(dictionary[i])
        dfs_list.append(dictionary.dfs[i])
    dt.write1dArray(words, "../data/sentiment/bow/names/" + str(lowest_amt) + "-" + str(highest_amt) + "-" + classification + ".txt")
    dt.write1dArray(dfs_list, "../data/sentiment/bow/frequency/global/" + str(lowest_amt) + "-" + str(highest_amt) + "-" + classification + ".txt")
    corpus = [dictionary.doc2bow(text) for text in phrase_vectors]

    all_fn = "../data/sentiment/bow/frequency/phrases/class-all-"+str(lowest_amt)+"-"+str(highest_amt)+"-" + classification
    all_fn_binary = "../data/sentiment/bow/binary/phrases/class-all-"+str(lowest_amt)+"-"+str(highest_amt)+"-" + classification

    import gensim.matutils

    corpus = gensim.matutils.corpus2csc(corpus)

    sp.save_npz(all_fn, corpus)

    """
    #all_fn = "../data/sentiment/bow/frequency/phrases/class-all-"+str(lowest_amt)+"-"+str(highest_amt)+"-" + classification
    #corpus = sp.load_npz(all_fn + ".npz")
    print("saving")
    
    ppmi = mt.convertPPMI( corpus)
    
    ppmi_sparse = sp.csr_matrix(ppmi)
    
    ppmi_fn = "../data/sentiment/bow/ppmi/class-all-"+str(lowest_amt)+"-"+str(highest_amt)+"-" + classification
    sp.save_npz(ppmi_fn, ppmi_sparse)
    """
    """
    for key,val in id_to_word.items():
        if val == "that":
            print(key)
    
    ids = np.asarray(list(id_to_word.keys()), dtype=np.int32)
    words = np.asarray(list(id_to_word.values()), dtype="str")
    
    sorted_ids = np.argsort(ids)
    complete_word_list = words[sorted_ids]
    
    word_list = complete_word_list[skip_top+3:highest_amt]
    
    new_word_list = []
    
    new_word_list.append("<UNK>")
    new_word_list.append("<START>")
    new_word_list.append("<OOV>")
    
    
    for i in range(skip_top):
        new_word_list.append("<OOV>")
    
    
    for w in word_list:
        new_word_list.append(w)
    """
    """
    for x in x_train:
        run = False
        for n in range(len(x)):
            if x[n] > highest_amt-1000:
                run = True
        if run:
            try:
                for id in x_train[0]:
                    print(id, end=' ')
                print("")
                for id in x_train[0]:
                    print(complete_word_list[id], end=' ')
                print("")
                for id in x_train[0]:
                    print(new_word_list[id], end=' ')
                print("")
            except KeyError:
                print("fail")
        break
    """
    """
    import codecs
    decoding_table = (
        '\x00'     #  0x00 -> NULL
        '\x01'     #  0x01 -> START OF HEADING
        '\x02'     #  0x02 -> START OF TEXT
        '\x03'     #  0x03 -> END OF TEXT
        '\x04'     #  0x04 -> END OF TRANSMISSION
        '\x05'     #  0x05 -> ENQUIRY
        '\x06'     #  0x06 -> ACKNOWLEDGE
        '\x07'     #  0x07 -> BELL
        '\x08'     #  0x08 -> BACKSPACE
        '\t'       #  0x09 -> HORIZONTAL TABULATION
        '\n'       #  0x0A -> LINE FEED
        '\x0b'     #  0x0B -> VERTICAL TABULATION
        '\x0c'     #  0x0C -> FORM FEED
        '\r'       #  0x0D -> CARRIAGE RETURN
        '\x0e'     #  0x0E -> SHIFT OUT
        '\x0f'     #  0x0F -> SHIFT IN
        '\x10'     #  0x10 -> DATA LINK ESCAPE
        '\x11'     #  0x11 -> DEVICE CONTROL ONE
        '\x12'     #  0x12 -> DEVICE CONTROL TWO
        '\x13'     #  0x13 -> DEVICE CONTROL THREE
        '\x14'     #  0x14 -> DEVICE CONTROL FOUR
        '\x15'     #  0x15 -> NEGATIVE ACKNOWLEDGE
        '\x16'     #  0x16 -> SYNCHRONOUS IDLE
        '\x17'     #  0x17 -> END OF TRANSMISSION BLOCK
        '\x18'     #  0x18 -> CANCEL
        '\x19'     #  0x19 -> END OF MEDIUM
        '\x1a'     #  0x1A -> SUBSTITUTE
        '\x1b'     #  0x1B -> ESCAPE
        '\x1c'     #  0x1C -> FILE SEPARATOR
        '\x1d'     #  0x1D -> GROUP SEPARATOR
        '\x1e'     #  0x1E -> RECORD SEPARATOR
        '\x1f'     #  0x1F -> UNIT SEPARATOR
        ' '        #  0x20 -> SPACE
        '!'        #  0x21 -> EXCLAMATION MARK
        '"'        #  0x22 -> QUOTATION MARK
        '#'        #  0x23 -> NUMBER SIGN
        '$'        #  0x24 -> DOLLAR SIGN
        '%'        #  0x25 -> PERCENT SIGN
        '&'        #  0x26 -> AMPERSAND
        "'"        #  0x27 -> APOSTROPHE
        '('        #  0x28 -> LEFT PARENTHESIS
        ')'        #  0x29 -> RIGHT PARENTHESIS
        '*'        #  0x2A -> ASTERISK
        '+'        #  0x2B -> PLUS SIGN
        ','        #  0x2C -> COMMA
        '-'        #  0x2D -> HYPHEN-MINUS
        '.'        #  0x2E -> FULL STOP
        '/'        #  0x2F -> SOLIDUS
        '0'        #  0x30 -> DIGIT ZERO
        '1'        #  0x31 -> DIGIT ONE
        '2'        #  0x32 -> DIGIT TWO
        '3'        #  0x33 -> DIGIT THREE
        '4'        #  0x34 -> DIGIT FOUR
        '5'        #  0x35 -> DIGIT FIVE
        '6'        #  0x36 -> DIGIT SIX
        '7'        #  0x37 -> DIGIT SEVEN
        '8'        #  0x38 -> DIGIT EIGHT
        '9'        #  0x39 -> DIGIT NINE
        ':'        #  0x3A -> COLON
        ';'        #  0x3B -> SEMICOLON
        '<'        #  0x3C -> LESS-THAN SIGN
        '='        #  0x3D -> EQUALS SIGN
        '>'        #  0x3E -> GREATER-THAN SIGN
        '?'        #  0x3F -> QUESTION MARK
        '@'        #  0x40 -> COMMERCIAL AT
        'A'        #  0x41 -> LATIN CAPITAL LETTER A
        'B'        #  0x42 -> LATIN CAPITAL LETTER B
        'C'        #  0x43 -> LATIN CAPITAL LETTER C
        'D'        #  0x44 -> LATIN CAPITAL LETTER D
        'E'        #  0x45 -> LATIN CAPITAL LETTER E
        'F'        #  0x46 -> LATIN CAPITAL LETTER F
        'G'        #  0x47 -> LATIN CAPITAL LETTER G
        'H'        #  0x48 -> LATIN CAPITAL LETTER H
        'I'        #  0x49 -> LATIN CAPITAL LETTER I
        'J'        #  0x4A -> LATIN CAPITAL LETTER J
        'K'        #  0x4B -> LATIN CAPITAL LETTER K
        'L'        #  0x4C -> LATIN CAPITAL LETTER L
        'M'        #  0x4D -> LATIN CAPITAL LETTER M
        'N'        #  0x4E -> LATIN CAPITAL LETTER N
        'O'        #  0x4F -> LATIN CAPITAL LETTER O
        'P'        #  0x50 -> LATIN CAPITAL LETTER P
        'Q'        #  0x51 -> LATIN CAPITAL LETTER Q
        'R'        #  0x52 -> LATIN CAPITAL LETTER R
        'S'        #  0x53 -> LATIN CAPITAL LETTER S
        'T'        #  0x54 -> LATIN CAPITAL LETTER T
        'U'        #  0x55 -> LATIN CAPITAL LETTER U
        'V'        #  0x56 -> LATIN CAPITAL LETTER V
        'W'        #  0x57 -> LATIN CAPITAL LETTER W
        'X'        #  0x58 -> LATIN CAPITAL LETTER X
        'Y'        #  0x59 -> LATIN CAPITAL LETTER Y
        'Z'        #  0x5A -> LATIN CAPITAL LETTER Z
        '['        #  0x5B -> LEFT SQUARE BRACKET
        '\\'       #  0x5C -> REVERSE SOLIDUS
        ']'        #  0x5D -> RIGHT SQUARE BRACKET
        '^'        #  0x5E -> CIRCUMFLEX ACCENT
        '_'        #  0x5F -> LOW LINE
        '`'        #  0x60 -> GRAVE ACCENT
        'a'        #  0x61 -> LATIN SMALL LETTER A
        'b'        #  0x62 -> LATIN SMALL LETTER B
        'c'        #  0x63 -> LATIN SMALL LETTER C
        'd'        #  0x64 -> LATIN SMALL LETTER D
        'e'        #  0x65 -> LATIN SMALL LETTER E
        'f'        #  0x66 -> LATIN SMALL LETTER F
        'g'        #  0x67 -> LATIN SMALL LETTER G
        'h'        #  0x68 -> LATIN SMALL LETTER H
        'i'        #  0x69 -> LATIN SMALL LETTER I
        'j'        #  0x6A -> LATIN SMALL LETTER J
        'k'        #  0x6B -> LATIN SMALL LETTER K
        'l'        #  0x6C -> LATIN SMALL LETTER L
        'm'        #  0x6D -> LATIN SMALL LETTER M
        'n'        #  0x6E -> LATIN SMALL LETTER N
        'o'        #  0x6F -> LATIN SMALL LETTER O
        'p'        #  0x70 -> LATIN SMALL LETTER P
        'q'        #  0x71 -> LATIN SMALL LETTER Q
        'r'        #  0x72 -> LATIN SMALL LETTER R
        's'        #  0x73 -> LATIN SMALL LETTER S
        't'        #  0x74 -> LATIN SMALL LETTER T
        'u'        #  0x75 -> LATIN SMALL LETTER U
        'v'        #  0x76 -> LATIN SMALL LETTER V
        'w'        #  0x77 -> LATIN SMALL LETTER W
        'x'        #  0x78 -> LATIN SMALL LETTER X
        'y'        #  0x79 -> LATIN SMALL LETTER Y
        'z'        #  0x7A -> LATIN SMALL LETTER Z
        '{'        #  0x7B -> LEFT CURLY BRACKET
        '|'        #  0x7C -> VERTICAL LINE
        '}'        #  0x7D -> RIGHT CURLY BRACKET
        '~'        #  0x7E -> TILDE
        '\x7f'     #  0x7F -> DELETE
        '\u20ac'   #  0x80 -> EURO SIGN
        '\ufffe'   #  0x81 -> UNDEFINED
        '\u201a'   #  0x82 -> SINGLE LOW-9 QUOTATION MARK
        '\u0192'   #  0x83 -> LATIN SMALL LETTER F WITH HOOK
        '\u201e'   #  0x84 -> DOUBLE LOW-9 QUOTATION MARK
        '\u2026'   #  0x85 -> HORIZONTAL ELLIPSIS
        '\u2020'   #  0x86 -> DAGGER
        '\u2021'   #  0x87 -> DOUBLE DAGGER
        '\u02c6'   #  0x88 -> MODIFIER LETTER CIRCUMFLEX ACCENT
        '\u2030'   #  0x89 -> PER MILLE SIGN
        '\u0160'   #  0x8A -> LATIN CAPITAL LETTER S WITH CARON
        '\u2039'   #  0x8B -> SINGLE LEFT-POINTING ANGLE QUOTATION MARK
        '\u0152'   #  0x8C -> LATIN CAPITAL LIGATURE OE
        '\ufffe'   #  0x8D -> UNDEFINED
        '\u017d'   #  0x8E -> LATIN CAPITAL LETTER Z WITH CARON
        '\ufffe'   #  0x8F -> UNDEFINED
        '\ufffe'   #  0x90 -> UNDEFINED
        '\u2018'   #  0x91 -> LEFT SINGLE QUOTATION MARK
        '\u2019'   #  0x92 -> RIGHT SINGLE QUOTATION MARK
        '\u201c'   #  0x93 -> LEFT DOUBLE QUOTATION MARK
        '\u201d'   #  0x94 -> RIGHT DOUBLE QUOTATION MARK
        '\u2022'   #  0x95 -> BULLET
        '\u2013'   #  0x96 -> EN DASH
        '\u2014'   #  0x97 -> EM DASH
        '\u02dc'   #  0x98 -> SMALL TILDE
        '\u2122'   #  0x99 -> TRADE MARK SIGN
        '\u0161'   #  0x9A -> LATIN SMALL LETTER S WITH CARON
        '\u203a'   #  0x9B -> SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
        '\u0153'   #  0x9C -> LATIN SMALL LIGATURE OE
        '\ufffe'   #  0x9D -> UNDEFINED
        '\u017e'   #  0x9E -> LATIN SMALL LETTER Z WITH CARON
        '\u0178'   #  0x9F -> LATIN CAPITAL LETTER Y WITH DIAERESIS
        '\xa0'     #  0xA0 -> NO-BREAK SPACE
        '\xa1'     #  0xA1 -> INVERTED EXCLAMATION MARK
        '\xa2'     #  0xA2 -> CENT SIGN
        '\xa3'     #  0xA3 -> POUND SIGN
        '\xa4'     #  0xA4 -> CURRENCY SIGN
        '\xa5'     #  0xA5 -> YEN SIGN
        '\xa6'     #  0xA6 -> BROKEN BAR
        '\xa7'     #  0xA7 -> SECTION SIGN
        '\xa8'     #  0xA8 -> DIAERESIS
        '\xa9'     #  0xA9 -> COPYRIGHT SIGN
        '\xaa'     #  0xAA -> FEMININE ORDINAL INDICATOR
        '\xab'     #  0xAB -> LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
        '\xac'     #  0xAC -> NOT SIGN
        '\xad'     #  0xAD -> SOFT HYPHEN
        '\xae'     #  0xAE -> REGISTEREvectorsD SIGN
        '\xaf'     #  0xAF -> MACRON
        '\xb0'     #  0xB0 -> DEGREE SIGN
        '\xb1'     #  0xB1 -> PLUS-MINUS SIGN
        '\xb2'     #  0xB2 -> SUPERSCRIPT TWO
        '\xb3'     #  0xB3 -> SUPERSCRIPT THREE
        '\xb4'     #  0xB4 -> ACUTE ACCENT
        '\xb5'     #  0xB5 -> MICRO SIGN
        '\xb6'     #  0xB6 -> PILCROW SIGN
        '\xb7'     #  0xB7 -> MIDDLE DOT
        '\xb8'     #  0xB8 -> CEDILLA
        '\xb9'     #  0xB9 -> SUPERSCRIPT ONE
        '\xba'     #  0xBA -> MASCULINE ORDINAL INDICATOR
        '\xbb'     #  0xBB -> RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
        '\xbc'     #  0xBC -> VULGAR FRACTION ONE QUARTER
        '\xbd'     #  0xBD -> VULGAR FRACTION ONE HALF
        '\xbe'     #  0xBE -> VULGAR FRACTION THREE QUARTERS
        '\xbf'     #  0xBF -> INVERTED QUESTION MARK
        '\xc0'     #  0xC0 -> LATIN CAPITAL LETTER A WITH GRAVE
        '\xc1'     #  0xC1 -> LATIN CAPITAL LETTER A WITH ACUTE
        '\xc2'     #  0xC2 -> LATIN CAPITAL LETTER A WITH CIRCUMFLEX
        '\xc3'     #  0xC3 -> LATIN CAPITAL LETTER A WITH TILDE
        '\xc4'     #  0xC4 -> LATIN CAPITAL LETTER A WITH DIAERESIS
        '\xc5'     #  0xC5 -> LATIN CAPITAL LETTER A WITH RING ABOVE
        '\xc6'     #  0xC6 -> LATIN CAPITAL LETTER AE
        '\xc7'     #  0xC7 -> LATIN CAPITAL LETTER C WITH CEDILLA
        '\xc8'     #  0xC8 -> LATIN CAPITAL LETTER E WITH GRAVE
        '\xc9'     #  0xC9 -> LATIN CAPITAL LETTER E WITH ACUTE
        '\xca'     #  0xCA -> LATIN CAPITAL LETTER E WITH CIRCUMFLEX
        '\xcb'     #  0xCB -> LATIN CAPITAL LETTER E WITH DIAERESIS
        '\xcc'     #  0xCC -> LATIN CAPITAL LETTER I WITH GRAVE
        '\xcd'     #  0xCD -> LATIN CAPITAL LETTER I WITH ACUTE
        '\xce'     #  0xCE -> LATIN CAPITAL LETTER I WITH CIRCUMFLEX
        '\xcf'     #  0xCF -> LATIN CAPITAL LETTER I WITH DIAERESIS
        '\xd0'     #  0xD0 -> LATIN CAPITAL LETTER ETH
        '\xd1'     #  0xD1 -> LATIN CAPITAL LETTER N WITH TILDE
        '\xd2'     #  0xD2 -> LATIN CAPITAL LETTER O WITH GRAVE
        '\xd3'     #  0xD3 -> LATIN CAPITAL LETTER O WITH ACUTE
        '\xd4'     #  0xD4 -> LATIN CAPITAL LETTER O WITH CIRCUMFLEX
        '\xd5'     #  0xD5 -> LATIN CAPITAL LETTER O WITH TILDE
        '\xd6'     #  0xD6 -> LATIN CAPITAL LETTER O WITH DIAERESIS
        '\xd7'     #  0xD7 -> MULTIPLICATION SIGN
        '\xd8'     #  0xD8 -> LATIN CAPITAL LETTER O WITH STROKE
        '\xd9'     #  0xD9 -> LATIN CAPITAL LETTER U WITH GRAVE
        '\xda'     #  0xDA -> LATIN CAPITAL LETTER U WITH ACUTE
        '\xdb'     #  0xDB -> LATIN CAPITAL LETTER U WITH CIRCUMFLEX
        '\xdc'     #  0xDC -> LATIN CAPITAL LETTER U WITH DIAERESIS
        '\xdd'     #  0xDD -> LATIN CAPITAL LETTER Y WITH ACUTE
        '\xde'     #  0xDE -> LATIN CAPITAL LETTER THORN
        '\xdf'     #  0xDF -> LATIN SMALL LETTER SHARP S
        '\xe0'     #  0xE0 -> LATIN SMALL LETTER A WITH GRAVE
        '\xe1'     #  0xE1 -> LATIN SMALL LETTER A WITH ACUTE
        '\xe2'     #  0xE2 -> LATIN SMALL LETTER A WITH CIRCUMFLEX
        '\xe3'     #  0xE3 -> LATIN SMALL LETTER A WITH TILDE
        '\xe4'     #  0xE4 -> LATIN SMALL LETTER A WITH DIAERESIS
        '\xe5'     #  0xE5 -> LATIN SMALL LETTER A WITH RING ABOVE
        '\xe6'     #  0xE6 -> LATIN SMALL LETTER AE
        '\xe7'     #  0xE7 -> LATIN SMALL LETTER C WITH CEDILLA
        '\xe8'     #  0xE8 -> LATIN SMALL LETTER E WITH GRAVE
        '\xe9'     #  0xE9 -> LATIN SMALL LETTER E WITH ACUTE
        '\xea'     #  0xEA -> LATIN SMALL LETTER E WITH CIRCUMFLEX
        '\xeb'     #  0xEB -> LATIN SMALL LETTER E WITH DIAERESIS
        '\xec'     #  0xEC -> LATIN SMALL LETTER I WITH GRAVE
        '\xed'     #  0xED -> LATIN SMALL LETTER I WITH ACUTE
        '\xee'     #  0xEE -> LATIN SMALL LETTER I WITH CIRCUMFLEX
        '\xef'     #  0xEF -> LATIN SMALL LETTER I WITH DIAERESIS
        '\xf0'     #  0xF0 -> LATIN SMALL LETTER ETH
        '\xf1'     #  0xF1 -> LATIN SMALL LETTER N WITH TILDE
        '\xf2'     #  0xF2 -> LATIN SMALL LETTER O WITH GRAVE
        '\xf3'     #  0xF3 -> LATIN SMALL LETTER O WITH ACUTE
        '\xf4'     #  0xF4 -> LATIN SMALL LETTER O WITH CIRCUMFLEX
        '\xf5'     #  0xF5 -> LATIN SMALL LETTER O WITH TILDE
        '\xf6'     #  0xF6 -> LATIN SMALL LETTER O WITH DIAERESIS
        '\xf7'     #  0xF7 -> DIVISION SIGN
        '\xf8'     #  0xF8 -> LATIN SMALL LETTER O WITH STROKE
        '\xf9'     #  0xF9 -> LATIN SMALL LETTER U WITH GRAVE
        '\xfa'     #  0xFA -> LATIN SMALL LETTER U WITH ACUTE
        '\xfb'     #  0xFB -> LATIN SMALL LETTER U WITH CIRCUMFLEX
        '\xfc'     #  0xFC -> LATIN SMALL LETTER U WITH DIAERESIS
        '\xfd'     #  0xFD -> LATIN SMALL LETTER Y WITH ACUTE
        '\xfe'     #  0xFE -> LATIN SMALL LETTER THORN
        '\xff'     #  0xFF -> LATIN SMALL LETTER Y WITH DIAERESIS
    )
    
    
    import collections
    
    encoding_table=codecs.charmap_build(decoding_table)
    mapped_ids = collections.OrderedDict()
    del_ind = []
    amt_of_encs = 0
    for w in range(len(word_list)):
        try:
            for char in word_list[w]:
                codecs.charmap_encode(char,"strict", encoding_table)
        except UnicodeEncodeError:
            amt_of_encs += 1
            del_ind.append(w)
            print(word_list[w], w)
        mapped_ids[skip_top+3+w] = w - amt_of_encs
    
    word_list = np.delete(word_list, del_ind)
    print("----------------------------------------")
    
    dt.write1dArray(word_list, "../data/sentiment/bow/names/" + str(lowest_amt) + "-" + str(highest_amt) + "-" + classification + ".txt")
    
    all_fn = "../data/sentiment/bow/frequency/phrases/class-all-"+str(lowest_amt)+"-"+str(highest_amt)+"-" + classification
    all_fn_binary = "../data/sentiment/bow/binary/phrases/class-all-"+str(lowest_amt)+"-"+str(highest_amt)+"-" + classification
    
    tf = np.zeros(shape=(len(vectors), len(word_list)), dtype=np.int32)
    tf_binary = np.zeros(shape=(len(vectors), len(word_list)), dtype=np.int32)
    
    for ds in range(len(vectors)): # d for document sequence
        for wi in range(len(vectors[ds])): # every word id in the sequence
            if vectors[ds][wi] >= skip_top+ 3:
                new_id = mapped_ids[vectors[ds][wi]]
                print(ds, new_id)
                tf[ds][new_id] += 1
                tf_binary[ds][new_id] = 1
    print("transposing")
    tf = np.asarray(tf, dtype="int").transpose()
    tf_binary = np.asarray(tf_binary, dtype="int").transpose()
    
    tf_sparse = sp.csr_matrix(tf)
    tf_binary_sparse = sp.csr_matrix(tf_binary)
    
    sp.save_npz(all_fn_binary, tf_binary_sparse)
    sp.save_npz(all_fn, tf_sparse)
    
    print("saving")
    
    #mt.printIndividualFromAll("sentiment",  "frequency/phrases", lowest_amt, highest_amt, classification, all_fn=all_fn, names_array=word_list)
    #mt.printIndividualFromAll("sentiment",  "binary/phrases", lowest_amt, highest_amt, classification, all_fn=all_fn_binary, names_array=word_list)
    
    ppmi_fn = "../data/sentiment/bow/ppmi/class-all-"+str(lowest_amt)+"-"+str(highest_amt)+"-" + classification
    #if dt.fileExists(ppmi_fn) is False:
    
    ppmi = mt.convertPPMI( tf_sparse)
    
    ppmi_sparse = sp.csr_matrix(ppmi)
    
    sp.save_npz(ppmi_fn, ppmi_sparse)
    dt.write2dArray(ppmi, ppmi_fn)
    #mt.printIndividualFromAll("sentiment",  "ppmi", lowest_amt, highest_amt, classification, all_fn=all_fn, names_array=word_list)
    dt.write2dArray(tf_binary, all_fn_binary)
    dt.write2dArray(tf, all_fn)
    
    """

    print("1")
    classes = np.asarray(classes, dtype=np.int32)
    print(2)
    print(3)
    print(4)
    names = ["sentiment"]
    dt.write1dArray(names, "../data/sentiment/classify/sentiment/names.txt")
    dt.write1dArray(classes, "../data/sentiment/classify/sentiment/class-" + "sentiment")
    dt.write1dArray(classes,"../data/sentiment/classify/sentiment/class-all")
    dt.write1dArray(list(range(len(classes))), "../data/sentiment/classify/sentiment/available_entities.txt")
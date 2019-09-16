#!/usr/bin/python
import re
import nltk
import gensim
import requests

try:
    import fastText as fasttext
except ImportError:
    import fasttext

class LazyFastText:
    def __init__(self, lang):
        """
        We work with both the fastText library and gensim, because both provide handy utitily
        functions. Gensim has functions like most_similar(word) and similar_by_vector(vector),
        whereas fastText has a helper function for computing a vector
        for out-of-vocabulary words.

        The "en_gensimfast" option is for languages that we loaded once the slow way
        (as FastText's .vec format), and then exported to .bin format via gensim's utility
        functions. This conversion to .bin drastically improves loading times
        (from 15 minutes to 30 seconds):
        embedding_dict = gensim.models.KeyedVectors.load_word2vec_format(dictFileName, binary=False)
        embedding_dict.save_word2vec_format(dictFileName+".bin", binary=True)
        embedding_dict = gensim.models.KeyedVectors.load_word2vec_format(dictFileName+".bin", binary=True)

        Keyword arguments:
        self._lang -- language "nl" or "en" (default: "nl") or "en_gensimfast"

        Created:
        self._gmodel -- language model for lang in gensim's word2vec_format
        self._fmodel -- language model for lang in fastText format
        """

        self.lang = lang
        self._gmodel = None
        self._fmodel = None

    def get_related_words(self, word, lang="en", candidates=1000, results=10, threshold=0.6):
        """Given a word, return a list of similar words (by vector)

        Keyword arguments:
        word -- target word for which we want similar words
        lang -- language "nl" or "en" (currently unused)
        candidates -- number of similar words to look up pre-filtering
        results -- number of words to return
        threshold -- a minimum distance between vectors of word and candidate words

        Returns:
        a list of results words that
        - are a noun
        - do not contain non-alpha-characters
        - have a minumum distance to word of threshold
        in order of distance to word
        """
        # load data in fasttext object if used for the first time
        if self._gmodel == None or self._fmodel == None:
            self._load_models()

        #get related words    
        if candidates < 0 or results < 0:
            raise ValueError
        try:
            candidates = self._gmodel.similar_by_word(word, candidates)
        except KeyError:
            word_vector = self._fmodel.get_word_vector(word)
            candidates = self._gmodel.similar_by_word(word_vector, candidates)
        return [w[0] for w in candidates if not re.findall('[^A-Za-z]+', w[0]) and nltk.pos_tag(nltk.word_tokenize(w[0]))[0][1] in ["NN", "NNS"] and w[1] < threshold][:results]

    def _load_models(self):
        """Utility function for loading the fastText models into gensim and fasttext

        Loads:
        gmodel -- language model for lang in gensim's word2vec_format
        fmodel -- language model for lang in fastText format
        """
        # dutch
        NL_model_vec = "../data/fasttext/wiki.nl.vec"
        NL_model_bin = "../data/fasttext/wiki.nl.bin"
        # english
        EN_model_vec = "../data/fasttext/wiki.en.vec"
        EN_model_bin = "../data/fasttext/wiki.en.bin"
        EN_model_gensim_bin = "../data/fasttext/wiki.en.gensim.bin"

        if self.lang == "nl":
            print("Loading fastText model in gensim...")
            self._gmodel = gensim.models.KeyedVectors.load_word2vec_format(NL_model_vec, binary=False)
            print("Loading fastText model in fastText...")
            self._fmodel = fasttext.load_model(NL_model_bin)
        elif self.lang == "en":
            print("Loading fastText model in gensim...")
            self._gmodel = gensim.models.KeyedVectors.load_word2vec_format(EN_model_vec, binary=False)
            print("Loading fastText model in fastText...")
            self._fmodel = fasttext.load_model(EN_model_bin)
        elif self.lang == "en_gensimfast":
            print("Loading fastText model in gensim...")
            self._gmodel = gensim.models.KeyedVectors.load_word2vec_format(EN_model_gensim_bin, binary=True)
            print("Loading fastText model in fastText...")
            self._fmodel = fasttext.load_model(EN_model_bin)  
        else:
            pass

def get_related_words(method, word, lang, results, fasttextwrapper):
    """Given a word, return a list of similar words according to arg method.

    Keyword arguments:
    method -- "fasttext" or "conceptnet"
    word -- target word for which we want similar words
    lang -- language "nl" or "en"
    results -- number of words to return

    Returns:
    a list of related words according to arg method.
    """
    if method == "fasttext":
        if lang=="en":
            return fasttextwrapper.get_related_words(word, lang, 1000, results, 0.6)
        else:
            raise Warning("This function has not been implemented for languages other than English yet.")
            return []
    elif method == "conceptnet":
        return get_related_words_conceptnet(word, lang, results, 0.5, 1)
    else:
        raise ValueError("Please specify a method for getting related words: 'fasttext' or 'conceptnet'")

def get_related_words_conceptnet(word, lang, results, min_threshold, max_threshold):
    # do conceptnet api request for related words in specific language
    try:
        api_result = requests.get("http://api.conceptnet.io/related/c/" + lang + "/" + word + "?filter=/c/" + lang).json()
    except Error as e:
        print(e, type(e))
        return []
    # filter related words on min and max threshold
    related_words = [rw for rw in api_result['related'] if rw['weight'] > min_threshold and rw['weight'] < max_threshold]
    # post-process words from result: extract from json and remove underscores
    try:
        related_words_str = [re.sub("_"," ",rw['@id'].split("/")[3]) for rw in related_words]
    except Error as e:
        raise ValueError("something went wrong post-processing the related words:", str(related_words))
        pass
    if len(related_words_str) > results:
        return related_words_str[:results]
    else:
        return related_words_str
    
def test_expand_seedwords(lang="en"):
    """ this function is meant to demonstrate this class """
    lazyfasttext = LazyFastText("en_gensimfast") # or "en" if you haven't transformed the .vec/.bin files yet
    testwords = ["cat","demon","biscuit","malware"]
    for word in testwords:
        print(word)
        print("Conceptnet:")
        print(get_related_words("conceptnet", word, lang, 5, lazyfasttext))
        print("FastText:")
        print(get_related_words("fasttext", word, lang, 5, lazyfasttext))

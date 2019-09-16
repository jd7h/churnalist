#!/usr/bin/python
import nltk
import spacy

def parse_plaintext(filename):
    """Open a plaintext file with input text and tokenize into sentences

    Keyword arguments:
    filename -- filename of the plaintext file with input text
    """
    # get input from a plaintext file
    t = ""
    with open(filename, "r") as infile:
        t = " ".join(infile.readlines())
    sentences = nltk.sent_tokenize(t)
    return sentences

def get_noun_list(sentences, lang="nl"):
    """From a list of sentences, return a list of all nouns

    we're using the default spacy datasets for en and nl
    and the pre-trained part-of-speech-tagger

    Relevant docs of Spacy:
    https://spacy.io/usage/linguistic-features
    Use Nouns, Noun Phrases and Noun Chunks

    Todo:
    propernames
    """
    nouns = []
    parserinfo = []
    nouninfo = {}

    if lang == "nl":
        nlp = spacy.load('nl_core_news_sm')
    elif lang == "en":
        nlp = spacy.load('en_core_web_sm')
    else:
        raise ValueError('Please specify the input language (valid options: "nl", "en")')
    for sentence in sentences:
        doc = nlp(sentence)
        parserinfo.append(doc)
        for token in doc:
            #print(token.text, token.pos_, token.tag_, token.dep_)
            #if token.pos_ == "NOUN" or token.pos_ == "PROPN":
            #if token.tag_ == "NN": # ik zie altijd enkelvoud woorden, werkt niet voor NL
            if token.pos_ == "NOUN":
                #print(token.text, token.tag_)
                nouns.append(token.text)
                if token.text not in nouninfo:
                    nouninfo[token.text.lower()] = token.tag_
    return parserinfo, nouns, nouninfo

def get_noun_chunk_list(sentences, lang="en", drop_detposs="true"):
    """From a list of English sentences, return a list of noun phrases and their root nouns

    We skip pronouns and English stopwords

    Keyword arguments:
    sentences -- a list of sentences, from nltk.sent_tokenize()
    lang -- language: "en" (this function is only implemented for English)
    drop_detposs -- remove determiners and possessives (default: True)

    Returns:
    parserinfo -- list of parser-information for every sentence
    noun_chunks -- list of noun phrases from sentences
    noun_dict -- dictionary with root nouns and their related noun phrases
    """
    if lang == "en":
        nlp = spacy.load('en_core_web_sm')
    else:
        raise ValueError('Please specify the input language (valid options: "en")')
    noun_chunks = []
    parserinfo = []
    noun_dict = {}
    # remove all noun phrases that have an English stopword as their root
    stopwords = set(nltk.corpus.stopwords.words('english'))

    for s in sentences:
        doc = nlp(s)
        parserinfo.append(doc)
        for nc in doc.noun_chunks: #nc is a span
            if nc.as_doc()[0].pos_ == "PRON":
                continue # this is a pronoun, skip this nounchunk
            if nc.root.text.lower() in stopwords:
                continue
            if nc.root.text not in noun_dict:
                noun_dict[nc.root.text] = []
            if drop_detposs and nc.as_doc()[0].dep_ in ['det', 'poss']: # if we want to drop the determiners and possesives, remove these from the nc
                noun_chunks.append(nc.as_doc()[1:])
                noun_dict[nc.root.text].append(nc.as_doc()[1:])

            else:
                noun_chunks.append(nc)
                noun_dict[nc.root.text].append(nc)

    return parserinfo, noun_chunks, noun_dict

def freqdist(nouns, top_n):
    """Given a list of nouns, print the most n frequest words and return a FreqDist object

    Keyword arguments:
    nouns -- a list of words
    top_n -- print the most frequent top_n words

    Returns:
    fdist -- a nltk.FreqDist object of all words and their frequency
    """
    # preprocessing: we make everything lowercase
    # note that this might be a bad idea for proper names and jargon ("ROT13")
    nouns_lower = [n.lower() for n in nouns]
    # Calculate frequency distribution
    fdist = nltk.FreqDist(nouns_lower)
    # Output top 50 words
    for word, frequency in fdist.most_common(top_n):
        print(u'{};{}'.format(word, frequency))
    return fdist

#deprecated
def get_seed_words(filename, lang="nl"):
    """Create a list of 20 seedwords, based on a story in a plaintext file

    Keyword arguments:
    filename -- filename of the plaintext file with input text
    lang -- language "nl" or "en" (Default: "nl")

    Returns:
    parserinfo -- list of parser-information for every sentence
    nouns -- list of noun phrases from sentences
    nouninfo -- dictionary with root nouns and their related noun phrases
    fdist -- a nltk.FreqDist object of all words from the input text and their frequency
    """
    sentences = parse_plaintext(filename)
    parserinfo, nouns, nouninfo = get_noun_list(sentences, lang)
    fdist = freqdist(nouns, 20)
    return parserinfo, nouns, nouninfo, fdist

def test_keyword_extraction():
    """Test keyword extraction with a test file"""
    sentences = parse_plaintext("../data/publication_story.txt")
    get_noun_chunk_list(sentences)

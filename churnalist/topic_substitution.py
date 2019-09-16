#!/usr/bin/python
import random
import json
import nltk
import spacy
import pattern3.en, pattern3.nl

PLAINTEXT_EN = "../data/headlines.txt"

# source: https://stackoverflow.com/questions/3540288/how-do-i-read-a-random-line-from-one-file-in-python
# reads a random line from afile
def random_line(afile):
    line = next(afile)
    for num, aline in enumerate(afile, 2):
      if random.randrange(num): continue
      line = aline
    return line

def get_random_headline(lang="en"):
    """Return a random headline from the dataset

    Keyword arguments:
    method -- "database" or "plaintext"
    lang -- "nl" or "en"

    Note that we currently only have English
    plaintext headlines.
    """
    if lang == "nl":
        raise ValueError("Plaintext files not available for Dutch")
    elif lang == "en":
        with open(PLAINTEXT_EN,"r") as infile:
            return random_line(infile).strip()
    else:
        raise ValueError("Please specify a headline language ('en' or 'nl')")

def get_n_random_headlines(lang="en", n=100):
    """Return a list of n random headline from the headlines dataset

    Keyword arguments:
    lang -- "nl" or "en"
    n -- number of random headlines to return

    Note that data/ currently only contains English
    plaintext headlines.
    """
    if n <= 0:
        raise ValueError("N can't be negative")
    if n > 5000:
        raise Warning("N is high. This might clog your memory. Use this carefully.")
    results = []
    if lang == "nl":
        raise ValueError("Plaintext files not available for Dutch")
    elif lang == "en":
        with open(PLAINTEXT_EN,"r") as infile:
            lines = infile.readlines()
            for i in range(0,n):
                results.append(random.choice(lines))
            return results
    else:
        raise ValueError("Please specify a headline language ('en' or 'nl')")

def find_subj(sentence, lang):
    """Find the object or subject of the sentence

    First we try the find the subject. We look in noun chunks (english only, not implemented for Dutch)
    and then the labels from the dependency parser.
    If we cannot find a subject, we try to find an object.

    We assume that the sentence is indeed 1 sentence and it cannot be split further
    since we do not pass it through the sentence tokenizer.

    Keyword arguments:
    sentence -- string, one sentence from the array as results from nltk.sent_tokenize() function
    lang -- language, "nl" or "en"
    """
    if lang == "nl":
        nlp = spacy.load('nl_core_news_sm')
    elif lang == "en":
        nlp = spacy.load('en_core_web_sm')
    else:
        raise ValueError('Please specify your language of choice: "nl" or "en"')
    doc = nlp(sentence)
    # we try it first with noun_chunks from spacy (not available for dutch)
    for chunk in doc.noun_chunks:
        if chunk.root.dep_ == "nsubj":
            return chunk
    # if we can't find an nsubj nounchunk, we try to find a nsubj token:
    for token in doc:
        if token.dep_ == "nsubj":
            return token
    # if we can't find a subj, let's try to find an object instead:
    #for chunk in doc.noun_chunks:
    #    if chunk.root.dep_ == "dobj":
    #        return chunk
    #for token in doc:
    #    if token.dep_ == "dobj":
    #        return token
    return None

def find_obj(sentence, lang):
    """Find the object or subject of the sentence

    First we try the find the subject. We look in noun chunks (english only, not implemented for Dutch)
    and then the labels from the dependency parser.
    If we cannot find a subject, we try to find an object.

    We assume that the sentence is indeed 1 sentence and it cannot be split further
    since we do not pass it through the sentence tokenizer.

    Keyword arguments:
    sentence -- string, one sentence from the array as results from nltk.sent_tokenize() function
    lang -- language, "nl" or "en"
    """
    if lang == "nl":
        nlp = spacy.load('nl_core_news_sm')
    elif lang == "en":
        nlp = spacy.load('en_core_web_sm')
    else:
        raise ValueError('Please specify your language of choice: "nl" or "en"')
    doc = nlp(sentence)
    # let's try to find an object:
    for chunk in doc.noun_chunks:
        if chunk.root.dep_ == "dobj":
            return chunk
    for token in doc:
        if token.dep_ == "dobj":
            return token
    return None

def conjugate(token, new_word, lang):
    """Conjugate new_word so that it matches the form (plural/singular) of token

    Tokens in Dutch or English have different parser tags that we can use for conjugation.
    We get the new form from the pattern library for language lang.
    If we get an error, we return new_word unedited.

    Keyword arguments:
    token -- the source word
    new_word -- this word should get the same form as token
    lang -- language "nl" or "en"
    """
    if lang == "nl":
        if "Sing" in token.tag_:
            return  pattern3.nl.singularize(new_word)
        return pattern3.nl.pluralize(new_word)
    elif lang == "en":
        # for english, we don't have plural/singular tags
        try:
            singular_token = pattern3.en.singularize(token)
            if singular_token == token: # assumption: then token is singular
                return pattern3.en.singularize(new_word)
            return pattern3.en.pluralize(pattern3.en.singularize(new_word)) # singularize does not change a singular word, but pluralize DOES change a plural word :/
        except Exception as exc:
            print("Could not singularize or pluralize word", token, "or", new_word)
            print(type(exc), exc)
            return new_word
    else:
        raise ValueError('Please specify your language of choice: "nl" or "en"')
    return new_word

# only works with Nouns
def substitute(sentence, word, lang, target):
    """Substitute the subject or object of sentence with word

    Conjugate the substitute candidate word to the form of the substitution target.
    Replace the target with the candidate and return the new sentence.

    Keyword arguments:
    sentence -- single sentence in language lang (headline from database)
    word -- the string that should substitute the subject or object in sentence
    lang -- language "nl" or "en"
    target -- object or subject 
    """
    conjugated_word = conjugate(str(target), word, lang)
    new_sentence = sentence.replace(target.text, conjugated_word, 1)
    return new_sentence

# for making the headline a bit more pretty
def capitalize(x):
    return x[0].upper() + x[1:] if len(x) > 0 else x

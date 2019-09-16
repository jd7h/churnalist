# Flask
from flask import Flask
from flask import request
from flask import render_template
from flask import Markup
from flask import escape
# for template streaming
from flask import Response

import random
import nltk
from churnalist import keyword_extraction as ke
from churnalist import expand_seedwords as kb
from churnalist import topic_substitution as ts

BLACKLIST = ["rape","sex","war","iraq","iran","kill","gay","murder","troops","terror"]

class StaticChurnalist():
    def __init__(self, inputtext):
        self.inputtext = inputtext
        self.seedwords = []
        self.headline_stash = []
        self.blacklist = ["rape","sex","war","iraq","iran","kill","gay","murder","troops","terror"]
        self.contextwords = {}

        if inputtext == "":
            raise ValueError("The input text cannot be empty")

        print("Tokenizing and parsing...")
        sentences = nltk.sent_tokenize(inputtext)
        parserinfo, noun_chunks, noun_dict = ke.get_noun_chunk_list(sentences,"en")
        #print(noun_dict)
        #for k in noun_dict:
        #  print(k,noun_dict[k])

        useConceptNet = False

        # STEP 2: knowledge base
        print("Building knowledge base...")
        ftw = kb.LazyFastText("en_gensimfast")
        notfound = []
        kb_results = {}
        if useConceptNet:
            for word in [w.lower() for w in noun_dict.keys()]:
                if word not in kb_results:
                    print("Searching related words for",word,"in ConceptNet...")
                    try:
                        related_words = kb.get_related_words("conceptnet", word, "en", 5, ftw)
                    except Exception as e:
                        print(e,type(e))
                        continue
                    if len(related_words) == []:
                        print("Searching related words for",word,"in FastText...")
                        notfound.append(word)
                        related_words = kb.get_related_words("fasttext", word, "en", 25, ftw)
                    kb_results[word] = related_words
                else:
                    continue
            for k in kb_results:
              print(k)
              for rel_word in kb_results[k]:
                print("\t",rel_word)

        # create pool of seed words from nouns_chunks, noun_dict, kb_results
        # context words
        print("making contextwords...")
        contextwords = {}

        # add all original keywords from input
        for n in noun_dict:
            contextwords[n.lower()] = []
            contextwords[n.lower()].append(n) # add yourself, withouth lowercase
            # noun_dict[something] contains spans, not strings! use w.text instead of w
            for w in noun_dict[n]:
                if w.text not in contextwords[n.lower()]:
                    contextwords[n.lower()].append(w.text)

        self.contextwords = contextwords #save contextwords

        # generation
        print("making seedwords...")
        self.seedwords = [w for n in contextwords.keys() for w in contextwords[n]]
        #print(seedwords)
        #seedwords = ["London", "UK", "conference", "games", "COG", "computational intelligence", "researchers", "academic", "industry","creativity","technology","science","research","presentations", "scientific talk","poster presentation","demo paper","science demo"]

        print("Getting a set of random headlines from dataset")
        self.headline_stash = ts.get_n_random_headlines("en",10)

    def generate(self, n):
        if n < 0:
            raise ValueError("n for generate(n) can't be lower than 0")
        for i in range(0,n): # generate 100 headlines max
            print("Generating headlines...")
            # generate 1 Gigaword headlines
            # choose a new word, from the seed word and all related words
            new_word = random.choice(self.seedwords)
            print("Seedword: ",new_word)
            obj = None
            print("Finding substitution target...")
            while type(obj) == type(None): # as long as we have not found a substitution target
                # get random headline
                try:
                    headline = self.headline_stash.pop()
                except Exception as e:
                    self.headline_stash = ts.get_n_random_headlines("en",10)
                    headline = self.headline_stash.pop()
                obj = ts.find_obj(headline,"en")
            print(headline.strip())
            print("Changing the object of the sentence...")
            new_headline = ts.substitute(headline, new_word, "en", obj) # new_word from noun_dict is a Span, not string!
            new_new_headline = new_headline
            subj_change = random.randrange(0,10)
            if subj_change >= 9:
                print("Changing the subject of the sentence too...")
                try:
                    new_word = random.choice(self.seedwords)
                    subj = ts.find_subj(new_headline, "en")
                    new_new_headline = ts.substitute(new_headline, new_word, "en", subj).strip()
                except Exception as e:
                    #print(e)
                    pass
            print(new_new_headline)
            badwords = [badword for badword in self.blacklist if badword in new_new_headline.lower()]
            if len(badwords) > 0:
                print("Error, blacklist words", str(badwords), "found in", new_new_headline)
                continue
            yield new_new_headline

class InteractiveChurnalist():
    def __init__(self, seedwords, blacklist):
        self.seedwords = [s.strip() for s in seedwords if s.strip() != ""]
        self.blacklist = blacklist
        print("Getting a set of random headlines from dataset")
        self.headline_stash = ts.get_n_random_headlines("en",10)

    def generate(self, n):
        if n < 0:
            raise ValueError("n for generate(n) can't be lower than 0")
        for i in range(0,n): # generate 100 headlines max
            print("Generating headlines...")
            # generate 1 Gigaword headlines
            # choose a new word, from the seed word and all related words
            new_word = random.choice(self.seedwords)
            print("Seedword: ",new_word)
            obj = None
            print("Finding substitution target...")
            while type(obj) == type(None): # as long as we have not found a substitution target
                # get random headline
                try:
                    headline = self.headline_stash.pop()
                except Exception as e:
                    self.headline_stash = ts.get_n_random_headlines("en",10)
                    headline = self.headline_stash.pop()
                obj = ts.find_obj(headline,"en")
            print(headline.strip())
            print("Changing the object of the sentence...")
            new_headline = ts.substitute(headline, new_word, "en", obj) # new_word from noun_dict is a Span, not string!
            new_new_headline = new_headline
            subj_change = random.randrange(0,10)
            if subj_change >= 9:
                print("Changing the subject of the sentence too...")
                try:
                    new_word = random.choice(self.seedwords)
                    subj = ts.find_subj(new_headline, "en")
                    new_new_headline = ts.substitute(new_headline, new_word, "en", subj).strip()
                except Exception as e:
                    #print(e)
                    pass
            print(new_new_headline)
            badwords = [badword for badword in self.blacklist if badword in new_new_headline.lower()]
            if len(badwords) > 0:
                print("Error, blacklist words", str(badwords), "found in", new_new_headline)
                continue
            yield new_new_headline


def postprocess_fade(headlinegen): #gets a generator, yields a generator
    nr = 0
# make headline useable for viewing in browser 
    for headline in headlinegen:
        nr += 1
        yield Markup('<li style="display:none" class="headline">') + Markup('<span style="color:lightgrey;margin-right:3em;">') + str(nr) + Markup('</span>') + escape(headline) + Markup('</li>')

def postprocess_ticker(headlinegen): #gets a generator, yields a generator
# make headline useable for viewing in browser 
    #return Markup('<li style="display:none" class="headline">') + Markup('<span style="color:lightgrey;margin-right:3em;">') + str(nr) + Markup('</span>') + escape(headline) + Markup('</li>')
    for headline in headlinegen:
        yield escape(headline.strip())

# helper function for template streaming
# source: https://flask.palletsprojects.com/en/1.1.x/patterns/streaming/
def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(5)
    return rv

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def startpage():
    return render_template('startpage.html', title="Generator input")

@app.route('/generate', methods=['POST'])
def process_input():
    if request.method != 'POST':
        return ""
    else:
        form = request.form
        if form['generator_type'] == 'noninteractive':
            return fancy_ticker(form['inputtext'])
        elif form['generator_type'] == 'interactive':
            return interactive_step1(form['inputtext'])
        else:
            pass    

def fancy_ticker(inputtext):
    churn = StaticChurnalist(inputtext)
    return Response(stream_template('fancyticker.html', big_headlines=postprocess_ticker(churn.generate(5)), ticker_headlines=postprocess_ticker(churn.generate(5)), title="Churnalist: fake news"))

def interactive_step1(inputtext):
    churn = StaticChurnalist(inputtext)
    return render_template('seedwords.html', title="Seed word picker", contextwords = churn.contextwords)

@app.route('/generate_interactive', methods=['POST'])
def interactive_step2():
    if request.method != 'POST':
        return ""
    else:
        approved_list = request.form.getlist('human_approved')
        manual_list = [word.strip() for word in request.form['manual_seedwords'].split("\n")]
        churn = InteractiveChurnalist(approved_list + manual_list, BLACKLIST)
        return Response(stream_template('fancyticker.html', big_headlines=postprocess_ticker(churn.generate(5)), ticker_headlines=postprocess_ticker(churn.generate(5)), title="Churnalist: fake news"))

# Churnalist
This repository contains the code for Churnalist, a headline generator. Churnalist is meant as a creative writing support tool for game writers. 

## Installation (Linux)
Install all requirements in a virtual environment:
```
$ python -m venv venv             # create a virtual environment
$ source venv/bin/activate        # active the virtual environment
$ pip install -r requirements.txt # install all required packages with pip
$ python                          # start Python
>>> import nltk
>>> nltk.download('punkt')        # use nltk downloader to download 'punkt' and 'stopwords'
>>> nltk.download('stopwords')
```


### Datasets for seedword extrapolation
Churnalist uses ConceptNet and FastText to expand the list of seedwords if the input text is short. The ConceptNet API requires a working internet connection and is relatively fast. FastText requires the large (15+ Gb) FastText language models but work completely offline. Since the suggestions of ConceptNet are better than FastText's and FastText models take a long time to load, Churnalist uses FastText as a fall-back method if ConceptNet doesn't work.

If you want to use the FastText word embeddings, you need the FastText language model. Note that this model requires at least 17 Gb of free space on your hard drive! To enable the FastText functionality, download and extract the [FastText Wiki word vectors](https://fasttext.cc/docs/en/pretrained-vectors.html) for English and place them in `data/fasttext`.
```
$ wget https://dl.fbaipublicfiles.com/fasttext/vectors-wiki/wiki.en.zip # download the model
$ unzip -d data/fasttext wiki.en.zip # extract the model in data/fasttext
```

### Running the Flask demo
The folder `demo/` contains a Flask App with a non-interactive and an interactive demo of Churnalist. To run it locally, do the following after the installation steps described above:
```
$ source venv/bin/activate        # activate the virtual environment you created earlier
$ cd demo                         # go the Flask demo folder
$ export FLASK_APP=churnalist.py  # tell Flask where the app is
$ export FLASK_DEBUG=1            # if you would like debug info & auto-reload upon code changes
$ flask run                       # run the Flask app
```

## Scientific publication
Churnalist is part of the [DATA2GAME](https://www.data2game.nl) research project and based on research by Judith van Stegeren and [Mariët Theune](https://wwwhome.ewi.utwente.nl/~theune/). 

If you want to use Churnalist in a scientific context, please cite the following paper:

```
@inproceedings{van2019churnalist,
  title={Churnalist: Fictional Headline Generation for Context-appropriate Flavor Text},
  author={van Stegeren, Judith and Theune, Mari{\"e}t},
  booktitle={10th International Conference on Computational Creativity},
  pages={65--72},
  year={2019},
  organization={Association for Computational Creativity}
}
```

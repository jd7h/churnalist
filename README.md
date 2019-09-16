# Churnalist
This repository contains the code for Churnalist, a headline generator. Churnalist is meant as a creative writing support tool for game writers. 

## Installation
Download and extract the [FastText Wiki word vectors](https://fasttext.cc/docs/en/pretrained-vectors.html) for English and place them in data/fasttext.
```
$ wget https://dl.fbaipublicfiles.com/fasttext/vectors-wiki/wiki.en.zip
$ unzip -d data/fasttext wiki.en.zip
```
Install all requirements in a virtual environment:
```
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
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

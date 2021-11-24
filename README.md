# Style transfer in NLP: a framework and multilingualanalysis with Friends TV series

This is the repository of "Style transfer in NLP: a framework and multilingual analysis with Friends TV series" paper. 

Style transfer is an important and a rapidly developing of Natural Language Processing. This days more and more methods and models are proposed which allow us to generate text in predefined style. In this paper we propose a framework for style transfer of ["Friends"](https://en.wikipedia.org/wiki/Friends) TV series. The trained models are able to mimic one of 6 main characters of this famous TV-series in English and Russian.  We also present a dialogue dataset of "Friends" subtitles in English and its Russian automatic translation. In addition to that we perform a multilingual comparison of "Friends" style transfer in the two considered languages.

## Content
### bot
 
[This](https://github.com/Alenush/style_transfer_sirius2021summer/tree/master/bot) folder contains data for Telegram-bot:
- `data` - DB for storing state of each chat, rating given to each message; paths to models and log
- `models` - Folder template holding the pre-trained models
- `ui` - Utilities for enhancing UI
- `utils` - Database control, Model uploader and Rating
- `main.py` - The main file to start bot itself

### data
 
[Folder](https://github.com/Alenush/style_transfer_sirius2021summer/tree/master/data) folder contains all output datasets we have:
- `bigram_pics` - pictures of frineds without background
- `data_for_tone_analysis` - statistics of tone analysis from positive and negative words
- `generated` - phrases generated by GPT3-Large
- `questions` - quections in English and Russian for mannual assessment of generated phrases
- `scripts` - all scripts with speakers' annotation and phrases of all friends in English and Russian
- `train_data` - train data for two step finetuning of GPT3-Large models split in 9 to 1 ratio (monologues and cleaned replics) in English and Russian

### utils
 
The [folder](https://github.com/Alenush/style_transfer_sirius2021summer/tree/master/utils) folder contains all Jupiter notebooks:
- `bigrams_trigrams` - a notebook to create bigrams and trigrams for each friend
- `binary_classifier` - notebooks for Bianry Classifiers (Training + Evaluation)
- `multilabel_classifier` - a notebook for Multilabel Classifiers
- Other files:
    - `Parser.ipynb` - parses website with series' scripts
    - `Data_preparation.ipynb` - cleans parsed scripts from irrelevant symbols and words
    - `Statistics.ipynb` - gets statistics of most frequently used words and visualizes it 
    - `Phrases_Preprocessing.ipynb` - gets phrases that are common for friends and hard to detect by a classifier in English
    - `Ru_Phrases_Preprocessing.ipynb` - gets phrases that are common for friends and hard to detect by a classifier in Russian
    - `Text_Analysis.ipynb` - brief analysis of most frequently used words
    - `Metrics.ipynb` - preprocessing and furhter tone anaylis
    - 
The checkpoints of the trained models stored [here]([folder](https://github.com/Alenush/style_transfer_sirius2021summer/tree/master/utils)).

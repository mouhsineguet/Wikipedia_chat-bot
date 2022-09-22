import numpy as np
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
import requests
import re
from bs4 import BeautifulSoup
import spacy
import urllib
from urllib.error import HTTPError
import requests
from urllib.request import Request, urlopen
import html2text
from english_words import english_words_lower_set as voc
from difflib import get_close_matches

nltk.download('words')
from nltk.corpus import words

nlp=spacy.load('en_core_web_sm',disable=['prace','ner'])
## cleaning the text
stopwords = ['a', 'about', 'above', 'after', 'again', 'ain', 'all', 'am', 'an',
             'and', 'any', 'are', 'as', 'at', 'be', 'because', 'been', 'before',
             'being', 'below', 'between', 'both', 'by', 'can', 'd', 'did', 'do',
             'does', 'doing', 'down', 'during', 'each', 'few', 'for', 'from',
             'further', 'had', 'has', 'have', 'having', 'he', 'her', 'here',
             'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'if', 'in',
             'into', 'is', 'it', 'its', 'itself', 'just', 'll', 'm', 'ma',
             'me', 'more', 'most', 'my', 'myself', 'now', 'o', 'of', 'on', 'once',
             'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'own', 're',
             's', 'same', 'she', "shes", 'should', "shouldve", 'so', 'some', 'such',
             't', 'than', 'that', "thatll", 'the', 'their', 'theirs', 'them',
             'themselves', 'then', 'there', 'these', 'they', 'this', 'those',
             'through', 'to', 'too', 'under', 'until', 'up', 've', 'very', 'was',
             'we', 'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom',
             'why', 'will', 'with', 'won', 'y', 'you', "youd", "youll", "youre",
             "youve", 'your', 'yours', 'yourself', 'yourselves']

# the function to clean the text from unwanted caracters and stop words
def text_processing(sentences):
    # text Cleaning
    alpha_pattern = "[^a-zA-Z0-9]"
    sequence_pattern = r"(.)\1\1+"
    seq_replace_pattern = r"\1\1"
    processed_sentences = []
    for par in sentences:
        par = par.lower()
        # replace non-alphabets with ' '
        par = re.sub(alpha_pattern, ' ', par)
        # replace more than 3 consecutive letters by 2 letters
        par = re.sub(sequence_pattern, seq_replace_pattern, par)
        ## words proccessing
        prcd_words = []
        for word in par.split():
            if len(word) > 1 and word not in stopwords:
                prcd_words.append(word)
        clean_par = ' '.join(prcd_words)
        #word tokenizing
        doc = nlp(clean_par)
        new_par = ' '.join([token.lemma_ for token in doc])
        processed_sentences.append(new_par)
    return processed_sentences


def article_processing(text):
    # delete paraghraphs that have less than 2 phrases (less than 65 letters)
    processed_article = text_processing(text)
    return processed_article

#the mean chat-bot discusion
hello = ['hello', 'hi', 'good morning', 'good evening', 'wsp', 'hiii', 'how are you']
print('Bot: welcome to english Wikipedia english article Chat Bot \n')

while True:
    first = input('you:  ')
    for w in first.split():
        if w.lower() in hello:
            print('Bot: Happy to see you please enter your english wikipedia article ')

    while True:
        try:
            link = str(input('you: '))
            if str(link[8:20]) != 'en.wikipedia':
                raise ValueError
            req = Request(link)
            html = urlopen(req)
            soup = BeautifulSoup(html, 'html.parser')
            h = html2text.HTML2Text()
            h.ignore_links = True
            text = h.handle(str(soup.find_all('p')))
            text = list(text.split('\n\n,\n\n'))
            break
        except HTTPError:
            print('Bot: your link is incorrect \n')
        except ValueError:
            print("please try with  english wikipedia article \n")
    new_article = article_processing(text)
    while True:
        inc = True
        print("Bot: tape your question ")
        while inc:
            quest = input('you: ')
            if len(quest) < 10:
                print("Bot: Sorry, your question it is too short")
                inc = True
            else:
                for w in quest.split():
                    w = str(w).lower()

                    if w not in words.words():
                        new = get_close_matches(w, voc)
                        if len(new) == 0:
                            inc = True
                        else:
                            quest = quest.replace(w, new[0])
                print(f"Bot: Did you mean : '{quest}', if yes type Y either N ")
                res = input('you: ')
                if res == 'Y' or res == 'y':
                    inc = False
                else:
                    print("bot: rewrite it again")
                    inc = True
        question = text_processing([quest])
        target = question + new_article
        #converting the question and the article to a matrix
        vect = TfidfVectorizer(min_df=1)
        tfidf = vect.fit_transform(target)
        pairwise_similarity = (tfidf * tfidf.T).A
        arr = pairwise_similarity[0]
        lis = arr.tolist()
        lis.pop(0)
        #find the paragraph that is the max similar to the question
        idx = lis.index(max(lis))
        print('Bot: the answer for your question is : \n')
        print(text[idx])
        print('\n Bot : do you want to go for other question yes or no \n')
        ans = input('you: ')
        if ans == 'yes':
            print('Bot: tape your next question')
        else:
            break
    print('Bot: Do you wanna go for other other article yes or no \n')
    ax = input('you : ')
    if ax.lower() == 'yes':
        print('Bot: enter your next article link')
    else:
        print('Bot : thank you for choosing us \n')
        break
exit()
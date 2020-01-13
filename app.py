from flask import Flask, request, render_template, jsonify
from flask import redirect
from flask import url_for
import requests
import json

import pandas as pd
import openpyxl
#import json
#import requests
import spacy
import os
nlp = spacy.load('en_core_web_sm')
import re
from collections import Counter
#from nltk.stem.snowball import SnowballStemmer
#s_stemmer = SnowballStemmer(language='english')

import matplotlib.pyplot as plt
from wordcloud import WordCloud
from bs4 import BeautifulSoup
#import requests as req
#import MeCab
import numpy as np
from PIL import Image

import random
from datetime import datetime
import string

from Datastore.MySQL import MySQL
dns = {
    'user': 'mysql',
    'host': 'localhost',
    'password': 'keisuke',
    'database': 'kaggle'
}
db = MySQL(**dns)

app = Flask(__name__)

def random_str(n):
    return ''.join([random.choice(string.ascii_letters + string.digits) for i in range(n)])

@app.route('/')
def main():
    props = {'title': 'BIOgrabber', 'msg': 'Welcome to Index Page.'}
    html = render_template('index.html', props=props)
    return html

def search():
    renderpage = render_template("search.html")
    return renderpage

@app.route('/searchtest', methods=['GET', 'POST'])
def searchtest():
    props = {'title': 'Step-by-Step Flask - hello', 'msg': 'What you want'}
    html = render_template('searchtest.html', props=props)
    return html

@app.route('/hello')
def hello():
    props = {'title': 'Step-by-Step Flask - hello', 'msg': 'Hello World.'}
    html = render_template('hello.html', props=props)
    return html

@app.route('/users')
def users():
    props = {'title': 'Users List', 'msg': 'Users List'}
    stmt = 'SELECT * FROM users'
    users = db.query(stmt)
    html = render_template('users.html', props=props, users=users)
    return html

@app.route('/users/<int:id>')
def user(id):
    props = {'title': 'User Information', 'msg': 'User Information'}
    stmt = 'SELECT * FROM users WHERE id = ?'
    user = db.query(stmt, id, prepared=True)
    html = render_template('user.html', props=props,user=user[0])
    return html


@app.route("/result", methods=['POST'])
def result():
    item = request.form['item']
    url_f    = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term='
    url_b    = '&retmax=1&retmode=json'
    url      = url_f + item + url_b
    get_url  = requests.get(url)
    get_json = get_url.json()
    pmids = get_json['esearchresult']['idlist']
    
    responses2 = {}
    for pmid in pmids:
        URL2= 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=json&rettype=abstract&id='
        queries2= URL2 + pmid
        response2 = requests.get(queries2)
        text = response2.text
        doc = nlp(text)
        words = [token.text for token in doc
            if not token.is_stop and not token.is_punct]
        word_freq = Counter(words)
        unique_words2 = [word for (word, freq) in word_freq.items() if freq != 0]
        responses2[pmid]=unique_words2
    
    Summaries = [{'pmid':pmid, 
    'Abstract':responses2[pmid]} for pmid in pmids]

    #data  = pd.DataFrame(columns = ['PMID','Title', 'Author', 'Journal', 'Pubdate','Abstract'])
    data  = pd.DataFrame(columns = ['PMID','Abstract'])

    PMIDs = [ i['pmid'] for i in Summaries ]
        #Titles = [ i['Title'] for i in Summaries ]
        #Authors = [ i['Author'] for i in Summaries ]
        #Journals = [ i['Journal'] for i in  Summaries ]
        #Pubdates = [ i['Pubdate'] for i in Summaries ]
    Abstracts = [ i['Abstract'] for i in Summaries ]

    data['PMID'] = PMIDs
        #data['Title'] = Titles
        #data['Author'] = Authors
        #data['Journal'] = Journals
        #data['Pubdate'] = Pubdates
    data['Abstract'] = Abstracts

    Abstdata = data.Abstract.apply(' '.join)
    OneAbstdata = Abstdata.values.tolist()
    OneAbsttext =''.join(OneAbstdata)

    stop_words = ['year','of','in','the','to','doing', 'am', 'between', 'of', 'same', 'she', 'to', "don't", "they're",
                    "we've", "she'll", "we'll", 'does', "you'll", "aren't", 'are', "we're",
                    'cannot', "haven't", 'into', 'yourselves', "didn't", 'during', 'her', 'how',
                    'all', 'should', 'herself', 'by', 'against', 'own', 'further', 'be',
                    'myself', 'about', 'me', 'them', "you're", 'off', 'ought', 'under', 'has',"he's", "she's", 'itself', "i'd", 'there', 'if', "wasn't", 'those', 'our',
                    'otherwise', 'did', 'above', 'however', 'was', 'com', 'ourselves', "i've",'your', "why's", 'else', 'yourself', 'his', 'most', "when's", 'why', 'this',
                    'once', "it's", "i'm", 'ever', "shouldn't", 'an', 'while', 'whom', "you've","i'll", 'k', "they've", 'what', "he'd", "hasn't", "couldn't", 'had', 'i',
                    "you'd", 'but', 'himself', 'could', "how's", 'so', 'hers', 'we', "weren't",'the', 'they', 'yours', 'just', 'nor', 'then', 'few', "shan't", 'r', 'too',
                    "mustn't", 'would', 'can', 'ours', 'such', 'very', "won't", 'were', 'in','only', 'below', 'any', 'as', 'here', 'again', "they'll", "can't", "let's",
                    'him', 'have', 'theirs', 'it', 'you', 'which', 'been', 'on', 'over', 'more','some', "here's", 'themselves', 'where', 'is', "we'd", 'shall', 'with',
                    'like', 'being', 'my', 'since', 'that', 'until', 'who', "wouldn't",'before', 'www', 'out', 'than', 'at', 'do', 'or', 'their', "where's",
                    "they'd", 'http', 'when', "isn't", "he'll", 'from', 'for', 'other',"that's", 'its', 'get', 'both', "hadn't", 'and', 'these', 'up', "what's",
                    'no', 'through', "she'd", 'also', "doesn't", 'not', "there's", 'a', 'he','because', 'down', 'after', "who's", 'having', 'each','','BP','department','various',
                    'de','doi','conflict','sCollection','Author','Cassell','stage','jkcvhl','cell','protein','Cultivated','St','Russia','Institute','pii','ND','released','Capacity',
                    'National','expression','expressed','University','Key','Medicine','Wang','Laboratory','State','colonization','China','Xining','age','Qinghai','Animal','communities','Zhang',
                    'Science','Laboratory','s41598','abundance','significantly','lambs','genes','Italy','mediate','Basic','Bari','Organs','Medical','information','Dec','sequence','Microcirculation','heritable','control',
                    'factors','refer','changes','Epub','process','term','Ribatti','vascular','regulated','Sciences','states','Different','angiogenic','factors','print','article','makes','due',
                    'analyze','events','mechanisms','cells','processes','aim','aberrations','PMID','Innsbruck','Zoology Center','molecular','Biosciences','weight','Technikerstrasse','uibk','low',
                    'pathway','Physics','Clinical','weight','Taiwan','patients','Taipei','Hospital','anti','City','showed','College','results','treatment','landscape','Shanghai','High','promote','distant','associated','poor',
                    'USA','small','Texas','significant','showed','College','United','America','Minnesota','increased','phenotype','mice','Istanbul','Nightingale Abide','statistically','Turkey','evaluation','utility','prognostic','London','UK',
                    'survival',"1'","2'","3'","depart'","pmid'","4'",'ahead',"print'",'Liverpool','Unit','severe','case','infection','Broadgreen','Hospitals','Royal','Health','identified','Infectious','West','England','UK','Tropical','adults','Trust',
                    'Sciences','two','features','North','comparison','Johnston','Research','Sciences','Biology','Copyright','Center','review','response','Published Elsevier','Electronic','address','therapy','School','non','System','Center','Cellular','effect','disease','immune',
                    'therapies','specific','study','role','studies','based','role','important','shown','activity','patient','targeting','Division','CONCLUSION','response','efficacy','METHOD','PMCID','analysis','compared','development','novel',
                    'trial','human','METHODS','group','composition','effects','level','Technology','diseases','potential','microbioal','including','species',]

    #mask = np.array(Image.open(requests.get('http://www.clker.com/cliparts/1/5/6/8/11949847551060334388button-purple_benji_park_01.svg.med.png', stream=True).raw))

    wordcloud = WordCloud(
        stopwords = set(stop_words),
        width=1000, height=1000,
        # background_color="white",
        mode="RGB",
        #font_path="static/font-awesome/fonts/fontawesome-webfront.ttf",
        #mask=mask
        )

    wordcloud.generate(OneAbsttext)
    plt.figure(figsize=(12,12), facecolor='k')
    plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
    plt.imshow(wordcloud)
    plt.axis('off')
    save_dir = "static/img/"
    #plt.savefig(save_dir + "figure.jpg")

    dt_now = datetime.now().strftime("%Y%m%d%H%M%S") + random_str(5)
    #dt_now = datetime.now() + random_str(5)
    save_path = os.path.join(save_dir, dt_now + ".jpg")
    plt.savefig(save_path)
    props = {'title': 'Step-by-Step Flask - hello', 'msg': 'What you ask for.',
             'item': item, 'url': url, 'pmids':pmids,'save_path':save_path}

    html = render_template('result.html', props=props)
    return html

@app.errorhandler(404)
def not_found(error):
    return redirect(url_for('main'))

if __name__ == '__main__':
    #app.run(debug=True)
    port = int(os.getenv("PORT", 5000))
    #port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
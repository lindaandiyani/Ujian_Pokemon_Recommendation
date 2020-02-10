import numpy as np
import pandas as pd
import requests
from flask import Flask, abort, jsonify, render_template,url_for, request,send_from_directory,redirect
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

df = pd.read_csv('Pokemon.csv')
print(df.head(5))

def kombi(i):
    return str(i['Type 1'])+ '??' +str(i['Generation'])+'??'+str(i['Legendary'])

df['Attribute']= df.apply(kombi, axis=1)
df['Name']= df['Name'].apply(lambda i: i.lower())

ext = CountVectorizer()
extfit = ext.fit_transform(df['Attribute'])
ext.get_feature_names()

extfit = extfit.toarray()

cosScore = cosine_similarity(extfit)
cosScore

pokemon = "pikachu"
indexfav = df[df['Name'] == pokemon].index[0]
indexfav

pokemonrekomendasi = list(enumerate(cosScore[indexfav]))
pokemonrekomendasi = list(filter(lambda x: x[1] > 0.5, pokemonrekomendasi))
pokemonrekomendasi = pokemonrekomendasi[:6]

recommendedList = []
for i in pokemonrekomendasi:
    recommendedList.append(df.iloc[i[0]][:-1])

recommendation = pd.DataFrame(recommendedList)

pokemonIndex = recommendation.index
print(recommendation)

pict = []

for i in pokemonIndex:
    pict.append(f'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{i}.png')

recommendation['image'] = pict

print(recommendation)

@app.route('/cari', methods=['GET','POST'])
def Cari():
    body = request.form
    pokefav = body['Pokemon']
    pokefav = pokefav.lower()
    if pokefav not in list(df['Name']):
        return redirect('/NotFound')
    favorit = df.iloc[indexfav][["Name",'Type 1','Generation','Legendary']]
    url = 'https://pokeapi.co/api/v2/pokemon/'+ pokefav
    url = requests.get(url)
    pictRecom = url.json()["sprites"]["front_default"]
    pokeSamaSortir = sorted(pokemonrekomendasi, key= lambda x:x[1], reverse= True)
    Rekom=[]
    for item in pokeSamaSortir[:7]:
        x={}
        if item[0] != indexfav:
            nama = df.iloc[item[0]]['Name'].capitalize()
            type = df.iloc[item[0]]['Type 1']
            legend = df.iloc[item[0]]['Legendary']
            gen = df.iloc[item[0]]['Generation']
            url = 'https://pokeapi.co/api/v2/pokemon/'+ nama.lower()
            url = requests.get(url)
            pic = url.json()["sprites"]["front_default"] 
            x['Name']= nama
            x['Type']= type
            x['Legend']= legend
            x['Generation']= gen
            x["gambar"] = pic
            Rekom.append(x)
    return render_template('hasil.html',rekomen= Rekom, favorit= favorit, pic=pictRecom)

#---------------------------------------------------------------------
@app.route('/NotFound')
def notFound():
    return render_template('notfound.html')
#--------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)
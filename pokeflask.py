import numpy as np 
import pandas as pd 
import joblib
import json
import requests
from flask import Flask, abort, jsonify, render_template,url_for, request,send_from_directory,redirect
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity 

app = Flask(__name__)

df = pd.read_csv("Pokemon.csv")
def kombinasi(i):
    return str(i['Type 1'])+ '??' +str(i['Generation'])+'??'+str(i['Legendary'])
df['Atribute']= df.apply(kombinasi,axis=1)
df['Name']= df['Name'].apply(lambda i: i.lower())

cov = CountVectorizer(tokenizer=lambda df: df.split('$'))
pokeUlti = cov.fit_transform(df['Atribute'])
skorPoke = cosine_similarity(pokeUlti)
exfit = pokeUlti.toarray()

cosScore = cosine_similarity(exfit)
cosScore

pokemon = "pikachu"
indexfav = df[df['Name'] == pokemon].index[0]
indexfav

recommendasipoke = list(enumerate(cosScore[indexfav]))
recommendesipoke = list(filter(lambda x: x[1] > 0.5, recommendasipoke))
recommendasipoke = recommendasipoke[:6]

recommended = []
for i in recommendasipoke:
    recommended.append(df.iloc[i[0]][:-1])

recommendation = pd.DataFrame(recommended)

pokemonIndex = recommendation.index
print(recommendation)

gambar = []

for i in pokemonIndex:
    gambar.append(f'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{i}.png')

recommendation['image'] = gambar

print(recommendation)



@app.route('/')
def home():
    return render_template('home.html')


@app.route('/hasil', methods=['GET','POST'])
def Found():
    body = request.form
    pokefav = body['pokemon']
    pokefav = pokefav.lower()
    if pokefav not in list(df['Name']):
        return redirect('/NotFound')
    indexfav = df[df["Name"] == pokefav].index[0]
    favorit = df.iloc[indexfav][["Name",'Type 1','Generation','Legendary']]
    url = 'https://pokeapi.co/api/v2/pokemon/'+ pokefav
    url = requests.get(url)
    picReko = url.json()["sprites"]["front_default"]
    pokeRekomen = list(enumerate(skorPoke[indexfav]))
    pokeSamaSort = sorted(pokeRekomen, key= lambda x:x[1], reverse= True)
    Rekomendasi=[]
    for item in pokeSamaSort[:7]:
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
            Rekomendasi.append(x)
    return render_template('hasil.html',rekomen= Rekomendasi, favorit= favorit, pic=picReko)

@app.route('/NotFound')
def notFound():
    return render_template('notfound.html')


if __name__ == "__main__":
    app.run(debug = True, port=5000)
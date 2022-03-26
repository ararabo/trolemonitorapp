from flask import Flask, jsonify, render_template, request,url_for
from riotwatcher import LolWatcher, ApiError
from datetime import datetime,timedelta
import pandas as pd
import json
import os
import settings

API_KEY = settings.AP

SAMPLE_IMAGE_NAME='sample_image.png'
IMAGES_DIR = './static/images'
COUNT_NUM=10
DIV_CLASS='my_dataviz_'
lol_watcher = LolWatcher(API_KEY)
region = 'jp1'
app = Flask(__name__)
# 日本語を使えるように
app.config['JSON_AS_ASCII'] = False
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

def initialize_troll_list():
    troll_list=[]
    for j in range(24):
        for i in range(7):
            troll_dict={}
            if(i==0):
                tgt_weekday='Mon'
            elif(i==1):
                tgt_weekday='Tue'
            elif(i==2):
                tgt_weekday='Wed'
            elif(i==3):
                tgt_weekday='Thu'
            elif(i==4):
                tgt_weekday='Fri'
            elif(i==5):
                tgt_weekday='Sat'
            elif(i==6):
                tgt_weekday='Sun'
            value=0
            troll_dict['group']=j
            troll_dict['variable']=tgt_weekday
            troll_dict['value']=value
            troll_list.append(troll_dict)
    return troll_list

@app.route('/', methods=['POST'])
def check_troll():
    # start_time=time.time()
    sn_names=request.form.get('query')
    sn_name_lists=sn_names.split(',')
    if len(sn_name_lists)==0:
        return render_template("index.html",sStartFlag=False)
    else:
        #SNが存在するかチェック
        exist_sn_name_list=[]
        for j in range(len(sn_name_lists)):
            sn_name=sn_name_lists[j]
            try:
                summoner  = lol_watcher.summoner.by_name(region, sn_name)
                exist_sn_name_list.append(sn_name)
            except Exception:
                continue
        troll_lists=[]
        sn_name_dic={}
        for i in range(len(exist_sn_name_list)):
            sn_name=exist_sn_name_list[i]
            tgt_div_class=DIV_CLASS+str(i)
            sn_name_dic[tgt_div_class]=sn_name
            #初期リスト
            troll_list=initialize_troll_list()
            summoner  = lol_watcher.summoner.by_name(region, sn_name)
            # spect_sn=lol_watcher.spectator.by_summoner(region,summoner["id"])
            recentmatchlists = lol_watcher.match.matchlist_by_puuid("asia",summoner["puuid"],count=COUNT_NUM) #Get a list of data for the last 20 games
            dict_time_count={}
            hour_lists=[]
            weekday_lists=[]
            count_lists=[]    
            for i in range(len(recentmatchlists)):
                tgt_match_data=recentmatchlists[i]
                match_data = lol_watcher.match.by_id("asia",tgt_match_data) #Extract only one match
                game_info=match_data['info']
                game_start_time=game_info['gameStartTimestamp']
                dt=datetime.fromtimestamp(int(str(game_start_time)[:-3]))
                tgt_hour=dt.hour
                tgt_weekday=dt.weekday()
                troll_list[tgt_hour*7+tgt_weekday]["value"]=troll_list[tgt_hour*7+tgt_weekday]["value"]+1
            troll_lists.append(troll_list)
        troll_json=json.dumps(troll_lists,ensure_ascii=False)
        return render_template("index.html",sStartFlag=False,json_data=troll_json,summoner_names=sn_name_dic)
@app.route('/',methods=["GET"])
def index():
    troll_json={}
    troll_lists=[]
    return render_template("index.html",sStartFlag=True,json_data=json.dumps(troll_lists))

if __name__ == '__main__':
    app.run()

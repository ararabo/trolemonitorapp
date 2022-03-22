from flask import Flask, jsonify, render_template, request,url_for
from riotwatcher import LolWatcher, ApiError
from datetime import datetime,timedelta
import pandas as pd
import json
import os
import time

API_KEY='{API_KEY}'
lol_watcher = LolWatcher(API_KEY)
region = 'jp1'
app = Flask(__name__)
SAMPLE_IMAGE_NAME='sample_image.png'
IMAGES_DIR = './static/images'
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

@app.route('/', methods=['POST'])
def check_troll():
    start_time=time.time()
    sn_name=request.form.get('query')
    summoner  = lol_watcher.summoner.by_name(region, sn_name)
    count_num=100
    # recentmatchlists = lol_watcher.match.matchlist_by_account(region,summoner["accountId"]) #Get a list of data for the last 20 games
    recentmatchlists = lol_watcher.match.matchlist_by_puuid("asia",summoner["puuid"],count=count_num) #Get a list of data for the last 20 games
    dict_time_count={}
    hour_lists=[]
    weekday_lists=[]
    count_lists=[]
    #初期リスト
    troll_lists=[]
    lap1_time=time.time()
    print(lap1_time-start_time)
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
            troll_lists.append(troll_dict)
    lap2_time=time.time()
    print(lap2_time-lap1_time)
    for i in range(len(recentmatchlists)):
        tgt_match_data=recentmatchlists[i]
        match_data = lol_watcher.match.by_id("asia",tgt_match_data) #Extract only one match
        game_info=match_data['info']
        game_start_time=game_info['gameStartTimestamp']
        # dict_time_count[int(str(game_start_time)[:-3])]=+1
        dt=datetime.fromtimestamp(int(str(game_start_time)[:-3]))
        tgt_hour=dt.hour
        tgt_weekday=dt.weekday()
        troll_lists[tgt_hour*7+tgt_weekday]["value"]=troll_lists[tgt_hour*7+tgt_weekday]["value"]+1
    lap3_time=time.time()
    print(lap3_time-lap2_time)
    troll_json=json.dumps(troll_lists,ensure_ascii=False)
    return render_template("index.html",sStartFlag=False,json_data=troll_json)
@app.route('/',methods=["GET"])
def index():
    troll_json={}
    troll_lists=[]
    return render_template("index.html",sStartFlag=True,json_data=json.dumps(troll_lists))

if __name__ == '__main__':
    app.run()

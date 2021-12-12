import time
import sqlite3
from flask import request, redirect, url_for

from bs4 import BeautifulSoup
from selenium import webdriver


from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///teams.sqlite3'
app.config ['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

 
   


class Team(db.Model):
    __tablename__ = 'Team'
    id = db.Column(db.Integer, primary_key=True)
    team = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return 'Team was created'

class Squad(db.Model):
    __tablename__ = 'Squad'
    id = db.Column(db.Integer, primary_key=True)   
    Team_id = db.Column(db.Integer, db.ForeignKey('Team.id'))
    Team = db.relationship("Team", backref=db.backref("Team", uselist=False))

    player_name = db.Column(db.String(80))


# @app.route('/')
# def index():
#   return render_template('home.html')
  

@app.route('/', methods =["GET", "POST"])
def func1():

    if request.method == "POST":
        url = request.form.get("series_name")
    
        # url = "https://www.espncricinfo.com/series/big-bash-league-2021-22-1269637"
        # url = "https://www.espncricinfo.com/series/ipl-2021-1249214"
        url_squad = url + "/squads"

        driver = webdriver.Chrome(executable_path = 'C:\\Users\\Aditya\\Documents\\chromedriver.exe')
        driver.minimize_window()
        driver.get(url_squad) 
        
        content = driver.page_source.encode('utf-8').strip()
        soup = BeautifulSoup(content, "html.parser") 
        t_data = soup.find_all("a",{"class":"black-link d-none d-md-inline-block pl-2"})

        arr = []
        for i in t_data:
            s1 = i.getText()
            arr.append(s1[:-6])
            
        
        print(arr)
        
        db.session.query(Team).delete()
        db.session.commit()
        

        for row in arr:
            guest = Team(team = row)
            db.session.add(guest)
            db.session.commit()

        db.session.query(Squad).delete()
        db.session.commit()

        for i in range(1,len(arr)+1):
            func2(i,driver,url_squad)
        driver.close()

        x = Team.query.all()  
        return render_template('enter_team.html', context=x)
        
    return render_template('home.html')
        
        

def func2(team_id,driver,url_squad):
    
    driver.find_element_by_xpath("//*[@id='main-container']/div[1]/div/div/div[2]/div/div[1]/div[1]/div[2]/div/div/div[" + str(team_id) + "]/div[1]/a").click()
    time.sleep(1)

    content = driver.page_source.encode('utf-8').strip()
    soup = BeautifulSoup(content, "html.parser") 
       
    t_data_players = soup.find_all("a",{"class":"h3 benton-bold name black-link d-inline"})
    # print(t_data_players)
        
    arr1 = []
    for i in t_data_players:
        s1 = i.getText()
        arr1.append(s1[:-1])
            
    print(arr1)

    for row in arr1:
        guest = Squad(Team_id = team_id, player_name = row)
        db.session.add(guest)
        db.session.commit()


    # url_squad = "https://www.espncricinfo.com/series/big-bash-league-2021-22-1269637/squads"
    # url_squad = "https://www.espncricinfo.com/series/ipl-2021-1249214/squads"
    driver.get(url_squad)


@app.route('/display_teams/', methods =["GET", "POST"])
def func3():
    if request.method == "POST":

        print('func3 run horayyyyy')
        x = Squad.query.all()    
        team_id = request.form.get("team_id")
        print("team id = ",team_id)

        squad_arr = []
        for i in range(len(x)):
            if x[i].Team_id == int(team_id):
                squad_arr.append(x[i].player_name)

        y = Team.query.all()
        team_id_name = y[int(team_id)-1].team
        
        print('Squad: ')
        print(squad_arr)
        
        return render_template('display_team.html', context=squad_arr, team_name = team_id_name, title="Display Teams")


@app.route('/match_teams/', methods =["GET", "POST"])
def func4():
    if request.method == "POST":
        url = "https://www.espncricinfo.com/matches/engine/match"
        id = request.form.get("match_id")
        # id = "/1269679", "/1269648"
        url_id = url + "/" + id + ".html"

        driver = webdriver.Chrome(executable_path = 'C:\\Users\\Aditya\\Documents\\chromedriver.exe')
        driver.minimize_window()
        driver.get(url_id)
        
        content = driver.page_source.encode('utf-8').strip()
        soup = BeautifulSoup(content, "html.parser") 
        
        arr2 = []
        t_data_players2 = soup.find_all('a',{'class':'small'})
        for i in t_data_players2:
            s1=i.getText()
            arr2.append(s1[:-1])

        arr2 = arr2[: len(arr2) - 6]
        print("1st Team Players: ")
        print(arr2)

        # ----------------------
        driver.find_element_by_id("toggleSquad").click()
        

        time.sleep(2)
        arr3 = []
        t_data_players3 = soup.find_all('a',{'class':'small'})
        for i in t_data_players3:
            s1=i.getText()
            arr3.append(s1[:-1])

        arr3 = arr3[: len(arr3) - 6]
        print("2nd Team Players: ")
        print(arr3)
        
        # ----------------------
    
        return render_template('match_team.html', context=arr2, title="Display Teams")
    

if __name__ == '__main__':
    app.run(debug=True)
    

from flask import Flask,render_template,request,app,jsonify
from flask_restful import Api,Resource
import os
import pandas as pd
from scipy.optimize.optimize import main
import pymysql
import json
from sqlalchemy import sql
from sklearn.datasets import load_iris
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
app = Flask(__name__)
conn = pymysql.connect(db='heroku_78638205065f537', user='bc06134d8f3e1f', passwd='550425d9', host='us-cdbr-east-04.cleardb.com')
api=Api(app)
app.config['SECRET_KEY']='mykey'

 
with conn:
        cur=conn.cursor()
        sql="select * from weatherv4"
        df=pd.read_sql(sql, conn)
        df=df[['MinTemp','MaxTemp','Rainfall','Evaporation','Sunshine','WindGustSpeed','WindSpeed9am','WindSpeed3pm','Humidity9am','Humidity3pm','Pressure9am','Pressure3pm','Cloud9am','Cloud3pm','Temp9am','Temp3pm','RainToday','RISK_MM','RainTomorrow']]             
        df['RainTomorrow']=df['RainTomorrow'].map({'Yes':1,'No':0}).astype(int)
        df['RainToday']=df['RainToday'].map({'Yes':1,'No':0}).astype(int)
        model = MLPClassifier()
        model               
        X=df.drop('RainTomorrow',axis=1)
        y=df['RainTomorrow']   
        X_train,y_train=X,y
        print(X_train.shape,y_train.shape)
        model.fit(X_train,y_train)
        accuracy=model.score(X_train,y_train)

        
          
@app.route('/', methods=['GET','POST'])
def hello():   
        return render_template('data.html')
       
@app.route('/data',methods=['GET','POST'])
def data():
       if request.method == 'POST':               
        file = request.files['csvfile']
        if not file:            
            return render_template('data.html')
        # if not os.path.isdir('static'):
        #     os.mkdir('static')
        filepath=os.path.join('static',file.filename)
        file.save(filepath)
        print(filepath)        
        dl = pd.read_csv(filepath)
        date=dl['Date']
        dl = dl[['MinTemp','MaxTemp','Rainfall','Evaporation','Sunshine','WindGustSpeed','WindSpeed9am','WindSpeed3pm','Humidity9am','Humidity3pm','Pressure9am','Pressure3pm','Cloud9am','Cloud3pm','Temp9am','Temp3pm','RainToday','RISK_MM']]       
        dl['RainToday']=dl['RainToday'].map({'Yes':1,'No':0}).astype(int)          
        y_predict=model.predict(dl)
        print(y_predict)  
        y_hat_test=model.predict(dl)
        global dt 
        dt=pd.concat([date,dl,pd.Series(y_hat_test,name='predicted')],axis='columns')
        dt['predicted']=dt['predicted'].map({1:'ตก',0:'ไม่ตก'}).astype(object) 
        
         
        return render_template('data.html',data=dt.to_html(),accuracy=accuracy)

class Weather(Resource):    
        def get(self):
            dt['predicted']=dt['predicted'].map({'ตก':1,'ไม่ตก':0}).astype(int)
            dh=dt.to_json(orient='index')
            j=json.loads(dh)
            print(json.dumps(j,indent=4))           
            return jsonify(j)
class Weatherlive(Resource):
               
        def get(self):
            conn = pymysql.connect(db='heroku_78638205065f537', user='bc06134d8f3e1f', passwd='550425d9', host='us-cdbr-east-04.cleardb.com')
            with conn:                
                import pandas as pd                
                sql="select * from weatherv4"
                dl=pd.read_sql(sql, conn)
                date=dl['Date']
                dl = dl[['MinTemp','MaxTemp','Rainfall','Evaporation','Sunshine','WindGustSpeed','WindSpeed9am','WindSpeed3pm','Humidity9am','Humidity3pm','Pressure9am','Pressure3pm','Cloud9am','Cloud3pm','Temp9am','Temp3pm','RainToday','RISK_MM']]       
                dl['RainToday']=dl['RainToday'].map({'Yes':1,'No':0}).astype(int)         
                y_predict=model.predict(dl)
                print(y_predict)  
                y_hat_test=model.predict(dl)         
                dlive=pd.concat([date,dl,pd.Series(y_hat_test,name='predicted')],axis='columns')
                dlive['predicted']=dlive['predicted'].map({1:'ตก',0:'ไม่ตก'}).astype(object)
                print(dlive) 
                print(accuracy)
                dlive['predicted']=dlive['predicted'].map({'ตก':1,'ไม่ตก':0}).astype(int)
                dh=dlive.to_json(orient='index')
                j=json.loads(dh)
                print(json.dumps(j,indent=4))
                return jsonify(j)            


api.add_resource(Weather,"/Weather")
api.add_resource(Weatherlive,"/Weatherlive")




if __name__ == "__main__":
    app.run(debug=True)  
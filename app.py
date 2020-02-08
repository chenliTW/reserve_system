from flask import Flask,render_template,redirect,url_for,request
from datetime import datetime
import calendar
import json

app=Flask(__name__)

db={}

count={}

def backup(file,indict):
    file=open(file,"w+")
    file.write(json.dumps(indict))
    file.close()

@app.route('/reserve/flush_old/')
def flush():
    now=datetime.now().date()
    bad=[]
    for i in db:
        if db[i]["year"]<=int(now.year) and db[i]["month"]<=int(now.month) and db[i]["day"]<int(now.day):
            bad.append(i)
    for i in bad:
        count[str(db[i]["year"])][str(db[i]["month"])][str(db[i]["day"])]-=1
        del db[i]
    backup("db.txt",db)
    backup("count.txt",count)
    return redirect(url_for("index"))

@app.route('/reserve/')
def index():
    now=datetime.now().date()
    return redirect(url_for("index")+str(now.year)+"/"+str(now.month)+"/")

@app.route('/reserve/<year>/<month>/')
def dispatcher(year,month):
    year_int=int(year)
    month_int=int(month)
    cal = calendar.monthcalendar(year_int,month_int)
    if month_int==12:
        nextmonth=str(year_int+1)+"/1/"
    else:
        nextmonth=year+"/"+str(month_int+1)+"/"
    if month_int==1:
        prevmonth=str(year_int-1)+"/12/"
    else:
        prevmonth=year+"/"+str(month_int-1)+"/"
    for week in cal:
        for i in range(len(week)):
            if week[i]==0:
                week[i]=[0,0]
            else:
                try:
                    week[i]=[week[i],count[year][month][str(week[i])]]
                except:
                    week[i]=[week[i],0]
    sorteddb=sorted(db.items(), key=lambda item:(item[1]["year"],item[1]["month"],item[1]["day"],item[1]["starttime"],item[1]["place"]))
    return render_template("cal.html",year=year,month=month,cal=cal,db=sorteddb,nextmonth=nextmonth,prevmonth=prevmonth,today=datetime.now().date())

@app.route('/reserve/register/<year>/<month>/<day>/',methods=["GET","POST"])
def register(year,month,day):
    if(request.method=="GET"):
        return render_template("register.html",year=year,month=month,day=day)
    else:
        if request.form.get("name") in db:
            delete(request.form.get("name"))
        query={request.form.get("name"):{"place":request.form.get("place"),"date":year+"/"+month+"/"+day,"starttime":request.form.get("starttime"),"endtime":request.form.get("endtime"),"year":int(year),"month":int(month),"day":int(day)}}
        log.write(json.dumps(query)+"\n")
        log.flush()
        db.update(query)
        if year in count:
            if month in count[year]:
                if day in count[year][month]:
                    count[year][month][day]+=1
                else:
                    count[year][month].update({day:1})
            else:
                count[year].update({month:{day:1}})
        else:
            count.update({year:{month:{day:1}}})
        backup("db.txt",db)
        backup("count.txt",count)
        return redirect(url_for("index"))

@app.route('/reserve/delete/<name>')
def delete(name):
    count[str(db[name]["year"])][str(db[name]["month"])][str(db[name]["day"])]-=1
    del db[name]
    backup("db.txt",db)
    backup("count.txt",count)
    return redirect(url_for("index"))

if __name__=="__main__":
    calendar.setfirstweekday(calendar.SUNDAY)
    db=json.loads(open("db.txt","r").read())
    count=json.loads(open("count.txt","r").read())
    log=open("log.txt","a+")
    app.run(port=8000)
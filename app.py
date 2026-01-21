from flask import Flask,render_template,request
import sqlite3
app=Flask(__name__)
def get_db_connection():
    conn=sqlite3.connect("productivity.db")
    conn.row_factory=sqlite3.Row
    return conn
def init_db():
    conn=get_db_connection()
    c=conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS productivity_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        age INTEGER NOT NULL,
        role TEXT NOT NULL,
        sleep_hours INTEGER NOT NULL,
        work_hours INTEGER NOT NULL,
        break_hours INTEGER NOT NULL,
        screen_time INTEGER NOT NULL,
        sleep_quality TEXT,
        physical_activity TEXT,
        productivity_score INTEGER NOT NULL,
        productivity_level TEXT NOT NULL,
        issues TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );""")
    conn.commit()
    conn.close()
def analyze_productivity(age, sleep, screen, work, breaks, role, activity, quality):
    score = 100
    issues = []
    role = role.strip().lower()
    activity= activity.strip().lower()
    quality=quality.strip().lower()

    if sleep < 5:
        score -= 30
        issues.append("Very low sleep")
    elif sleep < 6:
        score -= 20
        issues.append("Low sleep")

    if screen > 8:
        score -= 25
        issues.append("Excessive screen time")
    elif screen > 6:
        score -= 15
        issues.append("High screen time")

    if activity== "no":
        score -= 15
        issues.append("Lack of physical activity")

    if role == "student":
        if work < 3:
            score -= 20
            issues.append("Insufficient study hours")
        elif work > 8:
            score -= 10
            issues.append("Overstudying")

        if breaks > 4:
            score -= 10
            issues.append("Too many breaks")

    elif role == "working professional":
        if work < 6:
            score -= 20
            issues.append("Low working hours")
        elif work > 10:
            score -= 20
            issues.append("Work overload (burnout risk)")

        if breaks < 1:
            score -= 10
            issues.append("Insufficient breaks")

    elif role == "unemployed":
        if work < 2:
            score -= 25
            issues.append("Lack of daily structure")

        if screen > 6:
            score -= 15
            issues.append("Screen dependency")

    if quality== "poor":
        score -= 15
        issues.append("Poor sleep quality")
    elif quality== "average":
        score -= 5

    if score < 0:
        score = 0

    if not issues:
        issues.append("No major issues detected")
    
    level="Low"  
    if role == "student":
        if score >= 75:
            level = "High"
        elif score >= 50:
            level = "Moderate"
        
    elif role == "working professional":
        if score >= 70:
            level = "High"
        elif score >= 45:
            level = "Moderate"
       
    elif role == "unemployed":
        if score >= 65:
            level = "High"
        elif score >= 40:
            level = "Moderate"
    return score, issues, level,age,sleep,screen
@app.route("/",methods=["GET"])
def index():
    return render_template("index.html")
@app.route("/analyze",methods=["POST"])
def analyze():
    age=int(request.form.get("age",0))
    sleep=int(request.form.get("sleep",0))
    screen=int(request.form.get("screen",0))
    work=int(request.form.get("work",0))
    breaks=int(request.form.get("breaks",0))
    activity=request.form.get("activity","")
    quality=request.form.get("quality","")
    role=request.form.get("role","")
    score,issues,level,age,sleep,screen=analyze_productivity(age,sleep,screen,work, breaks, role, activity, quality)
    conn=get_db_connection()
    c=conn.cursor()
    c.execute("""INSERT INTO productivity_data (
    age,
    role,
    sleep_hours,
    work_hours,
    break_hours,
    screen_time,
    sleep_quality,
    physical_activity,
    productivity_score,
    productivity_level,
    issues
    )
    VALUES (
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
    );""",(age,role,sleep,work,breaks,screen,quality,activity,score,level,",".join(issues)))
    conn.commit()
    conn.close()
    return render_template("index.html",score=score,level=level,issues=issues,age=age,sleep=sleep,screen=screen,work=work,breaks=breaks)
if __name__=="__main__":
    init_db()
    app.run(host='127.0.0.1',debug=True)



import os
from sqlalchemy.engine import result
from sqlalchemy.sql.functions import user
import email
from flask import Flask,render_template,request,redirect,session
from db import Base,engine,SessionLocal
import models
import PyPDF2
import docx
import json
from ai import analyze_resume


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "secret123")

Base.metadata.create_all(bind=engine)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db = SessionLocal()
    db.close() 

## HOME
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")

## ----- SIGNUP
@app.route("/signup",methods=["GET","POST"])
def signup():
    db=SessionLocal()
    
    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("password")

        exiting_user=db.query(models.User).filter_by(email=email).first()
        if exiting_user:
            return "User already Exists"

        user=models.User(email=email,password=password)
        db.add(user)
        db.commit()

        return redirect("/login")
    return render_template("/signup.html")

## -----LOGIN

@app.route("/login",methods=["GET","POST"])
def login():
    db=SessionLocal()

    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("password")

        user=db.query(models.User).filter_by(email=email,password=password).first()
        if user:
            session["user"]=user.email
            return redirect("/dashboard")
        else:
            return "Invalid Credentials"
            
    return render_template("/login.html")

## ------ DASHBOARD

@app.route("/dashboard",methods=["GET","POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")
    
    result=None
    
    if request.method=="POST":
        user_goal=request.form.get("role")
        resume_text=request.form.get("resume")
        
        file=request.files.get("file")

        ## ----------- File Handeling
        if file and file.name !="":
            if file.filename.endswith(".pdf"):
                try:
                    pdf_reader=PyPDF2.PdfReader(file)
                    text=""
                    for page in pdf_reader.pages:
                        text+=page.extract_text() or ""
                        resume_text=text
                except Exception as e:
                    result={"error":f"PDF error:{str(e)}"}
            
            elif file.filename.endswith(".docx"):
                try:
                    doc=docx.Document(file)
                    text=""
                    for para in doc.paragraphs:
                        text+=para.text +"\n"
                        resume_text=text
                except Exception as e:
                    result={"error":f"DOCX error:{str(e)}"}

        if resume_text and user_goal:  
            try:
                result=analyze_resume(resume_text,user_goal)

                ## ---------- Save to DB

                db=SessionLocal()
                user=db.query(models.User).filter_by(email=session["user"]).first()

                report=models.Reports(
                    user_id=user.id,
                    resume_text=resume_text,
                    result=json.dumps(result)
        
                )
                db.add(report)
                db.commit()
            except Exception as e:
                result={"error":f"AI Error:{str(e)}"}
            
    return render_template("/dashboard.html",user=session["user"],result=result)

## ------- HISTORY

@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/login")
    
    db=SessionLocal()
    user=db.query(models.User).filter_by(email=session["user"]).first()
    reports=db.query(models.Reports).filter_by(user_id=user.id).all()

    ## Convert JSON to Python Dict
    pasred_reports=[]
    for r in reports:
        try:
            pasred_result=json.loads(r.result)
        except:
            pasred_result={}
        pasred_reports.append({
            "resume":r.resume_text,
            "result":pasred_result
        })
    return render_template("history.html",reports=pasred_reports)

## -------- LOGOUT
@app.route("/logout")
def logout():
    session.pop("user",None)
    return redirect("/login")
                        

if __name__ == "__main__":
    app.run(debug=True)

    

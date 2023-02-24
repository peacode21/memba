import os,random,string,requests

from flask import render_template,request,session,flash,redirect,url_for

import json

from sqlalchemy.sql import text

from sqlalchemy import or_

from werkzeug.security import generate_password_hash,check_password_hash

from membapp import app,db

from membapp.models import User,Party,Comments,Topics,ContactUs,Lga,State,Donation,Payment

from membapp.forms import ContactForm



#fuction to generate random sample to use for the filename uploads

def generate_name():

    filename = random.sample(string.ascii_lowercase,10) # will always return a list

    return ''.join(filename) #join every member of the list filename together



@app.route('/load_lga/<stateid>')
def load_lga(stateid):
    #using gets method
    #state_id = request.args.get('state_id')
    lgas = db.session.query(Lga).filter(Lga.lga_stateid==stateid).all()
    data2send = '<select class="form-control border-success">'
    for s in lgas:
        data2send =data2send+"<option>"+s.lga_name +"</option>"
    data2send = data2send+ "</select>"
    
    return data2send




@app.route('/check_username',methods=['POST'])
def check_username():
    email = request.form.get('email')
    #to compare if it exists
    check = User.query.filter(User.user_email==email).first()
    if check == None:
        sendback = {'status':1,'feedback':"Email is available"}
        return json.dumps(sendback)
    else:
        sendback = {'status':0,'feedback':"Email address already registered"}
        return json.dumps(sendback)
        






#creating routes

@app.route('/')
def home():
    contact = ContactForm()
    response = requests.get("http://127.0.0.1:8000/api/v1.0/listall")
    if response:
        rspjson = json.loads(response.text)
    else:
        rspjson = {}
    return render_template('user/home.html',contact=contact,rspjson=rspjson)



@app.route('/donate',methods=["POST","GET"])
def donate():
    if session.get('user') != None:
        deets = User.query.get(session.get('user'))
    else:
        deets = None
    if request.method == "GET":
        return render_template('user/donation_form.html')
    else:
        #ref = int(random.random() * 100000000)
        amount = request.form.get('amount')
        fullname = request.form.get('fullname')
        d = Donation(don_donor=fullname,don_amt=amount,don_userid=session.get('user'))
        don_donor=session.get('user')
        db.session.add(d);db.session.commit()
        session['donation_id'] = d.don_id
        return redirect("/confirm")



@app.route('/confirm')
def confirm():
    if session.get('donation_id')!=None:
        if request.method == 'GET':
            donor = db.session.query(Donation).get(session['donation_id'])
            return render_template('user/confirm.html',donor=donor,refno=session['reference'])
            
        else:
            p = Payment(pay_donid=session.get('donation_id'),payref=session['reference'])
            db.session.add(p);db.session.commit()

            don = Donation.query.get()
            donor_name = don.don_donor
            amount = don.don_amt * 100
            headers = {"Content-Type":"application/json","Authorisation":"Bearer sk_test_6e99ed89f7b74efd81abbf924e3f613d2728fc31"}

            data={"amount":amount,"reference":session["reference"],"email":donor_name}
            response = requests.post('https://api.paystack.co/transaction/initialize ',headers=headers,data=json.dumps(data))
            rspjson=json.loads(response.text)
            if rspjson['status'] == True:
                url = rspjson['data']['authorisation_url']
                return redirect(url)
            else:
                return redirect('/confirm')
            
    else:
        return redirect('/donate')



@app.route('/paystack',methods=['GET','POST'])
def paystack():
    if refid ==None:
        return redirect('/')
    else:
        headers = {"Content-Type":"application/json","Authorisation":"Bearer sk_test_6e99ed89f7b74efd81abbf924e3f613d2728fc31"}
        verifyurl = requests.post('https://api.paystack.co/transaction/initialize ',headers=headers)
        response= requests.get(verifyurl,headers=headers)
        rspjson=json.loads(response.text)
        if rspjson['status']== True:

            return "done"
        else:
            return 'payment was not successful'


@app.route('/signup/')

def user_signup():

    data = db.session.query(Party).all()

    return render_template('user/signup.html',data=data)



@app.route("/register/", methods=['POST'])

def register():

    party=request.form.get('partyid')

    email=request.form.get('email')

    pwd=request.form.get('pwd')

    hashed_pwd=generate_password_hash(pwd)

    if party !='' and email !='' and pwd !='':

        u=User(user_fullname='',user_email=email,user_pwd=hashed_pwd,user_partyid=party)

        db.session.add(u)

        db.session.commit()

        userid=u.user_id

        session['user']=userid

        return redirect(url_for('dashboard'))

    else:

        flash("<div class='alert alert-warning'>You must complete all the fields to signup</div>")

        return redirect(url_for('user_signup'))



@app.route('/login/',methods=['POST','GET'])

def user_login():

    if request.method =='GET':

        return render_template("user/login.html")

    else:

        #retrieve the form data

        email=request.form.get('email')

        pwd=request.form.get('pwd')

        #run a query to know if the username exists on the db

        deets=db.session.query(User).filter(User.user_email==email).first()

        #compared the password coming from the form with hashed pwd in db

        if deets != None:

            pwd_indb= deets.user_pwd

        #if the pwd chech above is right,we should log them in

        #by keeping their details(user_id) in session['user']

            chk=check_password_hash(pwd_indb,pwd)

            if chk:

                id= deets.user_id

                session['user']=id

                return redirect (url_for("dashboard"))

            else:

                flash("<div class='alert alert-danger'>invalid password</div>")

                return redirect(url_for('user_login'))

        else:

            flash("<div class='alert alert-danger'>invalid password</div>")

            return redirect(url_for('user_login'))

        





    

@app.route('/dashboard/')

def dashboard():

    #protect this route so that only logged in user can gget here

    if session.get('user') != None:

        #retrieve the details of the logged in user

        id=session['user']

        deets=db.session.query(User).get(id)

        return render_template('user/dashboard.html',deets=deets)

    else:

        return redirect(url_for('user_login'))



    

@app.route("/demo/")

def demo():

    #data=db.session.query(Party).filter(Party.party_id > 1,Party.party_id < 6).all()

    #data=db.session.query(Party).get(1)

    #data=db.session.query(Party).filter(Party.party_id> 1).filter(Party.party_id <=6).all()

    #data=db.session.query(User).filter(User.user_email==email).filter(User.user_pwd==pwd).first()



    #to display the user table

#data = db.session.query(User).all()

    

    #to join the user table and party table together

    data = db.session.query(User,Party).join(Party).all()



    #selecting them directly

    data = db.session.query(User.user_fullname,Party.party_name,Party.party_contact,Party.party_shortcode).join(Party).all()

    
    #another method

    data= User.query.join(Party).add_column(Party).all()



    #to filter those that chose labour party

    data= User.query.join(Party).filter(Party.party_name=='Labour Party').add_column(Party).all()

    #to filer data which user_fullname is not equal to timi

    data= User.query.join(Party).filter(User.user_fullname !='timi').add_column(Party).all()

    
    #to filter like

   #data= User.query.filter(User.user_fullname.like('%ope%')).all()



    #to filter the incase-sensitive like

#    data= User.query.filter(User.user_fullname.ilike('%ope%')).all()

     #to filter for IN

    data= User.query.filter(User.user_fullname.in_(['timi','tolu','bakare','temitope'])).all()



        #to filter NOT IN

   # data= User.query.filter(~User.user_fullname.like('%ope%')).all()



        #to filter IS NULL\

   # data= User.query.filter(User.user_fullname==None).all()


        #to filter IS NOT NULL\

    data= User.query.filter(User.user_fullname !=None).all()


        #to filter using or_ instead |  make sure to import from sqlalchemy import or_

    data= User.query.join(Party).filter(or_(Party.party_id==1,Party.party_id==12)).add_columns(Party).all()





    #using relationship for the table(classes) that are join with forign key

    data =db.session.query(Party).filter(Party.party_id==5).first()



    data=db.session.query(User).get(12)



    return render_template("user/test.html",data=data)



@app.route('/logout/')

def user_logout():

    #pop the session and redirect to home page

    if session.get('user')!=None:

        session.pop('user',None)

    return redirect('/')









@app.route('/profile/',methods=["POST","GET"])

def profile():

    id=session.get('user')

    if id == None:

        return redirect(url_for('user_login'))

    else:

        if request.method == 'GET':
            allstates=db.session.query(State).all()
            allparties=db.session.query(Party).all()
            deets=db.session.query(User).get(id)

            return render_template ('user/profile.html',deets=deets,allstates=allstates,allparties=allparties)

        else:#form was submitted

            fullname=request.form.get('fullname')

            phone=request.form.get('phone')

            #update the db using ORM method

            userobj=db.session.query(User).get(id)

            userobj.user_fullname=fullname

            userobj.user_phone=phone

            db.session.commit()

            flash("<div class='alert alert-success'>Profile updated</div>")

            return redirect("/dashboard")











        

@app.route('/profile/picture/',methods=["POST","GET"])
def profile_picture():
    if session.get('user') == None:
        return redirect(url_for('user_login'))
    else:
        if request.method == 'GET':
            return render_template('user/profile_picture.html')
        else:
            #retrieve the file
            file=request.files['pix']
            #to know the file name
            filename= file.filename
            allowed = ['.png','.jpg','.jpeg','.JPG']
            if filename !='':
                name,ext = os.path.splitext(filename) #import os in line1
                if ext.lower() in allowed:
                    newname= generate_name()+ext
                    file.save('membapp/static/uploads/'+newname) #it will be uploaded to the upload folder
                    userpic=db.session.query(User).get(session['user'])
                    userpic.user_pix = newname
                    db.session.commit()
                    flash("<div class='alert alert-success'>File Uploaded Successfully</div>"+ file.mimetype)
                    return redirect('/dashboard')
                else:
                    return 'File type not allowed'
                #filename.endswith can also be used to select type of file that can be uploaded
                #if filename.endswith('.jpeg') or filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.JPG'):
            else:
                flash("<div class='alert alert-danger'>Please choose a file</div>")
                return redirect('/profile/picture')







@app.route('/blog/')
def blog():
    articles = db.session.query(Topics).filter(Topics.topic_status==1).all()

    return render_template('user/blog.html',articles=articles)


@app.route('/blog/<id>/')
def blog_details(id):
    #blog_deets = db.session.query(Topics).filter(Topics.topic_id==id).first()
    blog_deets = Topics.query.get_or_404(id)
    return render_template('user/blog_details.html',blog_deets=blog_deets)

    
@app.route('/newtopic',methods=["GET","POST"])
def newtopic():
    if session.get('user') !=None:
        if request.method == 'GET':
            return render_template ('user/blogform.html')
        else:
            #retrieve form data validate
            content = request.form.get('content')
            if len(content) != 0:
                content = request.form.get('content')# your textarea name = content
                #insert into database
                t=Topics(topic_title=content,topic_userid=session['user'])
                db.session.add(t)
                db.session.commit()
                if t.topic_id:
                    flash("Post successfully submitted for approval")
                else:
                    flash('Oops, something went wrong. Please try again')
            else:
                flash("You cannot submit an empty post")
            return redirect('/blog')
    else:
        return redirect (url_for('user_login'))

@app.route('/contact',methods=["POST","GET"])
def contact_us():
    contact = ContactForm()
    if request.method == 'GET':
        return render_template('user/contact.html',contact=contact)
    else:
        if contact.validate_on_submit():
            email = contact.email.data
            #pix = request.files.getlist('pix')  to add multople pictures
            upload = contact.screenshot.data
            msg =contact.message.data
            m=ContactUs(msg_content=msg,msg_email=email)
            db.session.add(m)
            db.session.commit()
            return render_template('user/test.html',upload=upload)
            flash("We have received your message and will contact you soon ")
            return redirect("contact_us")
            
        else:
            return render_template('user/contact.html',contact=contact)

@app.route('/sendcomment')
def sendcomment():
    if session.get('user'):
        usermessage = request.args.get('message')
        user = request.args.get('userid')
        topic = request.args.get('topicid')
        comment = Comments(comment_text=usermessage,comment_userid=user,comment_topicid=topic)
        db.session.add(comment)
        db.session.commit()
        commenter = comment.commentby.user_fullname
        dateposted = comment.comment_date
        sendback = f"{usermessage} <br>by {commenter} on {dateposted}"
        return sendback
    else:
        return "Your message was not posted"


@app.route("/ajaxcontact", methods=['POST'])
def contact_ajax():
    form = ContactForm()
    if form.validate_on_submit():
        email = request.form.get('email')
        msg = request.form.get('msg')
        return f"{email} and {msg}"
    else:
        return "You need to complete the form"
    
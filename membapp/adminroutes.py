from flask import render_template,redirect,flash,session,request,url_for
from sqlalchemy.sql import text#,desc
from werkzeug.security import generate_password_hash,check_password_hash
from membapp import app,db
from membapp.models import Party,Topics


@app.route('/admin/',methods=['POST','GET'])
def admin_signup():
    if request.method =='GET':        
        return render_template('admin/adminreg.html')
    else:
        username = request.form.get('username')
        pwd = request.form.get('pwd')
        '''Convert the plain password to hashed value and insert into db'''
        hashed_pwd = generate_password_hash(pwd)
        #insert into database
        if username !='' or pwd !='':
            query = f"INSERT INTO admin SET admin_username='{username}', admin_pwd='{hashed_pwd}'"
            db.session.execute (text(query))
            db.session.commit()
            flash("<div class='alert alert-success'>Registration Successful. Login here</div>")
            return redirect(url_for('admin_login'))
        else:
            flash("<div class='alert alert-danger'>Username and password is required</div>")
            return redirect(url_for(admin_signup))




@app.route('/admin/login/',methods=['POST','GET'])
def admin_login():
    if request.method =='GET':
        return render_template('admin/adminlogin.html')
    else:
        username = request.form.get('username')
        pwd = request.form.get('pwd')
        #write your query
        query = f"SELECT * FROM admin WHERE admin_username='{username}'"
        result = db.session.execute(text(query))
        total = result.fetchone()

        if total: #if the username exist
            pwd_indb = total[2] #hashed pwd frm the database
            #compare this hashed with the pwd coming from the form
            chk = check_password_hash(pwd_indb,pwd) #return True or False

            if chk == True: #login is successfull save the credential in database
                session['loggedin']=username
                return redirect(url_for('admin_dashboard'))
            
            else:
                flash("Invalid Credentials")
                return redirect(url_for('admin_login'))
        else:
            flash("Invalid Credentials")
            return redirect(url_for('admin_login'))







# def admin_login():
#     if request.method =='GET':
#         return render_template('admin/adminlogin.html')
#     else:
#         username = request.form.get('username')
#         pwd = request.form.get('pwd')
#         #write your query
#         query = f"SELECT * FROM admin WHERE admin_username='{username}' AND admin_pwd='{pwd}'"
#         result = db.session.execute(text(query))
#         total = result.fetchall()

#         if total:        #the login details are correct
#             #log him in by saving his details in session
#             session['loggedin']=username
#             return redirect(url_for('admin_dashboard'))
#         else:
#             flash("Invalid Credentials")
#             return redirect(url_for('admin_login'))


@app.route('/admin/dashboard/')
def admin_dashboard():
    if session.get('loggedin') != None:
        return render_template('admin/index.html')
    else:
        return redirect(url_for('admin_login'))

@app.route('/admin/topics')
def all_topics():
    if session.get('loggedin') == None:
        return redirect(url_for('admin_login'))
    else:
        topics =Topics.query.all()
        return render_template("admin/alltopics.html",topics=topics)


@app.route('/admin/update_topic', methods=['POST'])
def update_topic():
    if session.get('loggedin') == None:
        return redirect(url_for('admin_login'))
    else:
        newstatus = request.form.get('status')
        topicid = request.form.get('topicid')
        t = Topics.query.get(topicid)
        t.topic_status=newstatus
        db.session.commit()
        flash('Topic successfully updated!')
        return redirect('/admin/topics')

@app.route('/admin/topics/edit/<id>')
def edit_topic(id):
    #TO DO ensure that this route is protected
    if session.get('loggedin') == None:
        return redirect(url_for('admin_login'))
    else:
        topic_deets = Topics.query.get(id)
        return render_template('admin/edit_topic.html',topic_deets=topic_deets)


@app.route('/admin/topic/delete/<id>')
def delete_post(id):
    if session.get('loggedin') == None:
        return redirect(url_for('admin_login'))
    else:
        topicobj = Topics.query.get_or_404(id)
        db.session.delete(topicobj)
        db.session.commit()
        flash("Successfully Deleted!")
        return redirect(url_for('all_topics'))



@app.route('/admin/logout/')
def admin_logout():
    if session.get('loggedin') != None:
        session.pop('loggedin',None)
    return redirect(url_for('admin_login'))



@app.route('/admin/party/', methods=['POST','GET'])
def admin_party():
    if session.get('loggedin') == None:
        return redirect(url_for('admin_login'))
    else:
        if request.method =='GET':
            return render_template('admin/adminparty.html')
        else:
            partyname = request.form.get('partyname')
            code = request.form.get('code')
            contact = request.form.get('contact')
            #step1: create an instance of Party (ensure that Party is imported from models) obj = Classname(column1=value,column2=value)
            p=Party(party_name=partyname, party_shortcode=code, party_contact=contact)
            #step2: add to session
            db.session.add(p)
            #step3: commit session
            db.session.commit()
            flash('Party Added Successfully')
            return redirect(url_for('parties'))


@app.route('/admin/parties/')
def parties():
    if session.get('loggedin') != None:
        #we will fetch from db using ORM method
        #data = db.session.query(Party).order_by(desc(Party.party_name)).all()

        data = db.session.query(Party).order_by(Party.party_name.desc()).all()
        return render_template('admin/all_parties.html',data=data)
    else:
        return redirect('/admin/login')
    


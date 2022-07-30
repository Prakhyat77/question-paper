from flask import Flask,render_template,url_for,redirect,request,flash,jsonify,session,make_response
import mysql.connector
import os
import pdfkit

app=Flask(__name__)
conn=mysql.connector.connect(host='localhost',user='root',password='',database='question')
cursor=conn.cursor()
app.secret_key = os.urandom(24)

@app.route('/',methods=['GET','POST'])
def login():
    if 'id' not in session:
        return render_template("login.html")
    else:
        return redirect('/index')

@app.route('/login_validation',methods=['POST'])
def login_validation():
    username=request.form.get('username')
    password=request.form.get('password')
    cursor.execute('''SELECT * FROM `login` WHERE `username` LIKE '{}' AND `password` LIKE '{}' '''.format(username,password))
    login_info=cursor.fetchall()
    if len(login_info)>0:
        session['id']=login_info[0][0]
        return render_template('dashboard.html')
    else:
        return render_template('login.html')    

@app.route('/logout')
def logout():
    session.pop('id')
    return redirect('/')

@app.route('/index')
def index():
    if 'id' in session:
        return render_template('dashboard.html')
    else:
        return redirect('/')

# start branch

@app.route('/branch')
def branch():
    if 'id' in session:
        cursor.execute('''SELECT * FROM `branch`''')
        branch_info=cursor.fetchall()
        return render_template('branch.html',branch_info=branch_info)
    else:
        return redirect('/')

@app.route('/add_branch',methods=['GET','POST'])
def add_branch():
    if 'id' in session:
        if request.method== 'POST':
            branch_name=request.form.get('b_name')
            semester=request.form.get('semester')
            status=request.form.get('b_status')
            cursor.execute('''SELECT * FROM `branch` WHERE `branch_name`='{}' AND `semester`='{}' '''.format(branch_name,semester))
            branch=cursor.fetchall()
            if len(branch)==0:
                cursor.execute('''INSERT INTO `branch`(`branch_name`,`semester`,`status`) VALUES ('{}','{}','{}')'''.format(branch_name,semester,status))
                conn.commit()
                return redirect('/branch')
            else:
                return render_template('add_branch.html',same=True)
        else:
            return render_template('add_branch.html')
    else:
        return redirect('/')

@app.route('/branch/edit/<string:b_id>',methods=['POST','GET'])
def edit_branch(b_id):
    if 'id' in session:
        if request.method=='POST':
            branch_name=request.form.get('b_name')
            semester=request.form.get('semester')
            status=request.form.get('b_status')
            cursor.execute('''UPDATE `branch` SET `branch_name`='{}' , `semester`='{}', `status`='{}' WHERE `b_id`='{}' '''.format(branch_name,semester,status,b_id))
            conn.commit()
            return redirect('/branch')
        else:
            cursor.execute('''SELECT * FROM `branch` WHERE `b_id` LIKE '{}' '''.format(b_id))
            edit_info=cursor.fetchall()
            return render_template('edit_branch.html',edit_infos=edit_info)
    else:
        return redirect('/')


@app.route('/branch/delete/<string:b_id>',methods=['GET'])
def delete_branch(b_id):
    if 'id' in session:
        cursor.execute('''SELECT * FROM `subject` WHERE `b_id`='{}' '''.format(b_id))
        delete_notice=cursor.fetchall()
        cursor.execute('''SELECT * FROM `branch`''')
        branch_info=cursor.fetchall()
        if len(delete_notice)>0:
            return render_template('branch.html',branch_info=branch_info,notice=True)
        else:
            cursor.execute('''DELETE FROM `branch` WHERE `b_id`='{}' '''.format(b_id))
            conn.commit()
            return redirect('/branch')
    else:
        return redirect('/')

# end branch

# start subject

@app.route('/subject')
def subject():
    if 'id' in session:
        cursor.execute('''SELECT * FROM `subject`''')
        subject_info=cursor.fetchall()
        return render_template('subject.html',subject_info=subject_info)
    else:
        return redirect('/')

@app.route('/add_subject',methods=['GET','POST'])
def add_subject():
    if 'id' in session:
        if request.method== 'POST':
            s_code=request.form.get('s_code')
            subject_name=request.form.get('subject_name')
            s_branch_name=request.form.get('s_branch_name')
            semester=request.form.get('semester')
            s_status=request.form.get('s_status')
            cursor.execute('''SELECT * FROM `branch` WHERE `branch_name`='{}' AND `semester`='{}' '''.format(s_branch_name,semester))
            subject=cursor.fetchall()
            if len(subject)>0:
                cursor.execute('''INSERT INTO `subject`(`s_code`,`subject_name`,`s_branch_name`,`semester`,`s_status`,`b_id`) VALUES ('{}','{}','{}','{}','{}','{}')'''.format(s_code,subject_name,s_branch_name,semester,s_status,subject[0][0]))
                conn.commit()
                return redirect('/subject')
            else:
                cursor.execute('''SELECT distinct `branch_name` FROM `branch` ORDER BY `branch_name` ASC''')
                branch_name=cursor.fetchall()
                cursor.execute('''SELECT distinct `semester` FROM `branch` ORDER BY `semester` ASC''')
                branch_semester=cursor.fetchall()
                return render_template('add_subject.html',notice=True,branch_name=branch_name,branch_semester=branch_semester)
        else:
            cursor.execute('''SELECT distinct `branch_name` FROM `branch` ORDER BY `branch_name` ASC''')
            branch_name=cursor.fetchall()
            cursor.execute('''SELECT distinct `semester` FROM `branch` ORDER BY `semester` ASC''')
            branch_semester=cursor.fetchall()
            return render_template('add_subject.html',branch_name=branch_name,branch_semester=branch_semester)
    else:
        return redirect('/')

@app.route('/subject/edit/<string:s_id>',methods=['POST','GET'])
def edit_subject(s_id):
    if 'id' in session:
        if request.method=='POST':
            s_code=request.form.get('s_code')
            subject_name=request.form.get('subject_name')
            s_branch_name=request.form.get('s_branch_name')
            semester=request.form.get('semester')
            s_status=request.form.get('s_status')
            cursor.execute('''UPDATE `subject` SET `subject_name`='{}' , `semester`='{}', `s_status`='{}',`s_code`='{}', `s_branch_name`='{}' WHERE `s_id`='{}' '''.format(subject_name,semester,s_status,s_code,s_branch_name,s_id))
            conn.commit()
            return redirect('/subject')
        else:
            cursor.execute('''SELECT * FROM `subject` WHERE `s_id` LIKE '{}' '''.format(s_id))
            edit_info=cursor.fetchall()
            cursor.execute('''SELECT * FROM `branch` ''')
            datas = cursor.fetchall()
            return render_template('edit_subject.html',edit_infos=edit_info,datas=datas)
    else:
        return redirect('/')

@app.route('/firstajax',methods=['POST','GET'])
def firstajaxsub():
    if 'id' in session:
        if request.method == 'POST':
            category_id = request.form['category_id']
            print(category_id)
            cursor.execute('''SELECT * FROM `branch` WHERE `branch_name`='{}' '''.format(category_id))
            semester = cursor.fetchall()
            print(semester)
            OutputArray = []
            for row in semester:               
                outputObj = {
                    'id':row[0],
                    'semester':row[2]
                }
                OutputArray.append(outputObj)
            return jsonify(OutputArray)
    else:
        return redirect('/')

@app.route('/subject/delete/<string:s_id>',methods=['GET'])
def delete_subject(s_id):
    if 'id' in session:
        cursor.execute('''DELETE FROM `subject` WHERE `s_id`='{}' '''.format(s_id))
        conn.commit()
        return redirect('/subject')
    else:
        return redirect('/')

# end subject

# start unit

@app.route('/unit')
def unit():
    if 'id' in session:
        cursor.execute('''SELECT * FROM `unit`''')
        unit_info=cursor.fetchall()
        return render_template('unit.html',unit_info=unit_info)
    else:
        return redirect('/')

@app.route('/add_unit',methods=['GET','POST'])
def add_unit():
    if 'id' in session:
        if request.method== 'POST':
            unit_number=request.form.get('unit_number')
            unit_name=request.form.get('unit_name')
            u_branch_name=request.form.get('u_branch_name')
            u_subject_name=request.form.get('u_subject_name')
            u_semester=request.form.get('u_semester')
            u_status=request.form.get('u_status')
            u_s_code=request.form.get('u_s_code')
            cursor.execute('''SELECT * FROM `subject` WHERE `subject_name`='{}' AND `semester`='{}' AND `s_code`='{}' '''.format(u_subject_name,u_semester,u_s_code))
            unit=cursor.fetchall()
            if len(unit)>0:
                cursor.execute('''INSERT INTO `unit`(`unit_number`,`unit_name`,`u_branch_name`,`u_subject_name`,`u_semester`,`u_status`,`s_id`,`u_s_code`) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}')'''.format(unit_number,unit_name,u_branch_name,u_subject_name,u_semester,u_status,unit[0][0],u_s_code))
                conn.commit()
                return redirect('/unit')
            else:
                cursor.execute('''SELECT distinct `s_branch_name` FROM `subject` ORDER BY `s_branch_name` ASC ''')
                branch_name=cursor.fetchall()
                cursor.execute('''SELECT distinct `subject_name`,`s_code` FROM `subject` ORDER BY `s_code` ASC ''')
                subject_name_code=cursor.fetchall()
                cursor.execute('''SELECT distinct `semester` FROM `subject` ORDER BY `semester` ASC ''')
                subject_semester=cursor.fetchall()
                return render_template('add_unit.html',notice=True,branch_name=branch_name,subject_name_code=subject_name_code,subject_semester=subject_semester)
        else:
            cursor.execute('''SELECT distinct `s_branch_name` FROM `subject` ORDER BY `s_branch_name` ASC ''')
            branch_name=cursor.fetchall()
            cursor.execute('''SELECT distinct `subject_name`,`s_code` FROM `subject` ORDER BY `s_code` ASC ''')
            subject_name_code=cursor.fetchall()
            cursor.execute('''SELECT distinct `semester` FROM `subject` ORDER BY `semester` ASC ''')
            subject_semester=cursor.fetchall()
            return render_template('add_unit.html',branch_name=branch_name,subject_name_code=subject_name_code,subject_semester=subject_semester)
    else:
        return redirect('/')

@app.route('/firstajaxunit',methods=['POST','GET'])
def firstajaxunit():
    if 'id' in session:
        if request.method == 'POST':
            u_branch_name = request.form['u_branch_name']
            print(u_branch_name)
            cursor.execute('''SELECT distinct`semester`  FROM `subject` WHERE `s_branch_name`='{}' '''.format(u_branch_name))
            semester = cursor.fetchall()
            print(semester)
            OutputArray = []
            for row in semester:               
                outputObj = {
                    'semester':row[0]
                }
                OutputArray.append(outputObj)
            return jsonify(OutputArray)
    else:
        return redirect('/')

@app.route('/secondajaxunit',methods=['POST','GET'])
def secondajaxunit():
    if 'id' in session:
        if request.method == 'POST':
            u_branch_name = request.form['u_branch_name']
            u_semester_name = request.form['u_semester_name']
            cursor.execute('''SELECT distinct`subject_name`  FROM `subject` WHERE `s_branch_name`='{}' ,`semester`='{}' '''.format(u_branch_name,u_semester_name))
            subject_name = cursor.fetchall()
            print(subject_name)
            OutputArray = []
            for row in subject_name:               
                outputObj = {
                    'subject_name':row[0]
                }
                OutputArray.append(outputObj)
            return jsonify(OutputArray)
    else:
        return redirect('/')

@app.route('/unit/delete/<string:u_id>',methods=['GET'])
def delete_unit(u_id):
    if 'id' in session:
        cursor.execute('''DELETE FROM `unit` WHERE `u_id`='{}' '''.format(u_id))
        conn.commit()
        return redirect('/unit')
    else:
        return redirect('/')


# end unit

# start question

@app.route('/question')
def question():
    if 'id' in session:
        cursor.execute('''SELECT * FROM `question`''')
        question_info=cursor.fetchall()
        return render_template('question.html',question_info=question_info)
    else:
        return redirect('/')

@app.route('/add_question',methods=['GET','POST'])
def add_question():
    if 'id' in session:
        if request.method== 'POST':
            q_question=request.form.get('q_question')
            q_marks=request.form.get('q_marks')
            q_unit_name=request.form.get('q_unit_name')
            q_s_name=request.form.get('q_s_name')
            q_b_name=request.form.get('q_b_name')
            q_semester=request.form.get('q_semester')
            q_status=request.form.get('q_status')
            cursor.execute('''SELECT * FROM `unit` WHERE `unit_name`='{}' AND `u_semester` IN (SELECT `u_semester` FROM `unit` WHERE `u_subject_name`='{}') '''.format(q_unit_name,q_s_name))
            question=cursor.fetchall()
            if len(question)>0:
                cursor.execute('''INSERT INTO `question` (`q_question`,`q_marks`,`q_unit_name`,`q_s_code`,`q_s_name`,`q_b_name`,`q_semester`,`q_status`,`q_date_of_reg`,`u_id`) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}',current_timestamp(),'{}')'''.format(q_question,q_marks,q_unit_name,question[0][8],q_s_name,q_b_name,q_semester,q_status,question[0][0]))
                conn.commit()
                return redirect('/question')
            else:
                cursor.execute('''SELECT distinct `u_branch_name` FROM `unit` ORDER BY `u_branch_name` ASC ''')
                branch_name=cursor.fetchall()
                cursor.execute('''SELECT distinct `u_subject_name`,`u_s_code` FROM `unit` ORDER BY `u_s_code` ASC ''')
                subject_name_code=cursor.fetchall()
                cursor.execute('''SELECT distinct `u_semester` FROM `unit` ORDER BY `u_semester` ASC ''')
                u_semester=cursor.fetchall()
                cursor.execute('''SELECT distinct `unit_name` FROM `unit` ORDER BY `unit_name` ASC ''')
                unit_name=cursor.fetchall()
                return render_template('add_question.html',notice=True,branch_name=branch_name,subject_name_code=subject_name_code,u_semester=u_semester,unit_name=unit_name)
        else:
            cursor.execute('''SELECT distinct `u_branch_name` FROM `unit` ORDER BY `u_branch_name` ASC ''')
            branch_name=cursor.fetchall()
            cursor.execute('''SELECT distinct `u_subject_name`,`u_s_code` FROM `unit` ORDER BY `u_s_code` ASC ''')
            subject_name_code=cursor.fetchall()
            cursor.execute('''SELECT distinct `u_semester` FROM `unit` ORDER BY `u_semester` ASC ''')
            u_semester=cursor.fetchall()
            cursor.execute('''SELECT distinct `unit_name` FROM `unit` ORDER BY `unit_name` ASC ''')
            unit_name=cursor.fetchall()
            return render_template('add_question.html',branch_name=branch_name,subject_name_code=subject_name_code,u_semester=u_semester,unit_name=unit_name)
    else:
        return redirect('/')

@app.route('/question/delete/<string:q_id>',methods=['GET'])
def delete_question(q_id):
    if 'id' in session:
        cursor.execute('''DELETE FROM `question` WHERE `q_id`='{}' '''.format(q_id))
        conn.commit()
        return redirect('/question')
    else:
        return redirect('/')


# end question

# start paper

@app.route('/paper')
def paper():
    if 'id' in session:
        cursor.execute('''SELECT * FROM `paper`''')
        paper_info=cursor.fetchall()
        return render_template('paper.html',paper_info=paper_info)
    else:
        return redirect('/')

@app.route('/add_main_paper',methods=['GET','POST'])
def add_main_paper():
    if 'id' in session:
        if request.method== 'POST':
            p_b_name=request.form.get('p_b_name')
            p_s_name=request.form.get('p_s_name')
            p_semester=request.form.get('p_semester')
            paper_name=request.form.get('paper_name')
            p_note=request.form.get('p_note')
            p_time_all=request.form.get('p_time_all')
            p_status=request.form.get('p_status')
            cursor.execute('''SELECT * FROM `question` WHERE `q_semester`='{}' AND `q_b_name`='{}' AND `q_s_name`='{}' '''.format(p_semester,p_b_name,p_s_name))
            paper=cursor.fetchall()
            if len(paper)>0:
                cursor.execute('''INSERT INTO `paper` (`p_b_name`,`p_s_name`,`p_semester`,`paper_name`,`p_note`,`p_time_all`,`p_status`,`q_id`,`p_s_code`) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}')'''.format(p_b_name,p_s_name,p_semester,paper_name,p_note,p_time_all,p_status,paper[0][0],paper[0][4]))
                conn.commit()
                return redirect('/paper')
            else:
                cursor.execute('''SELECT distinct `q_b_name` FROM `question` ORDER BY `q_b_name` ASC ''')
                branch_name=cursor.fetchall()
                cursor.execute('''SELECT distinct `q_s_name` FROM `question` ORDER BY `q_s_name` ASC ''')
                subject_name_code=cursor.fetchall()
                cursor.execute('''SELECT distinct `q_semester` FROM `question` ORDER BY `q_semester` ASC ''')
                u_semester=cursor.fetchall()
                return render_template('add_main_paper.html',notice=True,branch_name=branch_name,subject_name_code=subject_name_code,u_semester=u_semester)
        else:
            cursor.execute('''SELECT distinct `q_b_name` FROM `question` ORDER BY `q_b_name` ASC ''')
            branch_name=cursor.fetchall()
            cursor.execute('''SELECT distinct `q_s_name` FROM `question` ORDER BY `q_s_name` ASC ''')
            subject_name_code=cursor.fetchall()
            cursor.execute('''SELECT distinct `q_semester` FROM `question` ORDER BY `q_semester` ASC ''')
            u_semester=cursor.fetchall()
            return render_template('add_main_paper.html',branch_name=branch_name,subject_name_code=subject_name_code,u_semester=u_semester)
    else:
        return redirect('/')

@app.route('/generate_paper',methods=['POST','GET'])
def generate_paper():
    if 'id' in session:
        if request.method=='POST':
            question_id=request.form.getlist('question_id[]')
            p_id=request.form.getlist('p_id[]')
            for q_table_id in question_id:
                cursor.execute('''SELECT * FROM `question` WHERE `q_id`='{}' '''.format(q_table_id))
                question_paper=cursor.fetchall()
                cursor.execute('''INSERT INTO `question_paper` (`p_id`,`p_question`,`p_marks`,`p_unit_name`) VALUES ('{}','{}','{}','{}')'''.format(p_id[0],question_paper[0][1],question_paper[0][2],question_paper[0][3]))
                conn.commit()
            return redirect('/paper')
    else:
        return redirect('/')

@app.route('/paper/edit/<string:p_id>',methods=['POST','GET'])
def add_paper(p_id):
    if 'id' in session:
        cursor.execute('''SELECT * FROM `paper` WHERE `p_id`='{}' '''.format(p_id))
        paper_edit_info=cursor.fetchall()
        cursor.execute('''SELECT * FROM `question` WHERE `q_s_code`='{}' '''.format(paper_edit_info[0][4]))
        paper=cursor.fetchall()
        cursor.execute('''SELECT distinct `q_unit_name` FROM `question` WHERE `q_s_code`='{}' '''.format(paper_edit_info[0][4]))
        paper_unit_name=cursor.fetchall()
        return render_template('add_paper.html',paper=paper,paper_unit_name=paper_unit_name,paper_edit_info=paper_edit_info)
    else:
        return redirect('/')


@app.route('/paper/generate/<string:p_id>',methods=['POST','GET'])
def generate_paper_pdf(p_id):
    if 'id' in session:
        cursor.execute('''SELECT * FROM `question_paper` WHERE `p_id`='{}' '''.format(p_id))
        question=cursor.fetchall()
        cursor.execute('''SELECT sum(`p_marks`),count(p_q_id) FROM `question_paper` WHERE `p_id`='{}' '''.format(p_id))
        sum_count=cursor.fetchall()
        cursor.execute('''SELECT * FROM `paper` WHERE `p_id`='{}' '''.format(p_id))
        paper=cursor.fetchall()
        return render_template('generate_paper.html',question=question,sum_count=sum_count,paper=paper)
    else:
        return redirect('/')

@app.route('/paper/delete/<string:p_id>',methods=['GET'])
def delete_paper(p_id):
    if 'id' in session:
        cursor.execute('''DELETE FROM `question_paper` WHERE `p_id`='{}' '''.format(p_id))
        conn.commit()
        cursor.execute('''DELETE FROM `paper` WHERE `p_id`='{}' '''.format(p_id))
        conn.commit()
        return redirect('/paper')
    else:
        return redirect('/')

# end paper


if __name__=='__main__':
    app.run(host="localhost", port=8000, debug=True)
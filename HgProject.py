from flask import Flask, jsonify,request, json
import base64
from io import BytesIO
import image
import pymysql as mysql
import smtplib
from email.mime.text import MIMEText
import string
import random

app = Flask(__name__) 
@app.route('/signup',methods=['POST','GET']) 
def signup(): 
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()
    
    if request.method == 'POST':
        u_id = request.values['u_id']
        u_passwd = request.values['u_passwd']
        u_name = request.values['u_name']
        u_email = request.values['u_email']   
        sql ="insert into user values('"+str(u_id)+"','"+str(u_passwd)+"','"+str(u_name)+"','"+str(u_email)+"',1,True)"
        result = cur.execute(sql)
        con.commit()
        con.close()
        if result == 1:
            return "Success"
        else:
            return "Failed"
    else:
        return "Error"

@app.route('/signin',methods = ['POST','GET'])
def signin():
      con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
      cur = con.cursor()
    
      if request.method == 'POST':
            u_id = request.values['u_id']
            u_passwd = request.values['u_passwd']
 
            sql ="select * from user where u_id ='"+str(u_id)+"' and u_passwd ='"+str(u_passwd)+"'"
            result = cur.execute(sql)
            con.close()
            if result == 1:
                return "Success"
            else:
                return "Failed"
      else:
            return "Error"

@app.route('/getuser',methods = ['POST','GET'])
def getuser():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        u_id = request.values['u_id']
        sql = "select * from user where u_id ='"+str(u_id)+"'"
        result = cur.execute(sql)
        userinfo = cur.fetchall()
        userdata = {"u_id" : userinfo[0][0], "u_name":userinfo[0][2], "u_email" : userinfo[0][3],"u_permission" : userinfo[0][4], "push" : userinfo[0][5],"u_photo" :userinfo[0][6]}
        cur.execute("select team.t_num, team.t_name, team.t_logo, team.t_info,team.t_facebook,team.t_youtube from team where t_num = (select t_num from bookmark where u_id = '"+str(u_id)+"')")
        bookmarkdata = cur.fetchall()
        bookmarklist = []
        for data in bookmarkdata:
            teamdata = {"t_num":data[0], "t_name":data[1],"t_logo":data[2], "t_info":data[3], "t_facebook":data[4],"t_youtube":data[5]}
            bookmarklist.append(teamdata)
        if userinfo[0][4]==2:
            cur.execute("select team.t_name, team.t_logo, team.t_info,team.t_facebook,team.t_youtube, team.t_num from team where t_num = (select t_num from team_user where u_id='"+str(u_id)+"')")
            teaminfo = cur.fetchall()
            teamdata = {"t_name":teaminfo[0][0],"t_logo":teaminfo[0][1], "t_info":teaminfo[0][2], "t_facebook":teaminfo[0][3],"t_youtube":teaminfo[0][4], "t_num":teaminfo[0][5]}

            return jsonify(user = userdata, team = teamdata, bookmark = bookmarklist)
        else:
        
            return jsonify(user = userdata, bookmark = bookmarklist)

    else:
        return jsonify(result="Error")

@app.route('/registnotice', methods = ['POST','GET'])
def registernotice():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        jsondata = request.values['notice']
        data = json.loads(jsondata)
        #print(data)
        
        title = data['title']
        content = data['content']
        type = data['type']
        sql = "insert into notice values(null,'"+str(title)+"','"+str(content)+"','"+str(type)+"',null)"
        result = cur.execute(sql)
        if result ==1:
            photourl = "D:/Program Files (x86)/Apache Software Foundation/Apache2.2/htdocs/noticeImg/"
            cur.execute("select n_num from notice where n_title = '"+str(title)+"'")
            number = cur.fetchone()
            jsonphotoarr = data['photo']
            i=0
            for photo in jsonphotoarr:
                filename = str(photourl)+str(number[0])+"_"+str(photo['index'])+".jpg" 
                in_db_filename = "/noticeImg/"+str(number[0])+"_"+str(photo['index'])+".jpg" 
                with open(str(filename), "wb") as img:
                    img.write(base64.b64decode(photo['photo']))      
                    cur.execute("insert into notice_photo values('"+str(number[0])+"','"+str(photo['index'])+"','"+str(in_db_filename)+"')")
                i = i+1
            con.commit()
            con.close()
            return "Success"
        else:
            con.close()
            con.commit()
            return "Success"
    else:
        con.close()
        return "Error"
                        
@app.route('/getnotice')
def getnotice():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()
    
    sql = "select * from notice order by n_num desc"
    cur.execute(sql)
    noticedata = cur.fetchall()
    noticelist = []

    
    for data in noticedata:
        cur.execute("select n_photo_url from notice_photo where n_num = '"+str(data[0])+"' order by n_index asc")
        photodata = cur.fetchall()
        photodict = []
        
        for p_data in photodata:
            
            photoobj = {'photo':p_data[0]}
            photodict.append(photoobj)

        cur.execute(" select count(n_num) from notice_comment where n_num = '"+str(data[0])+"'")
        comment_num = cur.fetchone()
        jsonnoticedata = {"num":data[0],"title":data[1], "content":data[2],"type":data[3],"time":str(data[4]),"photo":photodict,"commentnum":comment_num[0]}
        noticelist.append(jsonnoticedata)
       
    resultdata = jsonify(noticelist = noticelist)
    
    return resultdata

@app.route('/getnoticecomment', methods = ['POST','GET'])
def getcomment():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        n_num = request.values['n_num']
        lastnum = request.values['lastnum']
        count = int(lastnum)+20
        sql = "select * from notice_comment where n_num = '"+str(n_num)+"'order by n_c_num desc Limit "+str(lastnum)+","+str(count)+""

        cur.execute(sql)
        commentdata = cur.fetchall()
       
        commentlist = []
        for data in commentdata:
            cur.execute("select count(n_c_num) from notice_comment_comment where n_c_num = '"+str(data[1])+"'")
            c_comment_num = cur.fetchone()
            n_commentdata = {"n_num":data[0],"n_c_num":data[1],"n_c_time":str(data[2]),"u_id":data[3],"n_c_content":data[4],"cc_count":c_comment_num[0]}
            commentlist.append(n_commentdata)
        resultdata = jsonify(n_commentlist = commentlist)
    return resultdata

@app.route('/getnoticecommentofcomment', methods = ['POST','GET'])
def getcommentofcomment():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        n_num = request.values['n_num']
        n_c_num = request.values['n_c_num']
        lastnum = request.values['lastnum']
        count = int(lastnum)+20
        sql = "select * from notice_comment_comment where n_num = '"+str(n_num)+"' and n_c_num = '"+str(n_c_num)+"' order by n_cc_num desc Limit "+str(lastnum)+","+str(count)+""
        cur.execute(sql)
        commentdata = cur.fetchall()
        commentlist = []
        for data in commentdata:
            n_c_commentdata = {"n_num":n_num,"n_c_num":data[1],"n_cc_num": data[2],"n_cc_time":str(data[3]),"u_id":data[4],"n_cc_content":data[5]}
            commentlist.append(n_c_commentdata)
        resultdata = jsonify(n_commentlist = commentlist)
    return resultdata

@app.route('/sendnoticereply',methods = ['POST','GET'])
def sendnoticereply():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        n_num = request.values['n_num']
        u_id = request.values['u_id']
        n_c_content = request.values['content']
        sql ="insert into notice_comment values("+n_num+", 0, null, '"+str(u_id)+"','"+str(n_c_content)+"')"
       
        result = cur.execute(sql)
        con.commit()

        sql2 = "select * from notice_comment where n_num = '"+str(n_num)+"'"
        replylist = []
        cur.execute(sql2)
        notice = cur.fetchall()
        for item in notice:
            replylist.append(notice)
        a = len(replylist)
        print(a)

        if result == 1:
            cur.execute("select * from notice_comment order by n_c_num desc Limit 0,20")
            commentdata = cur.fetchall()
       
            commentlist = []
            for data in commentdata:
                cur.execute("select count(n_c_num) from notice_comment_comment where n_c_num = '"+str(data[1])+"'")
                c_comment_num = cur.fetchone()
                n_commentdata = {"n_num":data[0],"n_c_num":data[1],"n_c_time":str(data[2]),"u_id":data[3],"n_c_content":data[4],"cc_count":c_comment_num[0]}
                commentlist.append(n_commentdata)
            resultdata = jsonify(n_commentlist = commentlist, n_size = a, result="Success")

            return resultdata

        else:
            return "0"
    else:
        return "0"

@app.route('/sendnoticecommentreply',methods = ['POST','GET'])
def sendnoticecommentreply():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        n_num = request.values['n_num']
        n_c_num = request.values['n_c_num']
        u_id = request.values['u_id']
        n_c_content = request.values['content']
        sql ="insert into notice_comment_comment values("+n_num+", "+n_c_num+", 0, null, '"+str(u_id)+"','"+str(n_c_content)+"')"
        result = cur.execute(sql)
        con.commit()

     
        if result == 1:
            cur.execute("select * from notice_comment_comment where n_c_num = '"+str(n_c_num)+"' order by n_cc_num desc Limit 0,20")
            commentreplydata = cur.fetchall()
       
            commentreplylist = []
            for data in commentreplydata:
                cur.execute("select count(n_cc_num) from notice_comment_comment where n_c_num = '"+str(data[1])+"'")
                commentreply_num = cur.fetchone()
                a = commentreply_num[0]
                n_commentdata = {"n_num":data[0],"n_c_num":data[1],"n_cc_num":str(data[2]), "n_cc_time":str(data[3]),"u_id":data[4],"n_cc_content":data[5]}
                commentreplylist.append(n_commentdata)
            resultdata = jsonify(n_commentreplylist = commentreplylist, n_size = a, result="Success")
            print(resultdata)
            return resultdata

        else:
            return jsonify(result="Failed")
    else:
        return jsonify(result="Failed")
    return jsonify(result="Failed") 

@app.route('/deletenotice', methods = ['POST','GET'])
def deletenotice():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        n_num = request.values['n_num']
        sql = "delete from notice where n_num = '"+str(n_num)+"'"
        result = cur.execute(sql)
        con.commit()
   
        if result == 1:
            return "Success"
        else :
            return "Error"

@app.route('/deletenoticecomment', methods = ['POST','GET'])
def deletenoticecomment():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        n_num = request.values['n_num']
        n_c_num = request.values['n_c_num']
        sql = "delete from notice_comment where n_num ='"+str(n_num)+"' and n_c_num ='"+str(n_c_num)+"'"
        result = cur.execute(sql)
        con.commit()

        sql2 = "select count(n_num) from notice_comment where n_num = '"+str(n_num)+"'"
       
        cur.execute(sql2)
        c_count = cur.fetchone()
       
        if result == 1:
            cur.execute("select * from notice_comment order by n_c_num desc Limit 0,20")
            commentdata = cur.fetchall()
       
            commentlist = []
            for data in commentdata:
                cur.execute("select count(n_c_num) from notice_comment_comment where n_c_num = '"+str(data[1])+"'")
                c_comment_num = cur.fetchone()
                n_commentdata = {"n_num":data[0],"n_c_num":data[1],"n_c_time":str(data[2]),"u_id":data[3],"n_c_content":data[4],"cc_count":c_comment_num[0]}
                commentlist.append(n_commentdata)
            resultdata = jsonify(n_commentlist = commentlist, c_count = c_count[0],result="Success")
            return resultdata

        else:
            return "Error"

@app.route('/deletenoticecommentreply', methods = ['POST','GET'])
def deletenoticecommentreply():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        n_num = request.values['n_num']
        n_c_num = request.values['n_c_num']
        n_cc_num = request.values['n_cc_num']
        sql = "delete from notice_comment_comment where n_num ='"+str(n_num)+"' and n_c_num ='"+str(n_c_num)+"' and n_cc_num = '"+str(n_cc_num)+"'"
        result = cur.execute(sql)
        con.commit()
        
        if result == 1:
            cur.execute("select * from notice_comment_comment where n_c_num = '"+str(n_c_num)+"'order by n_cc_num desc Limit 0,20")
            commentreplydata = cur.fetchall()
       
            cur.execute("select count(n_cc_num) from notice_comment_comment where n_c_num = '"+str(n_c_num)+"'")
            cc_count = cur.fetchone()
            
            commentreplylist = []
            for data in commentreplydata:
                
                n_commentdata = {"n_num":data[0],"n_c_num":data[1],"n_cc_num":str(data[2]), "n_c_time":str(data[3]),"u_id":data[4],"n_c_content":data[5]}
                commentreplylist.append(n_commentdata)
            resultdata = jsonify(n_commentreplylist = commentreplylist, cc_count=cc_count, result="Success")
            print(resultdata)
            return resultdata

        else:
            return jsonify(result="Failed")
    else:
        return jsonify(result="Failed")
    return jsonify(result="Failed")
    
@app.route('/gettodayschedule', methods = ['POST','GET'])
def gettodayschedule():
      con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
      cur = con.cursor()

      if request.method == 'GET':
          year = request.values['year']
          month = request.values['month']
          day = request.values['day']

          sql = "select * from schedules where s_year = '"+str(year)+"' and s_month = '"+str(month)+"' and s_day = '"+str(day)+"'"
          r = cur.execute(sql)
          s_list = []
          s_data = cur.fetchall()
          for data in s_data:
              cur.execute("select * from team where t_num = '"+str(data[8])+"'")
              team = cur.fetchone()
              teamdata = {"t_name":team[0],"t_logo":team[1], "t_info":team[2], 
                  "t_facebook":team[3],"t_youtube":team[4]}
              s_dict = {"s_num":data[0],"s_year":data[1],"s_month":data[2],"s_day":data[3],"start_hour":data[4],
                        "start_min":data[5],"end_hour":data[6],"end_min":data[7],"t_info":teamdata,"s_lat":data[9],"s_long":data[10],
                        "s_park":data[11],"flag":data[12]}
              s_list.append(s_dict)
          resultdata = jsonify(schedule = s_list,result = r)
          return resultdata
      else:
          return jsonify(result="Failed")

@app.route('/checkschedule', methods = ['POST','GET'])
def registerschedule():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        s_year = request.values['s_year']   
        s_month = request.values['s_month'] 
        s_day = request.values['s_day']     
        start_hour = request.values['start_hour']
        start_min = request.values['start_min']
        end_hour = request.values['end_hour']
        end_min = request.values['end_min']

        sql = "select * from schedules where s_year = '"+str(s_year)+"' and s_month = '"+str(s_month)+"' and s_day = '"+str(s_day)+"'"
        cur.execute(sql)
        s_data = cur.fetchall()

        start_time = int(start_hour) * 60 + int(start_min)
        end_time = int(end_hour) * 60 + int(end_min)
        schedulelist = []
       
        for data in s_data:
            my_start_time = int(data[4])*60+int(data[5])
            my_end_time = int(data[6])*60+int(data[7])
           
            if my_start_time < start_time and my_end_time <=start_time :
                pass

            elif my_start_time >=end_time and my_end_time>end_time:
                pass
            else:
                sql = "select schedules.*,team.t_logo,team.t_name from schedules inner join team where team.t_num =schedules.t_num and s_year = '"+str(s_year)+"' and s_month = '"+str(s_month)+"' and s_day = '"+str(s_day)+"'"
                result = cur.execute(sql)
                if result !=0:
                    scheduledata = cur.fetchall()
                    schedulelist = []
                    for data in scheduledata :
                        scheduledict =  {"s_num":data[0],"s_year":data[1],"s_month":data[2],"s_day":data[3],"start_hour":data[4],
                            "start_min":data[5],"end_hour":data[6],"end_min":data[7],"t_num":data[8],"s_lat":data[9],"s_long":data[10],
                            "s_park":data[11],"flag":data[12],"car_num":data[13],"t_logo":data[14],"t_name":data[15]}
                        schedulelist.append(scheduledict)
        resultdata = jsonify(schedule = schedulelist, result = "Success")
        return resultdata
        
    else :
        return "Failed"

@app.route('/getuserid', methods = ['POST','GET'])
def getuserid():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()
     
    if request.method == 'GET':
        u_email = request.values['u_email']
        sql = "select u_id from user where u_email = '"+str(u_email)+"'"
        result = cur.execute(sql)
               
        if result != 0 :
            myid = cur.fetchall()
            realid = str(myid[0][0])
            return realid
        else :
            return "Failed"
    else:
        return "Failed"

@app.route('/findpassword', methods = ['POST','GET'])
def findpassword():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        u_email = request.values['u_email']
        u_id = request.values['u_id']
        sql = "select u_email from user where u_id = '"+str(u_id)+"' and u_email = '"+str(u_email)+"'"
        result = cur.execute(sql)

        # -*- coding: 949 -*-
        if result != 0:
            myuser = cur.fetchall()

            smtpserver = 'smtp.gmail.com'
            smtpport = 587
            smtpuser = 'hangang.manager@gmail.com'
            smtppw = 'zxcv1245'
            recipients = str(myuser[0][0])
           
            tempPW = ''
            for i in range(0,8,1):
                randValue = random.randint(0,10)
                tempPW += str(randValue)
            
                                    
            msg = MIMEText("안녕하세요? 임시비밀번호는 '"+str(tempPW)+"'입니다.'", _charset = 'utf-8')
            msg['Subject'] = '한강에서 놀자 임시 비밀번호입니다.'
            msg['From'] = smtpuser
            msg['To'] = recipients  #
                             
            session = smtplib.SMTP(smtpserver, smtpport)
            session.ehlo()
            session.starttls()
            session.ehlo()

            session.login(smtpuser, smtppw)
            smtpresult = session.sendmail(smtpuser, recipients, msg.as_string())

            if smtpresult:
                errstr = ''
                for recip in smtpresult.keys():
                    errstr = """Could not delivery mail to: %s

            Server said: %s
            %s
                    
            %s""" % (recip, smtpresult[recip][0], smtpresult[recip][1], errstr)
                raise smtplib.SMTPException(errstr)

            session.close()
            return "Success"
        else :
            return "Failed"
    else:
        return "Failed"

@app.route('/getteaminfo', methods = ['POST','GET'])
def getteaminfo():
      con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
      cur = con.cursor()

      if request.method == 'GET':
          sql = "select * from team order by t_name"
          result = cur.execute(sql)
          
          if result != 0:
              teamdata = cur.fetchall()
              teamlist = []
              for data in teamdata:
                  teamdict = {"t_num":data[0], "t_name":data[1],"t_logo":data[2], "t_info":data[3], "t_facebook":data[4],"t_youtube":data[5]}
                  teamlist.append(teamdict)
              resultdata = jsonify(team = teamlist, result="Success")
              return resultdata
          else:
              return jsonify(result="Failed")

      else:
          return jsonify(result="Failed")

@app.route('/getscheduleofteam', methods = ['POST', 'GET'])
def getscheduleofteam():
      con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
      cur = con.cursor()
      
      if request.method == 'GET':
          t_num = request.values['t_num']
          s_year = request.values['s_year']
          s_month = request.values['s_month']
          if s_month == '12':
              nextmonth = 1
          else:
              nextmonth = int(s_month)+1
          sql = "select schedules.*,team.t_logo,team.t_name from schedules inner join team where team.t_num ='"+str(t_num)+"' and schedules.t_num = '"+str(t_num)+"'"
          result = cur.execute(sql)
              
          if result !=0:
              scheduledata = cur.fetchall()
              schedulelist = []
              for data in scheduledata :
                 scheduledict =  {"s_num":data[0],"s_year":data[1],"s_month":data[2],"s_day":data[3],"start_hour":data[4],
                       "start_min":data[5],"end_hour":data[6],"end_min":data[7],"t_num":data[8],"s_lat":data[9],"s_long":data[10],
                        "s_park":data[11],"flag":data[12],"car_num":data[13],"t_logo":data[14],"t_name":data[15]}
                 schedulelist.append(scheduledict)
              resultdata = jsonify(schedule = schedulelist, result = "Success")
              return resultdata
          else:
              return jsonify(result = "Failed")
      else:
          return jsonify(result = "Failed")

@app.route('/getscheduleofallteam')
def getscheduleofallteam():
     con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
     cur = con.cursor()
      
     sql = "select schedules.*,team.t_logo,team.t_name from schedules inner join team where team.t_num =schedules.t_num"
     result = cur.execute(sql)
     if result !=0:
              scheduledata = cur.fetchall()
              schedulelist = []
              for data in scheduledata :
                 scheduledict =  {"s_num":data[0],"s_year":data[1],"s_month":data[2],"s_day":data[3],"start_hour":data[4],
                       "start_min":data[5],"end_hour":data[6],"end_min":data[7],"t_num":data[8],"s_lat":data[9],"s_long":data[10],
                        "s_park":data[11],"flag":data[12],"car_num":data[13],"t_logo":data[14],"t_name":data[15]}
                 schedulelist.append(scheduledict)
              resultdata = jsonify(schedule = schedulelist, result = "Success")
              return resultdata
     else:
              return jsonify(result = "Failed")

@app.route('/')
@app.route('/d')
def test():
     con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
     cur = con.cursor()

     cur.execute("select * from team where t_num = 1")
     temp = cur.fetchone()
     teamdata = {"t_name":temp[0],"t_logo":temp[1], "t_info":temp[2], 
                  "t_facebook":temp[3],"t_youtube":temp[4]}
     return teamdata

if __name__ == '__main__': 
    app.debug = True
    app.run(host='203.252.166.213', port = 3000)

from flask import Flask, jsonify,request, json
import base64
from io import BytesIO
import image
import pymysql as mysql
import smtplib
from email.mime.text import MIMEText
import string
import random
from math import *
from datetime import datetime

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
        sql ="insert into user values('"+str(u_id)+"','"+str(u_passwd)+"','"+str(u_name)+"','"+str(u_email)+"',1,True, null, null)"
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
        userdata = {"u_id" : userinfo[0][0], "u_name":userinfo[0][2], "u_email" : userinfo[0][3],"u_permission" : userinfo[0][4], "push" : userinfo[0][5],"u_photo" :userinfo[0][7]}
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
        title = data['title']
        content = data['content']
        type = data['type']
        sql = "insert into notice values(null,'"+str(title)+"','"+str(content)+"','"+str(type)+"',null)"
        result = cur.execute(sql)
        if result ==1:
            photourl = "D:/Program Files (x86)/Apache Software Foundation/Apache2.2/htdocs/noticeImg/"
            cur.execute("select Max(n_num) from notice ")
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
            print(p_data)
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
        sql = "select notice_comment.*, user.u_permission, user.u_photo from notice_comment inner join user where notice_comment.u_id = user.u_id and n_num = '"+str(n_num)+"'order by n_c_num desc Limit "+str(lastnum)+","+str(count)+""
         
        cur.execute(sql)
        commentdata = cur.fetchall()
        
        
        commentlist = []
        for data in commentdata:
            cur.execute("select count(n_c_num) from notice_comment_comment where n_c_num = '"+str(data[1])+"'")
            c_comment_num = cur.fetchone()
            n_commentdata = {"n_num":data[0],"n_c_num":data[1],"n_c_time":str(data[2]),"u_id":data[3],"n_c_content":data[4],"u_permission":data[5],"u_photo":data[6],"cc_count":c_comment_num[0]}
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
        sql = "select notice_comment_comment.*, user.u_permission, user.u_photo from notice_comment_comment inner join user where notice_comment_comment.u_id = user.u_id and n_num = '"+str(n_num)+"' and n_c_num = '"+str(n_c_num)+"' order by n_cc_num desc Limit "+str(lastnum)+","+str(count)+""
        cur.execute(sql)
        commentdata = cur.fetchall()
        commentlist = []
        for data in commentdata:
            n_c_commentdata = {"n_num":n_num,"n_c_num":data[1],"n_cc_num": data[2],"n_cc_time":str(data[3]),"u_id":data[4],"n_cc_content":data[5],"u_permission":data[6],"u_photo":data[7]}
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

        sql2 = "select count(n_num) from notice_comment where n_num = '"+str(n_num)+"'"
        replylist = []
        cur.execute(sql2)
        noticereply_num = cur.fetchone()
        

        if result == 1:
            cur.execute("select notice_comment.*, user.u_permission, user.u_photo from notice_comment inner join user where notice_comment.u_id = user.u_id and n_num and n_num = '"+str(n_num)+"' order by n_c_num desc Limit 0,20")
            commentdata = cur.fetchall()
       
            commentlist = []
            for data in commentdata:
                cur.execute("select count(n_c_num) from notice_comment_comment where n_c_num = '"+str(data[1])+"'")
                c_comment_num = cur.fetchone()
                n_commentdata = {"n_num":data[0],"n_c_num":data[1],"n_c_time":str(data[2]),"u_id":data[3],"n_c_content":data[4],"u_permission":data[5],"u_photo":data[6],"cc_count":c_comment_num[0]}
                commentlist.append(n_commentdata)
            resultdata = jsonify(n_commentlist = commentlist, c_count = noticereply_num[0], result="Success")

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
            cur.execute("select notice_comment_comment.*, user.u_permission, user.u_photo from notice_comment_comment inner join user where notice_comment_comment.u_id = user.u_id and n_c_num = '"+str(n_c_num)+"' order by n_cc_num desc Limit 0,20")
            commentreplydata = cur.fetchall()
            cur.execute("select count(n_cc_num) from notice_comment_comment where n_c_num = '"+str(n_c_num)+"'")
            commentreply_num = cur.fetchone()
            a = commentreply_num[0]
            commentreplylist = []
            for data in commentreplydata:            
                n_commentdata = {"n_num":data[0],"n_c_num":data[1],"n_cc_num":str(data[2]), "n_cc_time":str(data[3]),"u_id":data[4],"n_cc_content":data[5],"u_permission":data[6],"u_photo":data[7]}
                commentreplylist.append(n_commentdata)
            resultdata = jsonify(n_commentreplylist = commentreplylist, cc_count = a, result="Success")
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

        cur.execute("delete from notice_comment_comment where n_c_num = '"+str(n_c_num)+"'")
        sql = "delete from notice_comment where n_num ='"+str(n_num)+"' and n_c_num ='"+str(n_c_num)+"'"
        result = cur.execute(sql)
        con.commit()

        sql2 = "select count(n_num) from notice_comment where n_num = '"+str(n_num)+"'"
       
        cur.execute(sql2)
        c_count = cur.fetchone()
       
        if result == 1:
            cur.execute("select notice_comment.*, user.u_permission, user.u_photo from notice_comment inner join user where notice_comment.u_id = user.u_id and n_num and n_num = '"+str(n_num)+"' order by n_c_num desc Limit 0,20")
            commentdata = cur.fetchall()
       
            commentlist = []
            for data in commentdata:
                cur.execute("select count(n_c_num) from notice_comment_comment where n_c_num = '"+str(data[1])+"'")
                c_comment_num = cur.fetchone()
                n_commentdata = {"n_num":data[0],"n_c_num":data[1],"n_c_time":str(data[2]),"u_id":data[3],"n_c_content":data[4],"u_permission":data[5],"u_photo":data[6],"cc_count":c_comment_num[0]}
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
            cur.execute("select notice_comment_comment.*, user.u_permission, user.u_photo from notice_comment_comment inner join user where notice_comment_comment.u_id = user.u_id and n_c_num = '"+str(n_c_num)+"' order by n_cc_num desc Limit 0,20")
            commentreplydata = cur.fetchall()
       
            cur.execute("select count(n_cc_num) from notice_comment_comment where n_c_num = '"+str(n_c_num)+"'")
            cc_count = cur.fetchone()
            
            commentreplylist = []
            for data in commentreplydata:
                
                n_commentdata =  n_commentdata = {"n_num":data[0],"n_c_num":data[1],"n_cc_num":str(data[2]), "n_cc_time":str(data[3]),"u_id":data[4],"n_cc_content":data[5],"u_permission":data[6],"u_photo":data[7]}
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

          sql = "select * from schedules where s_year = '"+str(year)+"' and s_month = '"+str(month)+"' and s_day = '"+str(day)+"'  order by schedules.s_park"
          r = cur.execute(sql)
          s_list = []
          s_data = cur.fetchall()
          for data in s_data:
              cur.execute("select * from team where t_num = '"+str(data[8])+"' order by schedules.s_park")
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
def checkschedule():
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
                sql = "select schedules.*,team.t_logo,team.t_name from schedules inner join team where team.t_num =schedules.t_num and s_year = '"+str(s_year)+"' and s_month = '"+str(s_month)+"' and s_day = '"+str(s_day)+"' order by schedules.s_park"
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

@app.route('/getschedule',methods = ['POST','GET'])
def getschedule():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        s_year = request.values['year']
        s_month = request.values['month']
        nextmonth =0
        if s_month == '12':
             nextmonth = 1
        else:
             nextmonth = int(s_month)+1
        sql = "select schedules.*,team.t_logo,team.t_name from schedules inner join team where team.t_num =schedules.t_num and s_year = '"+str(s_year)+"' and (s_month = '"+str(s_month)+"' or s_month = '"+str(nextmonth)+"') order by schedules.s_park"
        result = cur.execute(sql)
        s_data = cur.fetchall()

        schedulelist = []
        if result != 0:
            for data in s_data :
                scheduledict =  {"s_num":data[0],"s_year":data[1],"s_month":data[2],"s_day":data[3],"start_hour":data[4],
                                "start_min":data[5],"end_hour":data[6],"end_min":data[7],"t_num":data[8],"s_lat":data[9],"s_long":data[10],
                                "s_park":data[11],"flag":data[12],"car_num":data[13],"t_logo":data[14],"t_name":data[15]}
                schedulelist.append(scheduledict)

            resultdata = jsonify(schedule = schedulelist,result = "Success")
            return resultdata
        else:
            return jsonify(result = "Failed")
    else:
        return jsonify(result = "Failed")

@app.route('/deleterealtimeschedule', methods = ['POST','GET'])
def deleterealtimeschedule():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        r_num = request.values['r_num']
        sql ="update realtime_schedules set flag = 2 where r_s_num = "+r_num
        result = cur.execute(sql)
        if result != 0 :
            con.commit()
            return "Success"
        else:
            return "Failed"
    else:
        return "Failed"

        

        

@app.route('/deleteschedule',methods = ['POST','GET'])
def deleteschedule():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        s_num = request.values['s_num']

        sql = "delete from schedules where s_num = '"+str(s_num)+"'"
        result = cur.execute(sql)
        con.commit()
        if result != 0 :
            return "Success"
        else:
            return "Failed"
    else:
        return "Failed"



@app.route('/registschedule', methods = ['POST','GET'])
def registschedule():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        s_year = request.values['year']   
        s_month = request.values['month'] 
        s_day = request.values['day']     
        start_hour = request.values['start_hour']
        start_min = request.values['start_min']
        end_hour = request.values['end_hour']
        end_min = request.values['end_min']
        t_num = request.values['t_num']
        s_lat = request.values['lat']
        s_long = request.values['lng']
        s_park = request.values['park']
        car_num = request.values['car_num']

        sql = "select * from schedules where s_year = '"+str(s_year)+"' and s_month = '"+str(s_month)+"' and s_day = '"+str(s_day)+"' and s_park = '"+str(s_park)+"'"
        cur.execute(sql)
        s_data = cur.fetchall()

        start_time = int(start_hour) * 60 + int(start_min)
        end_time = int(end_hour) * 60 + int(end_min)
        schedulelist = []
        r = 0
        for data in s_data:
            my_start_time = int(data[4])*60+int(data[5])
            my_end_time = int(data[6])*60+int(data[7])
           
            if not((my_start_time < start_time and my_end_time <=start_time) or (my_start_time >=end_time and my_end_time>end_time)) and abs(getdistance(float(s_long),float(s_lat),float(data[10]),float(data[9]))) < 0.03 :
                print(abs(getdistance(float(s_long),float(s_lat),float(data[10]),float(data[9]))))
                return "Failed"
                
            else:
                print(not((my_start_time < start_time and my_end_time <=start_time) or (my_start_time >=end_time and my_end_time>end_time)))
                print(abs(getdistance(float(s_long),float(s_lat),float(data[10]),float(data[9]))))
                pass

    
             #print(abs(getdistance(float(s_long),float(s_lat),float(data[10]),float(data[9]))))
        insert_sql = "insert into schedules values(null,'"+str(s_year)+"','"+str(s_month)+"','"+str(s_day)+"','"+str(start_hour)+"','"+str(start_min)+"','"+str(end_hour)+"','"+str(end_min)+"','"+str(t_num)+"','"+str(s_lat)+"','"+str(s_long)+"','"+str(s_park)+"',0,'"+str(car_num)+"')"
        result = cur.execute(insert_sql)
        con.commit()
        print(result)
        if result == 1:
               return "Success"
        else:
               return "Failed"
      

    else:
        return "Failed"

def getdistance(lon1,lat1,lon2,lat2):
    lon1,lat1,lon2,lat2 = map(radians,[lon1,lat1,lon2,lat2])
    dlon = lon2-lon1
    dlat = lat2-lat1

    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2* atan2(sqrt(a),sqrt(1-a))

    km = 6367*c
    return km


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
          nextmonth = 0
          if s_month == '12':
              nextmonth = 1
          else:
              nextmonth = int(s_month)+1
          sql = "select schedules.*,team.t_logo,team.t_name from schedules inner join team where team.t_num ='"+str(t_num)+"' and schedules.t_num = '"+str(t_num)+"' and s_year = '"+str(s_year)+"' and (s_month = '"+str(s_month)+"' or s_month = '"+str(nextmonth)+"') order by schedules.s_park"
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
      
     sql = "select schedules.*,team.t_logo,team.t_name from schedules inner join team where team.t_num =schedules.t_num order by schedules.s_park"
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

@app.route('/checktodayschedule')
def checktodayschedule():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
          t_num = request.values['t_num']
          s_year = request.values['s_year']
          s_month = request.values['s_month']
          s_day = request.values['s_day']

          sql = "select schedules.*, t_logo, t_name from schedules inner join team where s_year = '" + str(s_year) + "' and s_month = '" + str(s_month) + "' and s_day = '" + str(s_day) + "' and schedules.t_num = '" + str(t_num) + "' and team.t_num = '" + str(t_num) + "' and flag = 0 order by schedules.s_park"
          result = cur.execute(sql)
          
          if result ==0:
                  sql = "select realtime_schedules.*, t_logo, t_name from realtime_schedules inner join team where r_s_year = '" + str(s_year) + "' and r_s_month = '" + str(s_month) + "' and r_s_day = '" + str(s_day) + "' and realtime_schedules.t_num = '" + str(t_num) + "' and team.t_num = '" + str(t_num) + "' and flag = 1 order by realtime_schedules.s_park"
                  r_result = cur.execute(sql)
                  realtimedata = cur.fetchall()
                  if r_result != 0:
                      for data in realtimedata:
                          realtimedict = {"r_num":data[0],"r_year":data[1],"r_month":data[2],"r_day":data[3],"start_hour":data[4],
                              "start_min":data[5],"end_hour":data[6],"end_min":data[7],"t_num":data[8],"r_lat":data[9],"r_long":data[10],
                              "r_park":data[11],"flag":data[12],"t_logo":data[13],"t_name":data[14]}
                      resultdata = jsonify(realtime = realtimedict, result = "Success")
                      return resultdata
                  else:
                      return jsonify(result = "Failed")  
                      
          else:

              scheduledata = cur.fetchall()
              scheduledict = {}
              for data in scheduledata :
                  scheduledict = {"s_num":data[0],"s_year":data[1],"s_month":data[2],"s_day":data[3],"start_hour":data[4],
                      "start_min":data[5],"end_hour":data[6],"end_min":data[7],"t_num":data[8],"s_lat":data[9],"s_long":data[10],
                      "s_park":data[11],"flag":data[12],"car_num":data[13],"t_logo":data[14],"t_name":data[15]}
             
              sql = "select realtime_schedules.*, t_logo, t_name from realtime_schedules inner join team where r_s_year = '" + str(s_year) + "' and r_s_month = '" + str(s_month) + "' and r_s_day = '" + str(s_day) + "' and realtime_schedules.t_num = '" + str(t_num) + "' and team.t_num = '" + str(t_num) + "' and flag = 1 order by realtime_schedules.s_park"
              r_result = cur.execute(sql)
              realtimedata = cur.fetchall()
              if r_result != 0:
                  for data in realtimedata:
                      realtimedict = {"r_num":data[0],"r_year":data[1],"r_month":data[2],"r_day":data[3],"start_hour":data[4],
                          "start_min":data[5],"end_hour":data[6],"end_min":data[7],"t_num":data[8],"r_lat":data[9],"r_long":data[10],
                          "r_park":data[11],"flag":data[12],"t_logo":data[13],"t_name":data[14]}
                  resultdata = jsonify(schedule = scheduledict, realtime = realtimedict, result = "Success")
                  return resultdata
              else:
                  return jsonify(schedule = scheduledict, result = "Success") 
    
    else:
        return jsonify(result = "Failed")

@app.route('/registrealtimeschedule')
def registrealtimeschedule():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        r_s_year = request.values['r_year']
        r_s_month = request.values['r_month']
        r_s_day = request.values['r_day']
        start_hour = request.values['start_hour']
        start_min = request.values['start_min']
        t_num = request.values['t_num']
        s_lat = request.values['r_lat']
        s_long = request.values['r_lng']
        s_park = request.values['park']
        s_num = request.values['s_num']

        if s_num != -1 :
            sql ="insert into realtime_schedules values(0, "+r_s_year+", "+r_s_month+", "+r_s_day+", "+start_hour+", "+start_min+", 0, 0, "+t_num+", "+s_lat+","+s_long+", '"+str(s_park)+"', 1)"
            result = cur.execute(sql)
            con.commit()

            sql ="update schedules set flag = 1 where s_num = "+s_num
            cur.execute(sql)
            con.commit()
        else:
            pass
        
        if result != 0:
            return "Success"
        else :
            return "Failed" 
    else:
        return "Failed"

@app.route('/getrealtimeschedule',methods=['POST','GET'])
def getrealtimeschedule():
     con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
     cur = con.cursor()

     if request.method == 'GET':
        r_year = request.values['r_year']
        r_month = request.values['r_month']
        r_day = request.values['r_day']

        sql = "select realtime_schedules.*, t_logo, t_name from realtime_schedules inner join team where realtime_schedules.t_num = team.t_num and r_s_year = '" + str(r_year) + "' and r_s_month = '" + str(r_month) + "' and r_s_day = '" + str(r_day) + "' and flag = 1 order by realtime_schedules.s_park"
        result = cur.execute(sql)
        realtimedata = cur.fetchall()
        r_list = []
        
        if result != 0:
            for data in realtimedata:
                realtimedict = {"r_num":data[0],"r_year":data[1],"r_month":data[2],"r_day":data[3],"start_hour":data[4],
                    "start_min":data[5],"end_hour":data[6],"end_min":data[7],"t_num":data[8],"r_lat":data[9],"r_long":data[10],
                    "r_park":data[11],"flag":data[12],"t_logo":data[13],"t_name":data[14]}
                r_list.append(realtimedict)
            resultdata = jsonify(realtime = r_list, result = "Success")
            return resultdata
        else:
            return jsonify(result = "Failed") 
     else:
        return jsonify(result = "Failed")



@app.route('/getqna',methods=['POST','GET'])
def getqna():
        con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
        cur = con.cursor()
  
        sql = "select * from qna order by q_time desc"
        result = cur.execute(sql)
        if result != 0:
            qnadata = cur.fetchall()
            qnalist = []
            for data in qnadata:
                cur.execute("select count(q_num) from qna_reply where q_num = '"+str(data[1])+"'")
                count = cur.fetchone()
                qnadict = {"u_id": data[0],"q_num":data[1],"title":data[2],"content":data[3],"time":data[4],"c_count":count[0]}
                qnalist.append(qnadict)
            resultdata = jsonify(qna = qnalist, result = "Success")
            return resultdata
        else:
            return jsonify(result = "Failed")


@app.route('/getqnareply',methods=['POST','GET'])
def getqnareply():
     con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
     cur = con.cursor()

     if request.method == 'GET':
           q_num = request.values['q_num']
           lastnum = request.values['lastnum']
           count = int(lastnum)+20
           sql = "select qna_reply.*, user.u_permission, user.u_photo from qna_reply inner join user where qna_reply.u_id = user.u_id and q_num = '"+str(q_num)+"'order by q_r_num desc Limit "+str(lastnum)+","+str(count)+""
         
           cur.execute(sql)
           commentdata = cur.fetchall()
        
        
           commentlist = []
           for data in commentdata:
               cur.execute("select count(q_r_num) from qna_reply_reply where q_r_num = '"+str(data[1])+"'")
               c_comment_num = cur.fetchone()
               n_commentdata = {"q_num":data[0],"q_r_num":data[1],"q_r_time":str(data[2]),"u_id":data[3],"q_r_content":data[4],"u_permission":data[5],"u_photo":data[6],"cc_count":c_comment_num[0]}
               commentlist.append(n_commentdata)
           resultdata = jsonify(q_commentlist = commentlist)
           return resultdata

@app.route('/sendqnareply',methods=['POST','GET'])
def sendqnareply():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        q_num = request.values['q_num']
        u_id = request.values['u_id']
        q_r_content = request.values['content']
        sql ="insert into qna_reply values("+q_num+", 0, null, '"+str(u_id)+"','"+str(q_r_content)+"')"
       
        result = cur.execute(sql)
        con.commit()

       
        sql2 = "select count(q_num) from qna_reply where q_num = '"+str(q_num)+"'"
        replylist = []
        cur.execute(sql2)
        qnareply_num = cur.fetchone()

        if result == 1:
            cur.execute("select qna_reply.*, user.u_permission, user.u_photo from qna_reply inner join user where qna_reply.u_id = user.u_id and q_num and q_num = '"+str(q_num)+"' order by q_r_num desc Limit 0,20")
            commentdata = cur.fetchall()
       
            commentlist = []
            for data in commentdata:
                cur.execute("select count(q_r_num) from qna_reply_reply where q_r_num = '"+str(data[1])+"'")
                c_comment_num = cur.fetchone()
                n_commentdata = {"q_num":data[0],"q_r_num":data[1],"q_r_time":str(data[2]),"u_id":data[3],"q_r_content":data[4],"u_permission":data[5],"u_photo":data[6],"cc_count":c_comment_num[0]}
                commentlist.append(n_commentdata)
            resultdata = jsonify(q_commentlist = commentlist, c_count = qnareply_num[0], result="Success")

            return resultdata

        else:
            return jsonify(result = "Failed")
    else:
        return jsonify(result = "Failed")

@app.route('/deleteqnareply', methods = ['POST','GET'])
def deleteqnareply():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        q_num = request.values['q_num']
        q_r_num = request.values['q_r_num']

        cur.execute("delete from qna_reply_reply where q_r_num = '"+str(q_r_num)+"'")
        sql = "delete from qna_reply where q_num ='"+str(q_num)+"' and q_r_num ='"+str(q_r_num)+"'"
        result = cur.execute(sql)
        con.commit()

        sql2 = "select count(q_num) from qna_reply where q_num = '"+str(q_num)+"'"
       
        cur.execute(sql2)
        c_count = cur.fetchone()
       
        if result == 1:
            cur.execute("select qna_reply.*, user.u_permission, user.u_photo from qna_reply inner join user where qna_reply.u_id = user.u_id and q_num = '"+str(q_num)+"' order by q_r_num desc Limit 0,20")
            commentdata = cur.fetchall()
       
            commentlist = []
            for data in commentdata:
                cur.execute("select count(q_r_num) from qna_reply_reply where q_r_num = '"+str(data[1])+"'")
                c_comment_num = cur.fetchone()
                n_commentdata = {"q_num":data[0],"q_r_num":data[1],"q_r_time":str(data[2]),"u_id":data[3],"q_r_content":data[4],"u_permission":data[5],"u_photo":data[6],"cc_count":c_comment_num[0]}
                commentlist.append(n_commentdata)
            resultdata = jsonify(q_commentlist = commentlist, c_count = c_count[0],result="Success")
            return resultdata

        else:
            return "Error"

@app.route('/getteambloginfo',methods=['POST','GET'])
def getteambloginfo():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        t_num = request.values['t_num']
        year = request.values['year']
        month = request.values['month']
        
        nextmonth =0
        if month == '12':
             nextmonth = 1
        else:
             nextmonth = int(s_month)+1
        sql = "select schedules.*,team.t_logo,team.t_name from schedules inner join team where team.t_num = '"+str(t_num)+"' and schedules.t_num= '"+str(t_num)+"' and s_year = '"+str(year)+"' and (s_month = '"+str(month)+"' or s_month = '"+str(nextmonth)+"') order by schedules.s_park"
        result = cur.execute(sql)
        s_data = cur.fetchall()
        schedulelist = []
        
        if result != 0:
            for data in s_data :
                scheduledict =  {"s_num":data[0],"s_year":data[1],"s_month":data[2],"s_day":data[3],"start_hour":data[4],
                                "start_min":data[5],"end_hour":data[6],"end_min":data[7],"t_num":data[8],"s_lat":data[9],"s_long":data[10],
                                "s_park":data[11],"flag":data[12],"car_num":data[13],"t_logo":data[14],"t_name":data[15]}
                schedulelist.append(scheduledict)

           
        cur.execute("select * from team where t_num = '"+str(t_num)+"'")
        teaminfo = cur.fetchall()
        teamdata = {"t_name":teaminfo[0][1],"t_logo":teaminfo[0][2], "t_info":teaminfo[0][3], "t_facebook":teaminfo[0][4],"t_youtube":teaminfo[0][5], "t_num":teaminfo[0][0],"t_backgroundimg":teaminfo[0][6]}
        
        #####
        sql = "select cheerful.*, team.t_name from cheerful inner join team where team.t_num = '"+str(t_num)+"' and cheerful.t_num = '"+str(t_num)+"' order by c_time desc Limit 0,20 "
        result = cur.execute(sql)
        cheerdata = cur.fetchall()
        cheer_list = []
            
        if result != 0:
            for data in cheerdata:
                    
                sql = "select count(c_num) from cheerful_reply where c_num = '"+str(data[0])+"'"
                cur.execute(sql)
                countdata = cur.fetchone()
                    
                sql = "select u_permission, u_photo from user where u_id = '"+str(data[1])+"'"
                cur.execute(sql)
                cheeruserdata = cur.fetchone()
                  
                cheerdict = {"ch_num":data[0],"u_id":data[1],"t_num":data[2],"ch_content":data[3],"ch_photourl":data[4],
                    "ch_time":str(data[5]),"t_name":data[6],"u_permission":cheeruserdata[0],"u_photo":cheeruserdata[1], "ch_count":countdata[0]}
                cheer_list.append(cheerdict)
        #####
                
        gallery_result = cur.execute("select * from team_gallery where t_num = '"+str(t_num)+"' order by num desc Limit 0,20" )
        gallery_data = cur.fetchall()
        gallery_list = []
        if gallery_result !=0:
            for g_data in gallery_data:
                gallerydict = {"num":g_data[0],"t_num":g_data[1],"photo_url":g_data[2]}
                gallery_list.append(gallerydict)

        resultdata = jsonify(schedule = schedulelist,teaminfo = teamdata, cheerful = cheer_list,gallery = gallery_list)
        return resultdata
    else:
        return jsonify(result = "Failed")

@app.route('/changeteaminfo',methods=['POST','GET'])
def changeteaminfo():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        t_num = request.values['t_num']
        t_info = request.values['t_info']
        
        sql = "update team set t_info = '"+str(t_info)+"' where t_num = "+t_num
        result = cur.execute(sql)
        
        if result != 0 :
            con.commit()
            return "Success"
        else :
            return "Failed"
    else :
        return "Failed"

@app.route('/changeteamfacebook',methods=['POST','GET'])
def changeteamfacebook():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        t_num = request.values['t_num']
        t_facebook = request.values['t_facebook']
        
        sql = "update team set t_facebook = '"+str(t_facebook)+"' where t_num = "+t_num
        result = cur.execute(sql)
        
        if result != 0 :
            con.commit()
            return "Success"
        else :
            return "Failed"
    else :
        return "Failed"

@app.route('/changeteamyoutube',methods=['POST','GET'])
def changeteamyoutube():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        t_num = request.values['t_num']
        t_youtube = request.values['t_youtube']
        
        sql = "update team set t_youtube = '"+str(t_youtube)+"' where t_num = "+t_num
        result = cur.execute(sql)
        
        if result != 0 :
            con.commit()
            return "Success"
        else :
            return "Failed"
    else :
        return "Failed"

@app.route('/deleteteamfacebook',methods=['POST','GET'])
def deleteteamfacebook():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()


    if request.method == 'GET':
        t_num = request.values['t_num']

        sql = "update team set t_facebook = '' where t_num = "+t_num
        result = cur.execute(sql)

        if result !=0:
            con.commit()
            return "Success"
        else:
            return "Failed"
    else:
        return "Failed"

@app.route('/deleteteamyoutube',methods=['POST','GET'])
def deleteteamyoutube():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        t_num = request.values['t_num']

        sql = "update team set t_youtube = '' where t_num = "+t_num
        result = cur.execute(sql)

        if result !=0:
            con.commit()
            return "Success"
        else:
            return "Failed"
    else:
        return "Failed"

@app.route('/registbookmark',methods=['POST','GET'])
def registbookmark():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        u_id = request.values['u_id']
        t_num = request.values['t_num']
        event = request.values['event']
        print(event)
        if str(event) == "delete":
            sql = "delete from bookmark where u_id = '"+str(u_id)+"' and t_num = '"+str(t_num)+"'"
            result = cur.execute(sql)

            if result !=0:
                con.commit()
                return "Success"
            else:
                return "Failed"
            
        else:
            sql ="insert into bookmark values('"+str(u_id)+"',"+t_num+")"
            result = cur.execute(sql)

            if result !=0:
                con.commit()
                return "Success"
            else:
                return "Failed"
    else:
        return "Failed"

@app.route('/deletebookmark',methods=['POST','GET'])
def deletebookmark():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        u_id = request.values['u_id']
        t_num = request.values['t_num']

        sql = "delete from bookmark where u_id = '"+str(u_id)+"' and t_num = "+t_num
        result = cur.execute(sql)

        if result !=0:
            con.commit()
            return "Success"
        else:
            return "Failed"
    else:
        return "Failed"

@app.route('/changeteamlogoimage',methods=['POST','GET'])
def changeteamlogoimage():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        t_num = request.values['t_num']
        t_logoImg = request.values['t_logoImg']

        logo_url = "D:/Program Files (x86)/Apache Software Foundation/Apache2.2/htdocs/teamImg/"
        filename = str(logo_url)+t_num+"_"+str(datetime.today().strftime("%Y%m%d%H%M%S"))
        logo_filename = "/teamImg/"+t_num+"_"+str(datetime.today().strftime("%Y%m%d%H%M%S"))

        with open(str(filename), "wb") as img:
            img.write(base64.b64decode(t_logoImg))
            cur.execute("update team set t_logo = '"+str(logo_filename)+"' where t_num = "+t_num)
        con.commit()
        con.close()

        return jsonify(url = logo_filename, result = "Success")
    else:
        return jsonify(result = "Failed")

@app.route('/changebackgroundimage',methods=['POST','GET'])
def changebackgroundimage():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        t_num = request.values['t_num']
        t_background_img = request.values['t_background_img']
         
        bg_url = "D:/Program Files (x86)/Apache Software Foundation/Apache2.2/htdocs/teambackimg/"
        filename = str(bg_url)+t_num+"_"+str(datetime.today().strftime("%Y%m%d%H%M%S"))
        bg_filename = "/teambackimg/"+t_num+"_"+str(datetime.today().strftime("%Y%m%d%H%M%S"))

        with open(str(filename), "wb") as img:
            img.write(base64.b64decode(t_background_img))
            cur.execute("update team set t_background_img = '"+str(bg_filename)+"' where t_num = "+t_num)
        con.commit()
        con.close()

        return jsonify(url = bg_filename, result = "Success")
    else:
        return jsonify(result = "Failed")

@app.route('/registreport',methods=['POST','GET'])
def registreport():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        #r_year = request.values['r_year']
        #r_month = request.values['r_month']
        #r_day = request.values['r_day']
        #r_starthour = request.values['r_starthour']
        #r_startmin = request.values['r_startmin']
        #r_endhour = request.values['r_endhour']
        #r_endmin = request.values['r_endmin']
        #people_num = request.values['people_num']
        #contents = request.values['contents']
        #t_num = request.values['t_num']
        #park = request.values['park']

        jsondata = request.values['report']
        data = json.loads(jsondata)
        r_year = data['r_year']
        r_month = data['r_month']
        r_day = data['r_day']
        r_starthour = data['r_starthour']
        r_startmin = data['r_startmin']
        r_endhour = data['r_endhour']
        r_endmin = data['r_endmin']
        people_num = data['people_num']
        contents = data['contents']
        t_num = data['t_num']
        park = data['park']
        r_members = data['r_members']

        print(r_year)
        print(r_month)
        print(r_day)
        print(r_starthour)
        print(r_startmin)
        print(r_endhour)
        print(r_endmin)
        print(people_num)
        print(contents)
        print(t_num)
        print(park)
        print(r_members)

        sql = "insert into report values(0, '"+str(r_year)+"','"+str(r_month)+"','"+str(r_day)+"','"+str(r_starthour)+"','"+str(r_startmin)+"','"+str(r_endhour)+"','"+str(r_endmin)+"','"+str(people_num)+"','"+str(contents)+"',0,'"+str(t_num)+"','"+str(park)+"','"+str(r_members)+"')"
        result = cur.execute(sql)
        print(result)

        if result ==1:
            photourl = "D:/Program Files (x86)/Apache Software Foundation/Apache2.2/htdocs/reportImg/"
            cur.execute("select report_num from report where r_year = '"+str(r_year)+"' and r_month = '"+str(r_month)+"' and r_day = '"+str(r_day)+"'")
            number = cur.fetchone()
            jsonphotoarr = data['photo']

            for photo in jsonphotoarr:
                filename = str(photourl)+str(number[0])+"_"+str(photo['index'])+".jpg" 
                in_db_filename = "/reportImg/"+str(number[0])+"_"+str(photo['index'])+".jpg" 
                with open(str(filename), "wb") as img:
                    img.write(base64.b64decode(photo['photo']))      
                    cur.execute("insert into report_photo values('"+str(number[0])+"','"+str(in_db_filename)+"')")

            con.commit()
            con.close()
            return "Success"
        else:
            con.close()
            return "Failed"
    else:
        return "Failed"

@app.route('/changeuserinfo',methods=['POST','GET'])
def changeuserinfo():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'POST':
        u_id = request.values['u_id']
        u_email = request.values['u_email']
        u_passwd = request.values['u_passwd']

        #print(u_id)
        #print(u_email)
        #print(u_passwd)
        sql = "update user set u_passwd = '"+str(u_passwd)+"', u_email = '"+str(u_email)+"' where u_id = '"+str(u_id)+"'"
        result = cur.execute(sql)
        print(result)

        if result != 0:
            con.commit()
            con.close()
            return "Success"
        else :
            con.close()
            return "Failed"
    else:
        return "Failed"

@app.route('/getreport',methods=['POST','GET'])
def getreport():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        r_year = request.values['r_year']
        r_month = request.values['r_month']
        t_num = request.values['t_num']

        if int(t_num) != -1:
            sql = "select * from report inner join team where report.r_year = '"+str(r_year)+"' and report.r_month = '"+str(r_month)+"' and team.t_num = '"+str(t_num)+"' and report.t_num = '"+str(t_num)+"'"
            result = cur.execute(sql)
            reportdata = cur.fetchall()
            report_list = []

            if result != 0:
                for data in reportdata:
                    sql = "select report_photo.r_photourl from report inner join report_photo where report_photo.report_num = '"+str(data[0])+"' and report.report_num = '"+str(data[0])+"'"
                    cur.execute(sql)
                    urldata = cur.fetchall()
                    urllist = []
                    for u_data in urldata :
                        urldict = {'photo':u_data[0]}
                        urllist.append(urldict)
                                                       
                    reportdict = {"report_num":data[0],"r_year":data[1],"r_month":data[2],"r_day":data[3],"r_starthour":data[4],
                        "r_startmin":data[5],"r_endhour":data[6],"r_endmin":data[7],"people_num":data[8],"contents":data[9],"flag":data[10],
                        "t_num":data[11],"park":data[12],"r_members":data[13],"t_name":data[15],"t_logo":data[16],"photo":urllist}
                    report_list.append(reportdict)
                 
                resultdata = jsonify(report = report_list, result = "Success")
                return resultdata
            else:
                return jsonify(report = report_list, result = "Success")
        else :
            sql = "select * from report inner join team where report.t_num = team.t_num and report.r_year = '"+str(r_year)+"' and report.r_month = '"+str(r_month)+"'"
            result = cur.execute(sql)
            reportdata = cur.fetchall()
            report_list = []
           
            if result != 0:
                for data in reportdata:
                    sql = "select report_photo.r_photourl from report inner join report_photo where report_photo.report_num = '"+str(data[0])+"' and report.report_num = '"+str(data[0])+"'"
                    cur.execute(sql)
                    urldata = cur.fetchall()
                    urllist = []
                    for u_data in urldata :
                        urldict = {'photo':u_data[0]}
                        urllist.append(urldict)
                                                       
                    reportdict = {"report_num":data[0],"r_year":data[1],"r_month":data[2],"r_day":data[3],"r_starthour":data[4],
                        "r_startmin":data[5],"r_endhour":data[6],"r_endmin":data[7],"people_num":data[8],"contents":data[9],"flag":data[10],
                        "t_num":data[11],"park":data[12],"r_members":data[13],"t_name":data[15],"t_logo":data[16],"photo":urllist}
                    report_list.append(reportdict)
                 
                resultdata = jsonify(report = report_list, result = "Success")
                return resultdata
            else:
                return jsonify(report = report_list, result = "Success") 

    else:
        return jsonify(result = "Failed")

@app.route('/signout',methods=['POST','GET'])
def signout():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        u_id = request.values['u_id']

        #foreign 키 무시하고 삭제하기
        sql = "set foreign_key_checks = 0"
        cur.execute(sql)
        
        sql = "delete from user where u_id = '"+str(u_id)+"'"
        result = cur.execute(sql)

        sql = "set foreign_key_checks = 1"
        cur.execute(sql)

        if result !=0:
            con.commit()
            con.close()
            return "Success"

        else :
            con.close()
            return "Failed"

    else:
        con.close()
        return "Failed"

@app.route('/deletereport',methods=['POST','GET'])
def deletereport():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        report_num = request.values['report_num']

        #sql = "set foreign_key_checks = 0"
        #cur.execute(sql)
        sql = "delete from report_photo where report_num = '"+str(report_num)+"'"
        result1 = cur.execute(sql)
        sql = "delete from report where report_num = '"+str(report_num)+"'"
        result2 = cur.execute(sql)

        if result2 !=0:
            con.commit()
            con.close()
            return "Success"
        else:
            con.close()
            return "Failed"
    else:
        con.close()
        return "Failed"

@app.route('/getadminandteamqna',methods=['POST','GET'])
def getadminandteamqna():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
       
        sql = "select team_board.*,team.t_name from team_board inner join team where team_board.t_num = team.t_num order by b_time desc"
        result = cur.execute(sql)
        if result != 0:
            aat_qnadata = cur.fetchall()
            aat_qnalist = []
            for data in aat_qnadata:
                cur.execute("select count(b_num) from team_board_reply where b_num = '"+str(data[0])+"'")
                count = cur.fetchone()#title,t_name
                aat_qnadict = {"b_num": data[0],"u_id":data[1],"t_num":data[2],"contents":data[3],"title":data[4],"time":str(data[5]), "c_count":count[0], "t_name":data[6]}
                aat_qnalist.append(aat_qnadict)
            resultdata = jsonify(qna = aat_qnalist, result = "Success")
            return resultdata
        else:
            return jsonify(result = "Failed")
    else :
        return jsonify(result = "Failed")

@app.route('/registqna',methods=['POST','GET'])
def registqna():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        u_id = request.values['u_id']
        title = request.values['title']
        content = request.values['content']

        sql = "insert into qna values('"+str(u_id)+"', 0, '"+str(title)+"', '"+str(content)+"', null)"
        result = cur.execute(sql)

        if result !=0:
            con.commit()
            con.close()
            return jsonify(result = "Success")

        else:
            con.close()
            return jsonify(result = "Failed")
    else:
        con.close()
        return jsonify(result = "Failed")

@app.route('/registadminandteamqna',methods=['POST','GET'])
def registadminandteamqna():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        u_id = request.values['u_id']
        t_num = request.values['t_num']
        content = request.values['content']
        title = request.values['title']

        sql = "insert into team_board values(0, '"+str(u_id)+"', '"+str(t_num)+"','"+str(content)+"','"+str(title)+"',null)"
        result = cur.execute(sql)

        if result !=0:
            con.commit()
            con.close()
            return jsonify(result = "Success")

        else:
            con.close()
            return jsonify(result = "Failed")
    else:
        con.close()
        return jsonify(result = "Failed")

@app.route('/registcheerful',methods=['POST','GET'])
def registcheerful():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        u_id = request.values['u_id']
        t_num = request.values['t_num']
        ch_content = request.values['ch_contents']
        ch_photo = request.values['ch_photo']
        
        if str(ch_photo) == "empty":
            sql = "insert into cheerful values(null,'"+str(u_id)+"','"+str(t_num)+"','"+str(ch_content)+"',null,null)"
            result = cur.execute(sql)
            if result !=0:
                con.commit()
                con.close()
                return "Success"
            else:
                con.close()
                return "Failed"
        else:
           
             photourl = "D:/Program Files (x86)/Apache Software Foundation/Apache2.2/htdocs/cheerfulImg/"
             filename = str(photourl)+str(t_num)+"_"+str(datetime.today().strftime("%Y%m%d%H%M%S"))+".jpg"
             in_db_filename = "/cheerfulImg/"+str(t_num)+"_"+str(datetime.today().strftime("%Y%m%d%H%M%S"))+".jpg"
             with open(str(filename), "wb") as img:
                 img.write(base64.b64decode(ch_photo))      
             result = cur.execute("insert into cheerful values(null,'"+str(u_id)+"','"+str(t_num)+"','"+str(ch_content)+"','"+str(in_db_filename)+"',null)")
             con.commit()
             con.close()
             if result != 0:
                return "Success"
             else:
                 return "Failed"

@app.route('/getcheerful',methods=['POST','GET'])
def getcheerful():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        t_num = request.values['t_num']
        lastnum = request.values['lastnum']
        count = int(lastnum)+20

        if int(t_num) != -1:
            sql = "select cheerful.*, team.t_name from cheerful inner join team where cheerful.t_num = team.t_num and team.t_num = '"+str(t_num)+"' and cheerful.t_num = '"+str(t_num)+"' order by c_time desc Limit "+str(lastnum)+","+str(count)+""
            result = cur.execute(sql)
            cheerdata = cur.fetchall()
            cheer_list = []
            

            if result != 0:
                for data in cheerdata:
                    
                    sql = "select count(c_num) from cheerful_reply where c_num = '"+str(data[0])+"'"
                    cur.execute(sql)
                    countdata = cur.fetchone()
                    
                    sql = "select u_permission, u_photo from user where u_id = '"+str(data[1])+"'"
                    cur.execute(sql)
                    cheeruserdata = cur.fetchone()
                    
                    
                    
                                                                                                  
                    cheerdict = {"ch_num":data[0],"u_id":data[1],"t_num":data[2],"ch_content":data[3],"ch_photourl":data[4],
                        "ch_time":str(data[5]),"t_name":data[6],"u_permission":cheeruserdata[0],"u_photo":cheeruserdata[1], "ch_count":countdata[0]}
                    cheer_list.append(cheerdict)
                 
                resultdata = jsonify(cheer = cheer_list, result = "Success")
                return resultdata
            else:
                return jsonify(cheer = cheer_list, result = "Success")
        else :
            sql = "select cheerful.*, team.t_name from cheerful inner join team where cheerful.t_num = team.t_num order by c_time desc Limit "+str(lastnum)+","+str(count)+""
            result = cur.execute(sql)
            cheerdata = cur.fetchall()
            cheer_list = []
            
            if result != 0:
                for data in cheerdata:
                    
                    sql = "select count(c_num) from cheerful_reply where c_num = '"+str(data[0])+"'"
                    cur.execute(sql)
                    countdata = cur.fetchone()
                    
                    sql = "select u_permission, u_photo from user where u_id = '"+str(data[1])+"'"
                    cur.execute(sql)
                    cheeruserdata = cur.fetchone()
                                                                                                                      
                    cheerdict = {"ch_num":data[0],"u_id":data[1],"t_num":data[2],"ch_content":data[3],"ch_photourl":data[4],
                        "ch_time":str(data[5]),"t_name":data[6],"u_permission":cheeruserdata[0],"u_photo":cheeruserdata[1], "ch_count":countdata[0]}
                    cheer_list.append(cheerdict)
                 
                resultdata = jsonify(cheer = cheer_list, result = "Success")
                return resultdata
            else:
                return jsonify(cheer = cheer_list, result = "Success")          

    else:
        return jsonify(result = "Failed")

@app.route('/registphotocontest', methods = ['POST','GET'])
def registerphotocontest():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        jsondata = request.values['photo_obj']
        data = json.loads(jsondata)
        #print(data)
        
        content = data['p_contents']
        t_num = data['t_num']
        u_id = data['u_id']

        sql = "insert into photo_contest values(null,'"+str(t_num)+"','"+str(u_id)+"','"+str(content)+"')"
        result = cur.execute(sql)
        if result ==1:
            photourl = "D:/Program Files (x86)/Apache Software Foundation/Apache2.2/htdocs/photocontestImg/"
            cur.execute("select Max(num) from photo_contest" )
            number = cur.fetchone()          
            jsonphotoarr = data['photo']
            i=0
            for photo in jsonphotoarr:
                filename = str(photourl)+str(number[0])+"_"+str(photo['index'])+".jpg" 
                in_db_filename = "/photocontestImg/"+str(number[0])+"_"+str(photo['index'])+".jpg" 
                with open(str(filename), "wb") as img:
                    img.write(base64.b64decode(photo['photo']))      
                    cur.execute("insert into photo_contest_photourl values('"+str(number[0])+"','"+str(photo['index'])+"','"+str(in_db_filename)+"')")
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

@app.route('/getphotocontest',methods = ['POST','GET'])
def getphotocontest():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()
    
    if request.method == 'GET':
        lastnum = request.values['lastnum']
        count = int(lastnum)+20
        sql = "select photo_contest.*,team.t_name from photo_contest inner join team where photo_contest.t_num = team.t_num order by num desc Limit "+str(lastnum)+","+str(count)+" "
        result = cur.execute(sql)
        contestdata = cur.fetchall()
        contestlist = []
        if result != 0:
            for data in contestdata:
                cur.execute("select url from photo_contest_photourl where num = '"+str(data[0])+"' order by p_index asc")
                photodata = cur.fetchall()
                photodict = []
        
                for p_data in photodata:
                    print(p_data)
                    photoobj = {'photo':p_data[0]}
                    photodict.append(photoobj)

                jsonnoticedata = {"p_num":data[0],"t_num":data[1], "u_id":data[2],"p_contents":data[3],"t_name":data[4],"photo":photodict}
                contestlist.append(jsonnoticedata)
       
            resultdata = jsonify(contestlist = contestlist, result = "Success")
    
            return resultdata
        else:
            return jsonify(result = "Failed")
    else:
        return jsonify(result = "Failed")

@app.route('/registteamgallery',methods = ['POST','GET'])
def registteamgallery():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        t_num = request.values['t_num']
        tg_photo = request.values['tg_photo']

        photourl = "D:/Program Files (x86)/Apache Software Foundation/Apache2.2/htdocs/teamgalleryImg/"
        filename = str(photourl)+str(t_num)+"_"+str(datetime.today().strftime("%Y%m%d%H%M%S"))+".jpg"
        in_db_filename = "/teamgalleryImg/"+str(t_num)+"_"+str(datetime.today().strftime("%Y%m%d%H%M%S"))+".jpg"
        with open(str(filename), "wb") as img:
             img.write(base64.b64decode(tg_photo))      
        result = cur.execute("insert into team_gallery values(null,'"+str(t_num)+"','"+str(in_db_filename)+"')")
        con.commit()
        con.close()
        if result != 0:
           return "Success"
        else:
            return "Failed" 
    else:
        return "Failed"

@app.route('/getteamgallery',methods = ['POST','GET'])
def getteamgallery():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
        lastnum = request.values['lastnum']
        t_num = request.values['t_num']
        count = int(lastnum)+20
        sql = "select * from team_gallery where t_num = '"+str(t_num)+"' order by num desc Limit "+str(lastnum)+","+str(count)+" "
        result = cur.execute(sql)
        gallerydata = cur.fetchall()
        gallerylist = []
        if result !=0:
            for data in gallerydata:
                jsongallerydata = {"num":data[0],"t_num":data[1],"photo":data[2]}
                gallerylist.append(jsongallerydata)
       
            resultdata = jsonify(gallerylist = gallerylist, result = "Failed")
    
            return resultdata
        else:
            return jsonify(result = "Failed")

    else:
        return jsonify(result = "Failed")


@app.route('/main',methods= ['POST','GET'])
def mainhome():
    con = mysql.connect(host = 'localhost', port = 5000, user = 'root', passwd = 'cjy12120', db = 'hangang', charset = 'utf8')
    cur = con.cursor()

    if request.method == 'GET':
         sql = "select * from notice order by n_num desc Limit 0,3"
         cur.execute(sql)
         noticedata = cur.fetchall()
         noticelist = []
    
         for data in noticedata:
            cur.execute("select n_photo_url from notice_photo where n_num = '"+str(data[0])+"' order by n_index asc")
            photodata = cur.fetchall()
            photodict = []
        
            for p_data in photodata:
                print(p_data)
                photoobj = {'photo':p_data[0]}
                photodict.append(photoobj)


            cur.execute(" select count(n_num) from notice_comment where n_num = '"+str(data[0])+"'")
            comment_num = cur.fetchone()
            jsonnoticedata = {"num":data[0],"title":data[1], "content":data[2],"type":data[3],"time":str(data[4]),"photo":photodict,"commentnum":comment_num[0]}
            noticelist.append(jsonnoticedata)


         year = request.values['year']
         month = request.values['month']
         day = request.values['day']
         nextday = int(day)+1
         sql = "select schedules.*,team.t_logo,team.t_name from schedules inner join team where team.t_num =schedules.t_num and s_year = '"+str(year)+"' and s_month = '"+str(month)+"' and s_day = '"+str(day)+"' order by schedules.s_park"
         result = cur.execute(sql)
         s_data = cur.fetchall()

         schedulelist = []
         if result != 0:
            for data in s_data :
                scheduledict =  {"s_num":data[0],"s_year":data[1],"s_month":data[2],"s_day":data[3],"start_hour":data[4],
                                "start_min":data[5],"end_hour":data[6],"end_min":data[7],"t_num":data[8],"s_lat":data[9],"s_long":data[10],
                                "s_park":data[11],"flag":data[12],"car_num":data[13],"t_logo":data[14],"t_name":data[15]}
                schedulelist.append(scheduledict)


         sql = "select realtime_schedules.*, t_logo, t_name from realtime_schedules inner join team where realtime_schedules.t_num = team.t_num and flag = 1 order by realtime_schedules.s_park"
         result = cur.execute(sql)
         realtimedata = cur.fetchall()
         r_list = []
        
         if result != 0:
            for data in realtimedata:
                realtimedict = {"r_num":data[0],"r_year":data[1],"r_month":data[2],"r_day":data[3],"start_hour":data[4],
                    "start_min":data[5],"end_hour":data[6],"end_min":data[7],"t_num":data[8],"r_lat":data[9],"r_long":data[10],
                    "r_park":data[11],"flag":data[12],"t_logo":data[13],"t_name":data[14]}
                r_list.append(realtimedict)


         sql = "select photo_contest.*,team.t_name from photo_contest inner join team where photo_contest.t_num = team.t_num order by num desc Limit 0,6 "
         result = cur.execute(sql)
         contestdata = cur.fetchall()
         contestlist = []

         if result != 0:
            for data in contestdata:
                cur.execute("select url from photo_contest_photourl where num = '"+str(data[0])+"' order by p_index asc")
                photodata = cur.fetchall()
                photodict = []
        
                for p_data in photodata:
                    print(p_data)
                    photoobj = {'photo':p_data[0]}
                    photodict.append(photoobj)

                jsonnoticedata = {"p_num":data[0],"t_num":data[1], "u_id":data[2],"p_contents":data[3],"t_name":data[4],"photo":photodict}
                contestlist.append(jsonnoticedata)


        
         return jsonify(noticelist = noticelist, contestlist=contestlist, realtimelist = r_list, schedulelist =  schedulelist)
    else:
         return jsonify(result = "Success")
            

         


            
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




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
    

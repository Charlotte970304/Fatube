from flask import Flask, render_template,request,redirect,url_for
import os,io,time,copy
from PIL import Image
from flask_mail import Mail,Message


root=False
app = Flask(__name__)



def fill_images(photo):

    """ 填充正方形白色背景圖片 """
    width, height = photo.size # 獲取圖片的寬高
    side = max(width, height) # 對比寬和高哪個大
    # 新生成的圖片是正方形的,邊長取大的,背景設置白色
    new_image = Image.new(photo.mode, (side, side), color='white')
    # 根據尺寸不同，將原圖片放入新建的空白圖片中部
    if width > height:
        new_image.paste(photo, (0, int((side - height) / 2)))
    else:
        new_image.paste(photo, (int((side - width) / 2), 0))
    
    new_image = new_image.convert("RGB")
    return new_image

@app.route('/')
def index():

    if root:
        login='yes'
        return render_template('index.html',login=login)
    else:
        login='no'
        return render_template('index.html',login=login)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    global root
    alert=""
    if request.method == 'POST': 
        if request.values['username']=="root" and request.values['password']=="0000" :
            root=True
            return redirect(url_for('index'))
        else:
            alert='Wrong ID or Password'            
    return render_template('login.html',alert=alert)

@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    global root
    if request.method == 'POST': 
        if request.values['logout'] == 'Yes':
            root=False

        return redirect(url_for('index'))
    return render_template('logout.html')

@app.route('/upload', methods=['POST', 'GET'])
def upload():

    dirs=os.listdir(os.path.join(os.path.dirname(__file__), 'static\\uploads'))
    dirs.insert(0,'New Folder')
    dirs.insert(0,'Not Choose')

    if request.method == 'POST':
        flist = request.files.getlist("file[]")

        for f in flist:
            basepath = os.path.dirname(__file__)
            format=f.filename[f.filename.index('.'):]
            fileName=time.time()
            if format in ('.jpg','.png','.jpeg','.HEIC','.jfif'):
                format='.jpg'
            else:
                format='.mp4'
                

            if request.values['folder']=='0':
                return render_template('upload.html',alert='Please choose a folder or creat a folder',dirs=dirs)

            elif request.values['folder']=='1':
                if not os.path.isdir(os.path.join(basepath, 'static\\uploads\\'+request.values['foldername'])):
                    os.mkdir(os.path.join(basepath, 'static\\uploads\\'+request.values['foldername']))
                    os.mkdir(os.path.join(basepath, 'static\\uploads\\'+request.values['foldername'])+'\\video')
                    os.mkdir(os.path.join(basepath, 'static\\uploads\\'+request.values['foldername'])+'\\photo')
                    os.mkdir(os.path.join(basepath, 'static\\uploads\\'+request.values['foldername'])+'\\album')

                if format == '.mp4':
                    upload_path = os.path.join(basepath, 'static\\uploads\\'+request.values['foldername']+'\\video\\'+str(fileName).replace('.','')+str(format))
                else:
                    upload_path = os.path.join(basepath, 'static\\uploads\\'+request.values['foldername']+'\\photo\\'+str(fileName).replace('.','')+str(format))
                    album_path = os.path.join(basepath, 'static\\uploads\\'+request.values['foldername'],'album',str(fileName).replace('.','')+str(format))   
            else:
                if format == '.mp4':
                    upload_path = os.path.join(basepath, 'static\\uploads\\'+dirs[int(request.values['folder'])],'video',str(fileName).replace('.','')+str(format))
                else:
                    upload_path = os.path.join(basepath, 'static\\uploads\\'+dirs[int(request.values['folder'])],'photo',str(fileName).replace('.','')+str(format))
                    album_path = os.path.join(basepath, 'static\\uploads\\'+dirs[int(request.values['folder'])],'album',str(fileName).replace('.','')+str(format))

            if format!='.mp4':
                image = Image.open(f)
                image = image.convert("RGB")
                image.save(upload_path)
                image=fill_images(image)
                image.save(album_path)
            
            else:
                f.save(upload_path)
            
            #f.save(upload_path[:-3]+'png')
        return redirect(url_for('upload'))
    return render_template('upload.html',dirs=dirs)

@app.route('/contact/', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        if request.values['send'] == 'send':
            if request.values['email'] == '':
                return render_template('contact.html',alert="you should fill your email",content=request.values['letter'])
            elif request.values['letter'] == '':
                return render_template('contact.html',alert="Are you kidding?",content="")
            else:
                app.config.update(
                    #  hotmail的設置
                    MAIL_SERVER='smtp.live.com',
                    MAIL_PROT=587,
                    MAIL_USE_TLS=True,
                    MAIL_USERNAME='admin@hotmail.com',
                    MAIL_PASSWORD='password'
                )
                #  記得先設置參數再做實作mail
                mail = Mail(app)

                msg_title = 'Fatube-'+request.values['email']
                msg_sender = 'admin@hotmail.com'
                msg_recipients = ['admin@gmail.com']
                msg_body = request.values['letter']
                
                msg = Message(msg_title,
                      sender=msg_sender,
                      recipients=msg_recipients)
                msg.body = msg_body
                mail.send(msg)
                return render_template('contact.html',alert="you have send the letter",content="")

    return render_template('contact.html',alert="",content="")


@app.route('/album', methods=['POST', 'GET'])
def album():
    if root:
        login='yes'
    else:
        login='no'

    dirs=os.listdir(os.path.join(os.path.dirname(__file__), 'static\\uploads'))
    dirs.insert(0,'ALL')
    dirs.insert(0,'')

    dict2={} #record all folder has what number name

    for dir in dirs:
        if dir == "ALL" or dir == '':
            continue
        dict2[dir]={'photo':[],'video':[]}
        path=os.path.join(os.path.dirname(__file__), 'static\\uploads\\'+dir+'\\photo')
        for lists in os.listdir(path):
            dict2[dir]['photo'].append(lists)
        
        path=os.path.join(os.path.dirname(__file__), 'static\\uploads\\'+dir+'\\video')
        for lists in os.listdir(path):
            dict2[dir]['video'].append(lists)
        
    if request.method == 'POST':


        if request.values['folder']:
            print('yes')
        else:
            print('no')
        if request.values['edit'] == 'edit':
            return render_template('album.html',dirs=dirs,login=login, \
                filefolder=dirs[2:],files=dict2,edit=True)
        elif request.values['delete'] == 'delete':
            flist = request.form.getlist("delete_box")
            for f in flist:
                muru=f[:f.index('-')]
                name=f[f.index('-')+1:f.index('#')]
                format=f[f.index('#')+1:]
                if format == "video":
                    os.remove(os.path.join(os.path.dirname(__file__), 'static\\uploads\\'+muru,'video',name))
                else:
                    os.remove(os.path.join(os.path.dirname(__file__), 'static\\uploads\\'+muru,'photo',name))
                    os.remove(os.path.join(os.path.dirname(__file__), 'static\\uploads\\'+muru,'album',name))

                dict1={} #record all folder has what number name
                for dir in dirs:
                    if dir == "ALL" or dir == '':
                        continue
                    dict1[dir]={'photo':[],'video':[]}
                    path=os.path.join(os.path.dirname(__file__), 'static\\uploads\\'+dir+'\\photo')
                    for lists in os.listdir(path):
                        dict1[dir]['photo'].append(lists)
                    
                    path=os.path.join(os.path.dirname(__file__), 'static\\uploads\\'+dir+'\\video')
                    for lists in os.listdir(path):
                        dict1[dir]['video'].append(lists)

            return render_template('album.html',dirs=dirs,login=login, \
                filefolder=dirs[2:],files=dict1,edit=True)
        elif request.values['delete'] == 'cancel':
            return render_template('album.html',dirs=dirs,login=login, \
                filefolder=dirs[2:],files=dict2,edit=False)

        if request.values['folder']=='1' or request.values['folder']=='0':
            return render_template('album.html',dirs=dirs,login=login,files=dict2, filefolder=dirs[2:],edit=False)
        else:
            return render_template('album.html',dirs=dirs,login=login, \
                filefolder=[dirs[int(request.values['folder'])]],files=dict2,edit=False)
        

        
    return render_template('album.html',dirs=dirs,login=login, \
        files=dict2, filefolder=dirs[2:],edit=False)

@app.route('/photo/<folder>/<id>', methods=['POST', 'GET'])
def photo(folder,id):
    if root:
        login='yes'
    else:
        login='no'

    basepath = os.path.dirname(__file__)
    dirs=os.listdir(os.path.join(os.path.dirname(__file__), 'static\\uploads'))
    for dir in dirs:
        if len(os.listdir(os.path.join(basepath, 'static\\uploads\\'+dir,'photo')))==0:
            dirs.remove(dir)
    dirs.insert(0,'')

    fileName=[]
    for lists in os.listdir(os.path.join(basepath, 'static\\uploads\\'+folder,'photo')):
        sub_path = os.path.join(os.path.join(basepath, 'static\\uploads\\'+folder,'photo'), lists)
        if os.path.isfile(sub_path):
            fileName.append(lists[:lists.index('.')])

    if request.method == 'POST':
        if request.values['folder'] != '0':
            folder=dirs[int(request.values['folder'])]
            fileName.clear()
            for lists in os.listdir(os.path.join(basepath, 'static\\uploads\\'+folder,'photo')):
                sub_path = os.path.join(os.path.join(basepath, 'static\\uploads\\'+folder,'photo'), lists)
                if os.path.isfile(sub_path):
                    fileName.append(lists[:lists.index('.')])
            id=fileName[0]
        elif request.values['nextphoto'] == 'Last':
            id=fileName[(fileName.index(id))-1]
        elif request.values['nextphoto'] == 'Next':
            id=fileName[(fileName.index(id))+1]
        return redirect(url_for('photo',id=id,folder=folder))
    return render_template('photo.html',login=login,dirs=dirs,id=id,folder=folder,fileName=fileName)

@app.route('/video/<folder>/<id>', methods=['POST', 'GET'])
def video(folder,id):
    if root:
        login='yes'
    else:
        login='no'

    basepath = os.path.dirname(__file__)
    dirs=os.listdir(os.path.join(os.path.dirname(__file__), 'static\\uploads'))
    for dir in dirs:
        if len(os.listdir(os.path.join(basepath, 'static\\uploads\\'+dir,'video')))==0:
            dirs.remove(dir)
    dirs.insert(0,'')

    fileName=[]
    for lists in os.listdir(os.path.join(basepath, 'static\\uploads\\'+folder,'video')):
        sub_path = os.path.join(os.path.join(basepath, 'static\\uploads\\'+folder,'video'), lists)
        if os.path.isfile(sub_path):
            fileName.append(lists[:lists.index('.')])

    if request.method == 'POST':
        if request.values['folder'] != '0':
            folder=dirs[int(request.values['folder'])]
            fileName.clear()
            for lists in os.listdir(os.path.join(basepath, 'static\\uploads\\'+folder,'video')):
                sub_path = os.path.join(os.path.join(basepath, 'static\\uploads\\'+folder,'video'), lists)
                if os.path.isfile(sub_path):
                    fileName.append(lists[:lists.index('.')])
            id=fileName[0]
        elif request.values['nextvideo'] == 'Last':
            id=fileName[(fileName.index(id))-1]
        elif request.values['nextvideo'] == 'Next':
            id=fileName[(fileName.index(id))+1]
        return redirect(url_for('video',id=id,folder=folder))
    return render_template('video.html',login=login,dirs=dirs,id=id,folder=folder,fileName=fileName)



if __name__ == '__main__':
    app.run(debug=True)

import os

from werkzeug import secure_filename

from app import app

def allowed_file(filename):
    #判断文件名是否合法
    #rsplit指从右往左寻找切割，（‘.’,1)表示只切割一次
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload/',methods=['POST'])
def upload_file():
    if request.method == 'POST':
        print(request.files)
        file = request.files['file']
        if file and allowed_file(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        return jsonify({'status':1})

@app.route('/download/<filename>',methods=['GET'])
def download_file(filename):
    if request.method == 'GET':
        return send_from_directory(app.config['UPLOAD_FOLDER'],filename,as_attachment=True)

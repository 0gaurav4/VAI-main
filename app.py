from werkzeug.utils import secure_filename
from model_orm import DataSet
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from flask import Flask,render_template, request, flash, redirect, session,send_file,send_from_directory
import os
from Tasks.textclip import create_video_with_text
from Tasks.audiospeed import adjust_video_volume
from Tasks.backgroundremove import create_video_background_removal
from Tasks.clipextract import create_clip_extractor
from Tasks.videocompress import create_video_compression
from Tasks.stablize import stabilize_video
# from Tasks.objectdetect import process_video
from Tasks.videospeed import change_playback_speed
from Tasks.bluringObj import blur_content_in_video

app = Flask(__name__)
app.secret_key = 'thisisaverysecretkey'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['RESULT_FOLDER'] = 'static/results'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

def opendb():
    engine = create_engine("sqlite:///model.sqlite")
    Session = sessionmaker(bind=engine)
    return Session()

@app.route('/')
def home():
    return render_template('home.html')

def allowed_files(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {"mp4","mp4v"}

@app.route('/uploads', methods=['GET','POST'])
def uploadImage():
    if request.method == 'POST':
        print(request.files)
        if 'file' not in request.files:
            flash('❎ No file uploaded','danger')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('❎ no file selected','danger')
            return redirect(request.url)
        if file and allowed_files(file.filename):
            print(file.filename)
            db = opendb()
            filename = secure_filename(file.filename)
            path = os.path.join(os.getcwd(),"static/uploads", filename)
            print(path)
            file.save(path)
            upload = DataSet(filename=filename,filepath =f"static/uploads/{filename}", datatype = os.path.splitext(file.filename)[1])
            db.add(upload)
            db.commit()
            flash('file uploaded and saved','success')
            session['uploaded_file'] = f"/static/uploads/{filename}"
            return redirect('/dashboard')
        else:
            flash('❎ Wrong file selected, only mp4 files allowed','danger')
            return redirect(request.url)
   
    return render_template('upload.html',title='upload file')


@app.route('/dashboard')
def filelisting():
    db = opendb()
    filelist = db.query(DataSet).all()
    db.close()
    return render_template('dashboard.html', filelist=filelist)

@app.route('/results')
def results():
    list = os.listdir(app.config['RESULT_FOLDER'] or os.getcwd())
    get = request.args.get('filename') and request.args.get('filepath')
    if get:
        list = [x for x in list if get in x]
    list = sorted(list)
    print(list)
    return render_template('results.html', list=list)

@app.route('/edit/<int:id>')
def edit(id):
    db = opendb()
    file = db.query(DataSet).filter(DataSet.id==id).first()
    video = file.filepath
    db.close()
    return render_template('edit.html', id=id, file=video)


@app.route('/path')
def path():
    return render_template('expression')

@app.route('/delete/<int:id>')
def delete(id):
    sess=opendb()
    try:
        sess.query(DataSet).filter(DataSet.id==id).delete()
        sess.commit()
        sess.close()
        return redirect('/dashboard')
        # return render_template('dashboard.html')
    except Exception as e:
        return f" ❎ There was a problem while deleting {e}"
    
@app.route('/file/delete/')
def delete_file():
    if request.args.get('p'):
        path = request.args.get('p')
        if os.path.isfile(path):
            os.remove(path)
        return redirect('/results')
    return redirect('/results')
    
 
@app.route('/edit/add_text_to_video/<int:id>', methods=['POST'])
def create_video_with_text_view(id):
    db  = opendb()
    file = db.query(DataSet).filter(DataSet.id==id).first()
    db.close()
    path, ext = os.path.splitext(file.filepath)
    output_name = request.form.get('output_name') or 'text_overlay'
    start_time = request.form.get('start_time') or 0
    end_time = request.form.get('end_time') or 0
    text = request.form.get('text') or 'Video Editing AI'
    fontsize = request.form.get('fontsize') or 70
    position = request.form.get('position') or 'center'
    color = request.form.get('color') or 'white'
    duration = request.form.get('duration') or 10
    outout_pathT = os.path.join(os.getcwd(),"static","results","text_overlay"+output_name+ext)
    source = os.path.join(os.getcwd(),file.filepath)
    print(f'{source} => {outout_pathT}')
    create_video_with_text(video_path=source, output_name=outout_pathT, start_time=start_time, end_time=end_time, text=text, fontsize=fontsize, position=position, color=color, duration=duration)
    try:
        create_video_with_text(video_path=source, output_name=outout_pathT, start_time=start_time, end_time=end_time, text=text, fontsize=fontsize, position=position, color=color, duration=duration)
        return f'video created successfully : {outout_pathT}'
    except Exception as e:
        print(e)
        return f" ❎ There was a problem while deleting {e}"


@app.route('/edit/stablize/<int:id>', methods=['POST'])
def stablize(id):
    db  = opendb()
    file = db.query(DataSet).filter(DataSet.id==id).first()
    db.close()
    path, ext = os.path.splitext(file.filepath)
    output_name = request.form['output_name']
    outout_path = os.path.join(os.getcwd(),"static","results","stabilized_"+output_name+ext)
    source = os.path.join(os.getcwd(),file.filepath)
    print(f'{source} => {outout_path}')
    try:
        stabilize_video(video_path=source, output_name=outout_path)
        return f'video created successfully : {outout_path}'
    except Exception as e:
        return f" ❎ There was a problem while deleting {e}"

@app.route('/edit/edittrim/<int:id>', methods=['POST'])
def edittrim(id):
    db  = opendb()
    file = db.query(DataSet).filter(DataSet.id==id).first()
    db.close()
    path, ext = os.path.splitext(file.filepath)
    output_name = request.form.get('output_name') or 'clip'
    start_time = request.form.get('start_time') or 0
    end_time = request.form.get('end_time') or 0
    outout_pathT = os.path.join(os.getcwd(),"static","results","clip_extract_"+output_name+ext)
    source = os.path.join(os.getcwd(),file.filepath)
    print(f'{source} => {outout_pathT}')
    try:
        create_clip_extractor(video_path=source, output_name=outout_pathT, start_time=start_time, end_time=end_time)
        return f'video created successfully : {outout_pathT}'
    except Exception as e:
        return f" ❎ There was a problem while deleting {e}"
    
@app.route('/edit/videospeed/<int:id>', methods=['POST'])
def videoSpeed(id):
    db  = opendb()
    file = db.query(DataSet).filter(DataSet.id==id).first()
    db.close()
    path, ext = os.path.splitext(file.filepath)
    output_name = request.form.get('output_name') or 'clip'
    speed = request.form.get('speed') or 2
    outout_pathT = os.path.join(os.getcwd(),"static","results","video_speed_"+output_name+ext)
    source = os.path.join(os.getcwd(),file.filepath)
    print(f'{source} => {outout_pathT}')
    try:
        change_playback_speed(video_path=source, speed_factor=int(speed))
        return f'video created successfully : {outout_pathT}'
    except Exception as e:
        print(e)
        return f" ❎ There was a problem while deleting {e}"
    

@app.route('/edit/audio/<int:id>', methods=['POST'])
def audio(id):
    db  = opendb()
    file = db.query(DataSet).filter(DataSet.id==id).first()
    db.close()
    path, ext = os.path.splitext(file.filepath)
    output_name = request.form['output_name']
    outout_path = os.path.join(os.getcwd(),"static","results","audio_"+output_name+ext)
    source = os.path.join(os.getcwd(),file.filepath)
    print(f'{source} => {outout_path}')
    try:
        adjust_video_volume(video_path=source, output_name=outout_path)
        return f'video created successfully : {outout_path}'
    except Exception as e:
        return f" ❎ There was a problem while deleting {e}"

@app.route('/edit/object/<int:id>', methods=['POST'])
def object(id):
    db  = opendb()
    file = db.query(DataSet).filter(DataSet.id==id).first()
    db.close()
    path, ext = os.path.splitext(file.filepath)
    output_name = request.form['objname']
    outout_path = os.path.join(os.getcwd(),"static","results","object_"+output_name+ext)
    source = os.path.join(os.getcwd(),file.filepath)
    print(f'{source} => {outout_path}')
    try:
        blur_content_in_video(path=source, output_path=outout_path)
        return f'video created successfully : {outout_path}'
    except Exception as e:
        return f" ❎ There was a problem while deleting {e}"

@app.route('/edit/compress/<int:id>', methods=['POST'])
def compress(id):
    db  = opendb()
    file = db.query(DataSet).filter(DataSet.id==id).first()
    db.close()
    path, ext = os.path.splitext(file.filepath)
    output_name = request.form.get('output_name') or 'clip'
    outout_pathT = os.path.join(os.getcwd(),"static","results","compressed_"+output_name+ext)
    source = os.path.join(os.getcwd(),file.filepath)
    print(f'{source} => {outout_pathT}')
    try:
        create_video_compression(video_path=source, output_name=outout_pathT)
        return f'video created successfully : {outout_pathT}'
    except Exception as e:
        return f" ❎ There was a problem while deleting {e}"

@app.route('/edit/background/<int:id>', methods=['POST'])
def background(id):
    db  = opendb()
    file = db.query(DataSet).filter(DataSet.id==id).first()
    db.close()
    path, ext = os.path.splitext(file.filepath)
    output_name = request.form['output_name']
    outout_path = os.path.join(os.getcwd(),"static","results","bg_removed_"+output_name+ext)
    source = os.path.join(os.getcwd(),file.filepath)
    print(f'{source} => {outout_path}')
    try:
        create_video_background_removal(video_path=source, output_name=outout_path)
        return f'video created successfully : {outout_path}'
    except Exception as e:
        return f" ❎ There was a problem while deleting {e}"
    


if __name__ == '__main__':
  app.run(host='127.0.0.1', port=5000, debug=True)





 

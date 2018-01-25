from flask import Flask, request, render_template, redirect, send_file, send_from_directory, escape as flask_encode_html
from PIL import Image, ImageDraw
import os
import glob
import time
from collections import namedtuple

app = Flask('tidepodchallenge', static_url_path='')

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['TEMPLATES_AUTO_RELOAD'] = True

Frame = namedtuple('Frame', 'name, duration')

def extractFrames(inGif, outFolder):
    outFolder = outFolder.rstrip('/')
    files = glob.glob(outFolder + '/*')
    for f in files:
        os.remove(f)

    frame = Image.open(inGif)
    nframes = 0
    frames = []

    while frame:
        frame_name = '%s/%s-%s.gif' % (outFolder, os.path.basename(inGif), nframes)
        frame_duration = frame.info['duration']
        frames.append(Frame(name=frame_name, duration=frame_duration))
        frame.save( frame_name, 'GIF')
        nframes += 1
        try:
            frame.seek( nframes )
        except EOFError:
            break;

    return frames
    # return dict(enumerate(frame_names))

def createNewGif(positions):
    pod = Image.open('static/tidepod.gif').convert('RGBA')
    pod.thumbnail((75, 75), Image.ANTIALIAS)
    frames = sorted(glob.glob('frames/myfile.gif-*'), 
        key=lambda x: int(x.strip('.gif').split('-')[1]))
    processed_frames = []
    i = 0
    for pos, frame in zip(positions, frames):
        img = Image.open(frame).copy().convert('RGBA')
        if pos:
            img.paste(pod, (round(pos['left']), round(pos['top'])) )#, pod)
        processed_frames.append(img)
    first = processed_frames.pop(0)
    filename = f'results/podified-{int(time.time())}.gif'
    first.save(filename, 
        # duration=10,
        # loop=20,
        save_all=True, 
        append_images=processed_frames)
    print(os.path.getsize(filename))
    # print(processed_frames)
    return filename
    # return 'static/gosling.gif'

@app.route('/', methods=['GET'])
def get():
    print('Root')
    print(request)
    try:
        return send_from_directory('static', 'index.html')
    except Exception as e:
        print('Exception: ', e)
        
    # with open('index.html') as file:
        # return file.read()
    # return app.send_static_file('index.html')

@app.route('/static/<file_name>', methods=['GET'])
def static_get(file_name):
    return send_from_directory('static', file_name)

@app.route('/gif', methods=['POST'])
def upload_gif():
    try:
        file = request.files['gif_file']
        file.save('temp/myfile.gif')
        print(file)
        frames = extractFrames('temp/myfile.gif', 'frames/')
    except Exception as e:
        print('oopsies', e)

    # return redirect('/')
    durations = [f.duration for f in frames]

    return render_template('editor.html', 
        split=[f.name for f in frames], 
        average_duration=round(sum(durations) / len(durations)),
        count=len(frames))

@app.route('/frames/<image_path>', methods=['GET'])
def get_image(image_path):
    return send_from_directory('frames', image_path)

@app.route('/results/<image_path>', methods=['GET'])
def get_result(image_path):
    return send_from_directory('results', image_path)

@app.route('/results/', methods=['GET'])
def all_results():
    print(glob.glob('results/*'))
    return render_template('results.html', paths=[x.strip('results/') for x in glob.glob('results/*')])

@app.route('/positions', methods=['POST'])
def new_gif():
    try:
        positions = request.get_json()
        # print('Hello here is what I have', positions)
        return createNewGif(positions)
    except Exception as e:
        print('oopsies', e)

# TODO give them unique names
@app.after_request
def add_header(r):
    print('Hey, we got a request')
    print(r)
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', extra_files=['*'])

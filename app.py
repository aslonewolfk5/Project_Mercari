from flask import Flask, request, jsonify, render_template
import base64, os, tempfile, subprocess
from celery import Celery

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='redis://redis:6379/0',
    CELERY_RESULT_BACKEND='redis://redis:6379/0'
)

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

def save_and_ocr(image_data):
    try:
        image_data = base64.b64decode(image_data)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as img_file:
            img_file.write(image_data)
            img_path = img_file.name
        
        output_path = img_path.replace('.png', '')
        subprocess.run(['tesseract', img_path, output_path], check=True)
        
        with open(f'{output_path}.txt', 'r') as file:
            text = file.read()
        
        os.remove(img_path)
        os.remove(f'{output_path}.txt')
        
        return text
    except Exception as e:
        return str(e)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/image-sync', methods=['POST'])
def image_sync():
    image_data = request.json.get('image_data')
    if image_data:
        text = save_and_ocr(image_data)
        return jsonify({"text": text})
    return jsonify({"error": "No image data provided."}), 400

@celery.task
def ocr_task(image_data):
    return save_and_ocr(image_data)

@app.route('/image', methods=['POST'])
def image():
    image_data = request.json.get('image_data')
    if image_data:
        task = ocr_task.apply_async(args=[image_data])
        return jsonify({"task_id": task.id})
    return jsonify({"error": "No image data provided."}), 400

@app.route('/image/<task_id>', methods=['GET'])
def get_image(task_id):
    task = ocr_task.AsyncResult(task_id)
    if task.state == 'SUCCESS':
        return jsonify({"task_id": task.id, "text": task.result})
    return jsonify({"task_id": task.id, "status": task.state})

if __name__ == '__main__':
    app.run(debug=True)

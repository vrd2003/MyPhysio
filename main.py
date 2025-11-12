from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image

app = Flask(__name__)
CORS(app)

# Load the pre-trained face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def decode_base64_image(base64_string):
    """Decode base64 image string to numpy array"""
    try:
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        img_data = base64.b64decode(base64_string)
        img = Image.open(BytesIO(img_data))
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    except Exception as e:
        raise ValueError(f"Error decoding image: {str(e)}")

def encode_image_to_base64(image):
    """Encode numpy array image to base64 string"""
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode('utf-8')

@app.route('/test', methods=['GET'])
def test_connection():
    """Simple connection test for frontend"""
    return jsonify({
        'status': 'ok',
        'message': 'Flask backend is reachable!',
        'service': 'face-detection'
    })

@app.route('/detect-faces', methods=['POST'])
def detect_faces():
    """Detect faces in uploaded image"""
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400
        
        # Decode the image
        img = decode_base64_image(data['image'])
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        # Draw rectangles
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        processed_image = encode_image_to_base64(img)
        
        face_list = [
            {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)}
            for (x, y, w, h) in faces
        ]
        
        print(f"✅ Faces detected: {len(faces)}")  # Debug output
        
        return jsonify({
            'success': True,
            'faces_count': len(faces),
            'faces': face_list,
            'processed_image': f'data:image/jpeg;base64,{processed_image}'
        })
    
    except Exception as e:
        print(f"❌ Error during detection: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'face-detection'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

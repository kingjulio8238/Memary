import ml, utils 
from flask import Flask, request, jsonify, send_file, render_template, make_response
from flask.helpers import send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import json, os, uuid
import googlemaps

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
google_maps_key = os.getenv("google_maps_key")
gmaps = googlemaps.Client(key=google_maps_key)
           
@app.route('/audio/<filename>', methods=['GET'])
def serve_audio(filename):
    return send_from_directory(os.path.join('./audio_files'), filename, mimetype='audio/wav')

@app.route('/process', methods=['POST'])
def process(): 
  try: 
    question = request.form['question']
    
    if "vision" in question: 
      return handle_vision_question(request)
    elif "location" in question: 
      return handle_location_question(request)
    else: 
      return jsonify({"message": "Question type not recognized."}), 400    
    
  except Exception as e: 
    print(f"Caught exception: {e}")  
    return make_response(jsonify({"error": str(e)}), 400)
  
def handle_vision_question(request): 
  print("Handling vision request ...")
  try: 
    if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
          
    file = request.files['file']
    question = request.form['question']
    
    if file.filename == '':
      print("No file selected")
      return jsonify({"error": "No file selected"}), 400
    
    if file:
      filename = secure_filename(file.filename)
      filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
      file.save(filepath)
      print(f"Saved file to {filepath}")
      
      base64_image = ml.encode_image(filepath)
      
      gpt_response = ml.call_gpt_vision(base64_image, question)
      print("GPT-4 vision response recieved.")
      
      return handle_audio_response(gpt_response)
  
  except Exception as e:
    print(f"Caught exception in handle_vision_question: {e}")
    return jsonify({"error": str(e)}), 500 

def handle_location_question(request): 
  print("Handling location request ...")
  
  try: 
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    print(f"Location recieved: ({latitude}, {longitude})")
    
    if not latitude or not longitude: 
      text = "Location could not be determined."
    else: 
      reverse_geocode_result = gmaps.reverse_geocode((latitude, longitude))
      readable_address = reverse_geocode_result[0]['formatted_address']
    
      text = "Your readable address is" + readable_address  
    
    return handle_audio_response(text)
  
  except Exception as e: 
    print(f"Caught exception in handle_location_question: {e}")
    return jsonify({"error": str(e)}), 500 
  
def handle_audio_response(text): 
  audio_directory = './audio_files'  
  if not os.path.exists(audio_directory):
    os.makedirs(audio_directory)
    
  audio_filename = f"audio_{uuid.uuid4()}.mp3"
  audio_path = os.path.join(audio_directory, audio_filename)
  ml.text_to_speech(text, audio_path)
  print(f"Audio file saved at {audio_path}")
    
  audio_url = request.url_root + "audio/" + audio_filename
  return jsonify({"audio_url": audio_url})

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == "__main__": 
  app.run(debug=True)
  # app.run(host='0.0.0.0', port=5000)

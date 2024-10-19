import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime, timedelta
from flask import Flask, jsonify, Response
import threading
from flask_cors import CORS
recognized_names = []
app = Flask(__name__)
CORS(app, supports_credentials=True)

# Global variables to control camera processing
is_recognition_running = False
camera_active = False
video = None
frame_thread = None

# Load images from the specified folder
def load_images_from_folder(path):
    images = []
    person_names = []
    my_list = os.listdir(path)
    for cu_img in my_list:
        current_img = cv2.imread(f'{path}/{cu_img}')
        if current_img is not None:
            images.append(current_img)
            person_names.append(os.path.splitext(cu_img)[0])
    return images, person_names

# Face encodings for the loaded images
def face_encodings(images):
    encode_list = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)
        if encode:
            encode_list.append(encode[0])
        else:
            print("No face found in the image.")
    return encode_list

# Modify the mark_attendance function to return the name
def mark_attendance(name):
    with open('Attendance.csv', 'a+') as f:
        t_str = datetime.now().strftime('%H:%M:%S')
        d_str = datetime.now().strftime('%d/%m/%Y')
        f.write(f'\n{name},{t_str},{d_str}')
    recognized_names.append(name)  # Add recognized name to the list


# Update the run_recognition function
def run_recognition():
    global is_recognition_running, recognized_names
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    images, person_names = load_images_from_folder('images')
    encode_list_known = face_encodings(images)

    marked_attendance = {}

    while is_recognition_running:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image from camera.")
            break
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces_current_frame = face_recognition.face_locations(frame_rgb)
        encodes_current_frame = face_recognition.face_encodings(frame_rgb, faces_current_frame)

        for encode_face, face_loc in zip(encodes_current_frame, faces_current_frame):
            matches = face_recognition.compare_faces(encode_list_known, encode_face)
            face_dis = face_recognition.face_distance(encode_list_known, encode_face)
            match_index = np.argmin(face_dis)

            if matches[match_index] and face_dis[match_index] < 0.6:  # Adjust threshold as necessary
                     name = person_names[match_index].upper()
                     print(f"Recognized: {name}")

        if name not in marked_attendance:
                    marked_name = mark_attendance(name)
                    marked_attendance[name] = datetime.now()
                    print(f"Attendance marked for: {marked_name}")


# Function to generate video frames
def generate_frames():
    global camera_active
    cap = cv2.VideoCapture(0)
    while camera_active:
        success, frame = cap.read()
        if not success:
            break
        
        # Encode the frame in JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        # Yield the frame in a specific format for video streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/toggle_camera', methods=['POST'])
def toggle_camera():
    global camera_active, video, frame_thread

    # Start or stop the camera
    if camera_active:
        camera_active = False
        if video is not None:
            video.release()  # Release the video capture
            video = None
        if frame_thread is not None:
            frame_thread.join()  # Wait for the frame processing thread to finish
            frame_thread = None
        return jsonify({"camera_active": False, "message": "Camera stopped."})
    else:
        camera_active = True
        frame_thread = threading.Thread(target=generate_frames)
        frame_thread.start()  # Start the frame processing in a separate thread
        return jsonify({"camera_active": True, "message": "Camera started."})

@app.route('/recognize', methods=['POST'])
def recognize():
    global is_recognition_running, recognized_names
    if not is_recognition_running:
        recognized_names.clear()  # Clear previous recognized names
        is_recognition_running = True
        thread = threading.Thread(target=run_recognition)
        thread.start()
        return jsonify({"status": "success", "message": "Recognition started.", "recognized_names": recognized_names})
    else:
        return jsonify({"status": "error", "message": "Recognition is already running."})



if __name__ == "__main__":
    app.run(debug=True)

import cv2
import numpy as np
import serial
import time
import os
import pickle
from datetime import datetime

class ESPFaceAccessControl:
    def __init__(self, serial_port='COM3', baudrate=115200):
        self.face_detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        self.authorized_face = None
        self.authorized_name = "Authorized Person"
        self.is_trained = False
        
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.esp_connected = False
        self.ser = None
        
        self.mode = "waiting"
        self.last_recognition = None
        self.access_granted = False
        
        self.access_count = 0
        self.unknown_count = 0
        
        self.init_serial()
        self.load_authorized_face()
        
        print("System access control started")
        print("Show your face to camera and press L to learn")
        print("Press R to start recognition")
    
    def init_serial(self):
        try:
            self.ser = serial.Serial(self.serial_port, baudrate=115200, timeout=1)
            time.sleep(2)
            self.esp_connected = True
            print(f"Connected to ESP on {self.serial_port}")
            self.send_to_esp("system_ready")
        except Exception as e:
            print(f"ESP connection error: {e}")
            print("Simulation mode activated")
            self.esp_connected = False
    
    def send_to_esp(self, command):
        if self.esp_connected and self.ser and self.ser.is_open:
            try:
                self.ser.write(f"{command}\n".encode())
                print(f"Sent to ESP: {command}")
            except Exception as e:
                print(f"ESP send error: {e}")
        else:
            print(f"Simulation: {command}")
    
    def load_authorized_face(self):
        try:
            if os.path.exists('authorized_face.pkl'):
                with open('authorized_face.pkl', 'rb') as f:
                    face_data = pickle.load(f)
                    self.authorized_face = face_data['face']
                    self.authorized_name = face_data['name']
                    self.is_trained = True
                print(f"Loaded authorized face: {self.authorized_name}")
                
            if os.path.exists('face_model.yml'):
                self.face_recognizer.read('face_model.yml')
                print("Face model loaded")
                
        except Exception as e:
            print(f"Load error: {e}")
            self.authorized_face = None
            self.is_trained = False
    
    def save_authorized_face(self):
        try:
            if self.authorized_face is not None:
                face_data = {
                    'face': self.authorized_face,
                    'name': self.authorized_name,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                with open('authorized_face.pkl', 'wb') as f:
                    pickle.dump(face_data, f)
                
                self.face_recognizer.write('face_model.yml')
                print("Authorized face saved")
                
        except Exception as e:
            print(f"Save error: {e}")
    
    def learn_face(self, face_image):
        try:
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            
            self.authorized_face = gray
            self.authorized_name = "Authorized Person"
            
            faces = [gray]
            labels = [0]
            
            self.face_recognizer.train(faces, np.array(labels))
            self.is_trained = True
            
            self.save_authorized_face()
            
            print("Face memorized!")
            return True
            
        except Exception as e:
            print(f"Learning error: {e}")
            return False
    
    def recognize_face(self, face_image):
        try:
            if not self.is_trained:
                return "not_trained", 100
                
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            label, confidence = self.face_recognizer.predict(gray)
            
            if confidence < 70:
                return "authorized", confidence
            else:
                return "unknown", confidence
                
        except Exception as e:
            print(f"Recognition error: {e}")
            return "error", 100
    
    def detect_faces(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 100),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        return faces
    
    def draw_access_info(self, frame, x, y, w, h, status, confidence=0):
        if status == "authorized":
            color = (0, 255, 0)
            text = "ACCESS GRANTED"
            message = f"Welcome! ({confidence:.1f})"
        elif status == "unknown":
            color = (0, 0, 255)
            text = "ACCESS DENIED"
            message = f"Unknown face ({confidence:.1f})"
        elif status == "learning":
            color = (255, 255, 0)
            text = "LEARNING MODE"
            message = "Memorizing face..."
        else:
            color = (255, 165, 0)
            text = "WAITING"
            message = "Show your face to camera"
        
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 3)
        
        cv2.rectangle(frame, (x, y-35), (x+w, y), color, -1)
        cv2.rectangle(frame, (x, y+h), (x+w, y+h+35), color, -1)
        
        cv2.putText(frame, text, (x+5, y-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.putText(frame, message, (x+5, y+h+25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def process_frame(self, frame):
        faces = self.detect_faces(frame)
        access_status = "waiting"
        
        if len(faces) > 0:
            x, y, w, h = faces[0]
            face_roi = frame[y:y+h, x:x+w]
            
            if self.mode == "learning":
                self.draw_access_info(frame, x, y, w, h, "learning")
                self.learn_face(face_roi)
                self.mode = "waiting"
                access_status = "learning_complete"
                
            elif self.mode == "recognition" and self.is_trained:
                status, confidence = self.recognize_face(face_roi)
                self.draw_access_info(frame, x, y, w, h, status, confidence)
                
                if status == "authorized":
                    access_status = "access_granted"
                    if not self.access_granted:
                        self.access_count += 1
                        self.send_to_esp("access_granted")
                        self.access_granted = True
                else:
                    access_status = "access_denied"
                    if self.access_granted or not self.last_recognition:
                        self.unknown_count += 1
                        self.send_to_esp("access_denied")
                        self.access_granted = False
                
                self.last_recognition = status
                
            else:
                status = "waiting" if not self.is_trained else "ready"
                self.draw_access_info(frame, x, y, w, h, status)
        
        else:
            if self.access_granted:
                self.access_granted = False
                self.send_to_esp("no_face")
        
        return frame, access_status, len(faces)
    
    def start_learning(self):
        self.mode = "learning"
        print("Learning mode: show your face to camera")
    
    def start_recognition(self):
        if self.is_trained:
            self.mode = "recognition"
            print("Recognition mode activated")
        else:
            print("Train the system first! Press L")
    
    def get_status(self):
        return {
            "system_trained": self.is_trained,
            "access_granted": self.access_granted,
            "access_count": self.access_count,
            "unknown_count": self.unknown_count,
            "current_mode": self.mode
        }

def main():
    access_system = ESPFaceAccessControl(serial_port='COM3')
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("Access Control System Commands:")
    print("=" * 50)
    print("L - Learn current face")
    print("R - Start recognition") 
    print("S - Show system status")
    print("C - Clear memory")
    print("Q - Exit")
    print("=" * 50)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Video capture error")
            break
        
        processed_frame, access_status, faces_count = access_system.process_frame(frame)
        
        status_text = f"Mode: {access_system.mode.upper()}"
        if access_system.is_trained:
            status_text += " | Trained"
        else:
            status_text += " | Not trained"
        
        cv2.putText(processed_frame, status_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        stats_text = f"Access: {access_system.access_count} | Denied: {access_system.unknown_count}"
        cv2.putText(processed_frame, stats_text, (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        instruction = "L:Learn R:Recognize S:Status Q:Quit"
        cv2.putText(processed_frame, instruction, (10, 450), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        cv2.imshow('ESP Box Face Access Control', processed_frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('l'):
            access_system.start_learning()
        elif key == ord('r'):
            access_system.start_recognition()
        elif key == ord('s'):
            status = access_system.get_status()
            print("System Status:")
            for key, value in status.items():
                print(f"  {key}: {value}")
        elif key == ord('c'):
            access_system.authorized_face = None
            access_system.is_trained = False
            if os.path.exists('authorized_face.pkl'):
                os.remove('authorized_face.pkl')
            if os.path.exists('face_model.yml'):
                os.remove('face_model.yml')
            print("Memory cleared")
    
    cap.release()
    cv2.destroyAllWindows()
    access_system.save_authorized_face()
    print("System shutdown complete")

if __name__ == "__main__":
    main()

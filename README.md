# ESP Box Face Access Control System

A real-time face recognition access control system with ESP microcontroller integration for physical device control.

## 🌟 Features

- **Real-time Face Detection & Recognition** using OpenCV
- **Single User Training** mode for authorized personnel
- **ESP Integration** via Serial communication
- **Live Video Feed** with visual access status
- **Access Statistics** and event logging
- **Data Persistence** between sessions
- **Simulation Mode** when ESP is unavailable

## 🛠 Technologies Used

- **OpenCV** - Computer vision and image processing
- **Haar Cascade** - Face detection
- **LBPH** (Local Binary Patterns Histograms) - Face recognition
- **PySerial** - ESP communication
- **Pickle** - Data serialization
- **NumPy** - Mathematical operations

## 📋 Prerequisites

- Python 3.6+
- Webcam
- ESP microcontroller (optional)

## 🔧 Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/esp-face-access-control.git
cd esp-face-access-control
```

2. **Install required packages**
```bash
pip install opencv-python numpy pyserial
```

## 🚀 Quick Start

1. **Run the application**
```bash
python face_access_control.py
```

2. **Connect ESP** (optional)
   - Connect your ESP device via USB
   - Update the serial port in the code if needed

3. **Follow on-screen instructions**

## ⌨️ Controls

| Key | Function |
|-----|----------|
| **L** | Learn current face |
| **R** | Start recognition mode |
| **S** | Show system status |
| **C** | Clear memory and trained data |
| **Q** | Quit application |

## 🔌 ESP Integration

### Connection Setup
```python
access_system = ESPFaceAccessControl(serial_port='COM3')  # Your port here
```

### ESP Commands
- `access_granted` - Door unlock trigger
- `access_denied` - Access denied signal
- `system_ready` - System initialization complete
- `no_face` - No face detected

### Wiring Example
```cpp
// ESP32 Example Code
#define RELAY_PIN 2  // Door lock relay

void setup() {
  Serial.begin(115200);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    
    if (command == "access_granted") {
      digitalWrite(RELAY_PIN, HIGH);
      delay(5000);  // Unlock for 5 seconds
      digitalWrite(RELAY_PIN, LOW);
    }
  }
}
```

## 📊 System Modes

### 1. Waiting Mode
- Detects faces without recognition
- Orange frame indicator
- Ready for training or recognition

### 2. Learning Mode
- Train system on authorized face
- Yellow frame indicator
- Press 'L' to activate

### 3. Recognition Mode
- Verifies detected faces
- Green/Red frame for access status
- Press 'R' to activate

## 💾 Data Storage

The system automatically saves:
- `face_model.yml` - Trained recognition model
- `authorized_face.pkl` - Authorized face data

## 🎮 Simulation Mode

When ESP is not connected, the system runs in simulation mode:
- Commands are displayed in console
- Full functionality without hardware
- Perfect for testing and development

## 🔧 Configuration

### Serial Settings
```python
def __init__(self, serial_port='COM3', baudrate=115200):
    # Change according to your setup
```

### Recognition Settings
```python
# Confidence threshold (lower = more strict)
if confidence < 70:
    return "authorized", confidence
```

### Detection Settings
```python
faces = self.face_detector.detectMultiScale(
    gray,
    scaleFactor=1.1,
    minNeighbors=5,
    minSize=(100, 100)
)
```

## 📈 Performance Tips

1. **Lighting**: Ensure good, consistent lighting
2. **Position**: Face should be centered and clearly visible
3. **Distance**: Maintain 1-2 meters from camera
4. **Background**: Use plain background for better accuracy
5. **Training**: Train in the same environment as usage

## 🐛 Troubleshooting

### Camera Issues
```bash
# Check camera detection
python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"
```

### ESP Connection Issues
1. Verify correct COM port
2. Check baud rate (115200)
3. Ensure USB cable supports data transfer
4. Restart ESP device

### Recognition Problems
1. Retrain with better lighting
2. Ensure face is clearly visible
3. Check camera focus
4. Reduce background clutter

## 📝 Usage Example

```python
# Initialize system
access_system = ESPFaceAccessControl(serial_port='COM3')

# Check system status
status = access_system.get_status()
print(f"System trained: {status['system_trained']}")

# Manual training (programmatic)
access_system.start_learning()
```

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a Pull Request

### Planned Features
- Multi-user support
- Web interface
- Mobile app integration
- Cloud synchronization
- Advanced ML models

## 📊 Statistics Tracking

The system maintains:
- Total access grants
- Access denials
- Recognition confidence scores
- System usage patterns

## 🔒 Security Notes

- LBPH is used for local face recognition
- No biometric data is transmitted externally
- All processing happens locally
- Data is stored encrypted on disk

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenCV community for excellent computer vision library
- ESP32 community for microcontroller support
- Contributors and testers

---

**Note**: For production use, consider implementing additional security measures and using more advanced face recognition algorithms.

## 📞 Support

For issues and questions:
1. Check [Troubleshooting](#-troubleshooting) section
2. Open a GitHub Issue
3. Provide system logs and configuration details

---

<div align="center">

**⭐ Star this repo if you find it helpful!**

</div>

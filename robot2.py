# Custom libraries
# from library.motor_control import Motor

# Web server imports
from flask import Flask, Response, send_file, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

# Camera Imports
from picamera2 import Picamera2
from libcamera import controls
import cv2

# Others
from datetime import datetime
import threading

# Init Web app
app = Flask(__name__)
CORS(app, resource={r"/*": {"origin": "*"}})
socketio = SocketIO(app)

# Init Camera
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
picam2.set_controls({"AfMode":controls.AfModeEnum.Continuous})

# To manage the streaming state
clients = 0
streaming = False
lock = threading.Lock()

# Init Motor information
# motor = Motor()
motor_states = [0, 0]
servo_states = [0, 0]

motor_commands = {
    'up': [1, 1],
    'down': [-1, -1],
    'left': [-1, 1],
    'right': [1, -1],
    'upleft': [0, 1],
    'upright': [1, 0],
    'downleft': [-1, 0],
    'downright': [0, -1],
    'stop': [0, 0],
}

sevo_commands = {
    'up': [1, 0],
    'down': [-1, 0],
    'left': [0, 1],
    'right': [0, -1],
    'upleft': [1, 1],
    'upright': [1, -1],
    'downleft': [-1, 1],
    'downright': [-1, -1],
    'stop': [0, 0],
}

servo_keys = {
    'ArrowUp': False,
    'ArrowDown': False,
    'ArrowRight': False,
    'ArrowLeft': False,
}

motor_keys = {
    'w': False,
    'a': False,
    's': False,
    'd': False,
}

key_to_command_map = {
    # w a s d
    (False, False, False, False) : 'stop',
    (False, False, False, True) : 'right',
    (False, False, True, False) : 'down',
    (False, False, True, True) : 'downright',
    (False, True, False, False) : 'right',
    (False, True, True, False) : 'downright',
    (True, False, False, False) : 'up',
    (True, False, False, True) : 'upright',
    (True, True, False, False) : 'upleft', 
}


def get_cpu_temperature():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as file:
            temp = file.read()
            # Convert the temperature to Celsius
            temp_celsius = float(temp) / 1000.0
            return temp_celsius
    except FileNotFoundError:
        return "Could not read CPU temperature. Make sure you are running this on a Raspberry Pi."


def update_motor_states():
    # global motor_states
    # motor_states = motor_commands.get(command, motor_states)
    # print(f"Updated motor states: {motor_states}")

    # # motor.set_motor_status(motor_states)
    key_state = (
        motor_keys['w'],
        motor_keys['a'],
        motor_keys['s'],
        motor_keys['d'],
    )

    if key_state in key_to_command_map:
        motor_states = key_to_command_map[key_state] 

    return motor_states


def update_servo_states():
    # global servo_states
    # servo_states = servo_commands.get(command, servo_states)
    # print(f"Updated servo states: {servo_states}")

    return servo_states


def generate():
    while True:
        frame = picam2.capture_array()
        # Convert the frame to a format that can be processed
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # frame = add_text_overlay(frame)
        # frame = add_cpu_temperature(frame)

        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')


def add_cpu_temperature(frame):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_color = (255, 255, 255)
    thickness = 2
    line_type = cv2.LINE_AA

    text = f"Cpu temp: {get_cpu_temperature()}C"
    position = (10, 40)
    cv2.putText(frame, text, position, font, font_scale, font_color, thickness, line_type)

    return frame


def add_text_overlay(frame):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_color = (255, 255, 255)
    thickness = 2
    line_type = cv2.LINE_AA

    text = "Live"
    position = (10, 40)
    cv2.putText(frame, text, position, font, font_scale, font_color, thickness, line_type)

    text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    position = (10, 470)
    cv2.putText(frame, text, position, font, font_scale, font_color, thickness, line_type)
    
    return frame


@app.route('/motor', methods=['POST'])
def motor_command():
    data = request.get_json()
    command = data.get('command')
    if command:
        updated_states = update_motor_states(command)
        return jsonify({'status': 'success', 'motor_states': updated_states})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid command'}), 400


@app.route('/servo', methods=['POST'])
def servo_command():
    data = request.get_json()
    command = data.get('command')
    if command:
        updated_states = update_servo_states(command)
        return jsonify({'status': 'success', 'motor_states': updated_states})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid command'}), 400


@app.route('/key', methods=['POST'])
def add_command():
    data = request.get_json()
    key = data.get('key')
    if key in servo_keys:
        print(f'Received arrow key : {key}')
        return jsonify({'status': 'success', 'servo_states': servo_states})
    elif key in motor_keys:
        print(f'Received Motor key : {key}')
        return jsonify({'status': 'success', 'motor_states': servo_states})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid key'}), 400


@app.route('/key', methods=['DELETE'])
def remove_command():
    data = request.get_json()
    key = data.get('key')
    if key in servo_keys:
        print(f'Received delete arrow key : {key}')
        return jsonify({'status': 'success', 'servo_states': servo_states})
    elif key in motor_keys:
        print(f'Received deleteMotor key : {key}')
        return jsonify({'status': 'success', 'motor_states': servo_states})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid key'}), 400


@app.route('/video_feed')
def video_feed():
    global streaming
    with lock:
        if not streaming:
            picam2.start()
            streaming = True

    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    return send_file('index2.html')


@socketio.on('connect')
def handle_connect():
    global clients
    with lock:
        clients += 1
        print(f"clients: {clients}")


@socketio.on('disconnect')
def handle_disconnect():
    global clients, streaming
    with lock:
        clients -= 1
        print(f"clients: {clients}")
        if clients == 0:
            picam2.stop()
            streaming = False


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

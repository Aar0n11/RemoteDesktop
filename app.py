from flask import Flask, render_template, request, jsonify, send_file
import pyautogui
import io
import mss
import mss.tools

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/move-mouse', methods=['POST'])
def moveMouse():
    print("Raw Request Data:", request.data)

    try:
        data = request.get_json()
        if data is None:
            raise ValueError("Invalid JSON data received.")
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error parsing JSON: {str(e)}'}), 400

    if 'x' not in data or 'y' not in data or 'screenWidth' not in data or 'screenHeight' not in data:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
    
    x = data.get('x')
    y = data.get('y')
    screenWidth = data.get('screenWidth')
    screenHeight = data.get('screenHeight')
    
    hostScreenWidth, hostScreenHeight = pyautogui.size()
    
    scaledX = int((x / screenWidth) * hostScreenWidth)
    scaledY = int((y / screenHeight) * hostScreenHeight)
    
    try:
        pyautogui.moveTo(scaledX, scaledY, duration=0.0, tween=pyautogui.linear)
        print(f"Received data: x={x}, y={y}, scaledX={scaledX}, scaledY={scaledY}")
        return jsonify({'status': 'success', 'message': 'Mouse moved successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error moving mouse: {str(e)}'}), 500

@app.route('/click', methods=['POST'])
def click():
    try:
        pyautogui.click()
        return jsonify({'status': 'success', 'message': 'Click Successful'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error clicking: {str(e)}'}), 500

@app.route('/mousedown', methods=['POST'])
def mouseDown():
    try:
        pyautogui.mouseDown()
        return jsonify({'status': 'success', 'message': 'Mouse button down'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error pressing mouse button: {str(e)}'}), 500

@app.route('/mouseup', methods=['POST'])
def mouseUp():
    try:
        pyautogui.mouseUp()
        return jsonify({'status': 'success', 'message': 'Mouse button up'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error releasing mouse button: {str(e)}'}), 500

@app.route('/scroll', methods=['POST'])
def scroll():
    try:
        data = request.get_json()
        if not data or 'deltaY' not in data:
            return jsonify({'status': 'error', 'message': 'Missing deltaY parameter'}), 400

        deltaY = data['deltaY']
        pyautogui.scroll(deltaY)

        return jsonify({'status': 'success', 'message': f'Scrolled {deltaY} successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error scrolling: {str(e)}'}), 500

@app.route('/key', methods=["POST"])
def key():
    try:
        data = request.get_json()
        if not data or 'key' not in data:
            return jsonify({'status': 'error', 'message': 'Missing key parameter'}), 400

        key_value = data['key']
        pyautogui.press(key_value)

        return jsonify({'status': 'success', 'message': f'Key "{key_value}" pressed successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error pressing key: {str(e)}'}), 500

@app.route('/screenshot')
def screenshot():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        
        from PIL import Image
        img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)

        img_io = io.BytesIO()
        img.save(img_io, format="JPEG", quality=20)
        img_io.seek(0)

    return send_file(img_io, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)

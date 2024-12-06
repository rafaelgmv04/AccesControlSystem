from flask import Flask, request, jsonify,render_template, redirect, url_for
import time
import licenseFile
from ProcessLicense import getLicenseProcess
import os
from collections import Counter
import requests
from dotenv import load_dotenv


app = Flask(__name__)

load_dotenv(dotenv_path="credentials.env")

arduino_ip = os.getenv("ARDUINO_IP")
arduino_port = os.getenv("ARDUINO_PORT")
licensesAPI = []


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        license = request.form.get('license')
        if license not in licenseFile.getLicenses():
            licenseFile.addLicense(license)
            return redirect(url_for('index'))
    return render_template('index.html', licenses=licenseFile.getLicenses())


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        images_dir = 'images'
        os.makedirs(images_dir, exist_ok=True)

        try:
            image = request.data
            if not image:
                return jsonify({'error': 'No image received'}), 400

            # Salva a imagem no disco
            timestamp = int(time.time())
            filename = os.path.join(images_dir, f'received_image_{timestamp}.jpg')

            with open(filename, 'wb') as f:
                f.write(image)

            # Processa a imagem
            process_image(image)
            return jsonify({'message': 'Image successfully received'}), 200

        except Exception as e:
            return jsonify({'Error': str(e)}), 500



'''
This function receives a list of possible licenses and returns the most common sequence of 3 pairs of letters or numbers.

details: the function receives a list of possible licenses, extracts the valid pairs from each license,
concatenates the pairs to form a sequence, and counts which sequence is the most common. If there is a tie, the function returns an empty string.
'''
def alg_to_find_ideal_license(possible_licenses):
    if not possible_licenses:
        return ""

    sequences = []

    for license in possible_licenses:
        pairs = ext_valid_pair(license)
        if len(pairs) == 3:
            sequences.append(''.join(pairs))


    common_sequences = Counter(sequences).most_common(1)
    if common_sequences:
        final_license = common_sequences[0][0]
    else:
        final_license = ""


    if len(final_license) == 6:
        print("Final ideal license:", final_license)
        return final_license
    else:
        print("Was not possible to calculate the final license.")
        return ""


'''
This function receives a license and returns a list of valid pairs.
condition: a valid pair is a pair of letters or a pair of numbers, not a mix of letters and numbers.
'''
def ext_valid_pair(license):
    pairs = []
    for i in range(0, len(license)-1, 2):
        pair = license[i:i+2]
        if (pair[0].isalpha() and pair[1].isalpha()) or (pair[0].isdigit() and pair[1].isdigit()):
            pairs.append(pair)
    return pairs


'''
This function processes the image and sends a command to the Arduino.
'''
def process_image(image):
    global licensesAPI

    try:
        license = getLicenseProcess(image)
        licensesAPI.append(license)

        if len(licensesAPI) == 5:

            matricula = alg_to_find_ideal_license(licensesAPI)
            licensesAPI.clear()

            if matricula and licenseFile.verifyLicense(matricula):

                send_command_to_arduino("open")

            else:
                send_command_to_arduino("denied")

    except Exception as e:

        licensesAPI.clear()
        send_command_to_arduino("error")
        return jsonify({'error': str(e)}), 500


'''
This function sends a command to the Arduino.
'''
def send_command_to_arduino(command):
    try:
        response = requests.post(f"{arduino_ip}/commandGate", data=command)
        if response.status_code == 200:
            print("Command sent successfully!")
        else:
            print(f"Fail sending command to Arduino: {response.status_code}")
    except Exception as e:
        print(f"Error sending command to Arduino: {e}")


    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

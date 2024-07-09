from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file,abort
import os
import time
import serial
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy.signal import find_peaks
import pandas as pd

app = Flask(__name__)

def save_to_excel(name, phone, duration, vatta_bpm, pitta_bpm, kapha_bpm):
    data = {'Name': [name],
            'Phone Number': [phone],
            'Duration of data': [duration],
            'Vatta BPM': [vatta_bpm],
            'Pitta BPM': [pitta_bpm],
            'Kapha BPM': [kapha_bpm]}

    try:
        df = pd.read_excel('data.xlsx')
        df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
    except FileNotFoundError:
        df = pd.DataFrame(data)

    df.to_excel('data.xlsx', index=False)

def collect_data():
    ser = serial.Serial('COM3', 9600)
    time_values = []
    vatta_values = []
    pitta_values = []
    kapha_values = []

    start_time = time.time()
    try:
        while time.time() - start_time < 20:
            data = ser.readline().decode(errors='ignore').strip()
            if data:
                values = data.split(",")
                if len(values) >= 3:
                    try:
                        vatta, pitta, kapha = map(int, values)
                        elapsed_time = time.time() - start_time
                        time_values.append(elapsed_time)
                        vatta_values.append(vatta)
                        pitta_values.append(pitta)
                        kapha_values.append(kapha)
                    except ValueError:
                        # Ignore lines with invalid data
                        continue
    finally:
        ser.close()

    def calculate_bpm(values, time_values):
        peaks, _ = find_peaks(values, height=520)
        peak_times = [time_values[i] for i in peaks]
        if len(peak_times) > 1:
            peak_intervals = [peak_times[i + 1] - peak_times[i] for i in range(len(peak_times) - 1)]
            average_interval = sum(peak_intervals) / len(peak_intervals) if len(peak_intervals) != 0 else 0
            bpm = 60 / average_interval if average_interval != 0 else 0
        else:
            bpm = 0
        return bpm

    vatta_bpm = calculate_bpm(vatta_values, time_values)
    pitta_bpm = calculate_bpm(pitta_values, time_values)
    kapha_bpm = calculate_bpm(kapha_values, time_values)

    return time_values, vatta_values, pitta_values, kapha_values, vatta_bpm, pitta_bpm, kapha_bpm

def create_pdfs(time_values, vatta_values, pitta_values, kapha_values, vatta_bpm, pitta_bpm, kapha_bpm):
    with PdfPages('vatta_readings.pdf') as pdf_vatta:
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.plot(time_values, vatta_values, linewidth=0.5)
        ax.plot([time_values[i] for i in find_peaks(vatta_values, height=520)[0]], 
                [vatta_values[i] for i in find_peaks(vatta_values, height=520)[0]], 
                'ro', markersize=4)
        ax.set_title(f'Vatta Readings (BPM: {vatta_bpm:.2f})', fontsize=16)
        ax.set_xlabel('Time (seconds)', fontsize=14)
        ax.set_ylabel('Analog Value', fontsize=14)
        ax.tick_params(axis='both', which='major', labelsize=12)
        ax.set_ylim(0, 1100)
        ax.grid(True, linestyle='--', linewidth=0.5)
        pdf_vatta.savefig(fig, dpi=300, bbox_inches='tight')
        plt.close()

    with PdfPages('pitta_readings.pdf') as pdf_pitta:
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.plot(time_values, pitta_values, linewidth=0.5)
        ax.plot([time_values[i] for i in find_peaks(pitta_values, height=520)[0]], 
                [pitta_values[i] for i in find_peaks(pitta_values, height=520)[0]], 
                'ro', markersize=4)
        ax.set_title(f'Pitta Readings (BPM: {pitta_bpm:.2f})', fontsize=16)
        ax.set_xlabel('Time (seconds)', fontsize=14)
        ax.set_ylabel('Analog Value', fontsize=14)
        ax.tick_params(axis='both', which='major', labelsize=12)
        ax.set_ylim(0, 1100)
        ax.grid(True, linestyle='--', linewidth=0.5)
        pdf_pitta.savefig(fig, dpi=300, bbox_inches='tight')
        plt.close()

    with PdfPages('kapha_readings.pdf') as pdf_kapha:
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.plot(time_values, kapha_values, linewidth=0.5)
        ax.plot([time_values[i] for i in find_peaks(kapha_values, height=520)[0]], 
                [kapha_values[i] for i in find_peaks(kapha_values, height=520)[0]], 
                'ro', markersize=4)
        ax.set_title(f'Kapha Readings (BPM: {kapha_bpm:.2f})', fontsize=16)
        ax.set_xlabel('Time (seconds)', fontsize=14)
        ax.set_ylabel('Analog Value', fontsize=14)
        ax.tick_params(axis='both', which='major', labelsize=12)
        ax.set_ylim(0, 1100)
        ax.grid(True, linestyle='--', linewidth=0.5)
        pdf_kapha.savefig(fig, dpi=300, bbox_inches='tight')
        plt.close()

    with PdfPages('comparative_readings.pdf') as pdf_comp:
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.plot(time_values, vatta_values, label='Vatta', linewidth=0.5)
        ax.plot(time_values, pitta_values, label='Pitta', linewidth=0.5)
        ax.plot(time_values, kapha_values, label='Kapha', linewidth=0.5)
        ax.set_title('Comparative Readings', fontsize=16)
        ax.set_xlabel('Time (seconds)', fontsize=14)
        ax.set_ylabel('Analog Value', fontsize=14)
        ax.tick_params(axis='both', which='major', labelsize=12)
        ax.set_ylim(0, 1100)
        ax.grid(True, linestyle='--', linewidth=0.5)
        ax.legend()
        pdf_comp.savefig(fig, dpi=300, bbox_inches='tight')
        plt.close()

@app.route('/')
def home():
    try:
        df = pd.read_excel('data.xlsx')
        users = df.to_dict(orient='records')
    except FileNotFoundError:
        users = []
    return render_template('home.html', title='Home', users=users)

@app.route('/start', methods=['POST'])
def start():
    name = request.form['name']
    phone = request.form['phone']
    return render_template('progress.html', title='Data Collection Progress', name=name, phone=phone)

@app.route('/collect_data', methods=['POST'])
def collect_data_route():
    data = request.get_json()
    name = data['name']
    phone = data['phone']

    time_values, vatta_values, pitta_values, kapha_values, vatta_bpm, pitta_bpm, kapha_bpm = collect_data()
    create_pdfs(time_values, vatta_values, pitta_values, kapha_values, vatta_bpm, pitta_bpm, kapha_bpm)

    duration = 20  # Fixed duration of 20 seconds
    save_to_excel(name, phone, duration, vatta_bpm, pitta_bpm, kapha_bpm)

    return jsonify({"status": "completed"})

@app.route('/report')
def report():
    files = ['vatta_readings.pdf', 'pitta_readings.pdf', 'kapha_readings.pdf', 'comparative_readings.pdf']
    return render_template('report.html', title='Report', files=files)

#@app.route('/download/<filename>', methods=['GET'])
#def download_file(filename):
#    return send_file(filename, as_attachment=True)

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    # Construct the full path to the file
    file_path = os.path.join(r'C:\Users\Sumit\Desktop\Prakriti Web App', filename)  # Update 'path/to/your/files' to your actual file directory

    # Check if the file exists
    if not os.path.isfile(file_path):
        abort(404, description="Resource not found")

    try:
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        print(f"Error sending file: {e}")
        abort(500, description="Internal Server Error")

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    if os.path.exists(filename):
        os.remove(filename)
    return redirect(url_for('report'))

if __name__ == '__main__':
    app.run(debug=True)

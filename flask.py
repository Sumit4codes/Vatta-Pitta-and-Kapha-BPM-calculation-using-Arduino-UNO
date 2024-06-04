import serial
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy.signal import find_peaks
import pandas as pd

# Function to save data to Excel
def save_to_excel(name, phone, duration, vatta_bpm, pitta_bpm):
    data = {'Name': [name],
            'Phone Number': [phone],
            'Duration of data': [duration],
            'Vatta BPM': [vatta_bpm],
            'Pitta BPM': [pitta_bpm]}

    try:
        df = pd.read_excel('data.xlsx')
        df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
    except FileNotFoundError:
        df = pd.DataFrame(data)

    df.to_excel('data.xlsx', index=False)


# Configure the serial port
ser = serial.Serial('COM3', 9600)  # Replace 'COM3' with the appropriate port on your system

# Lists to store the data
time_values = []
vatta_values = []
pitta_values = []

# Start time for calculating the elapsed time
start_time = None

try:
    print("Press Ctrl+C to start collecting data...")
    while True:
        pass
except KeyboardInterrupt:
    start_time = time.time()
    print("Collecting data...")

    # Read data from the serial port and store it
try:
    while True:
        data = ser.readline().decode().strip()
        if data:
            values = data.split(",")
            if len(values) >= 2:  # Check if there are enough values
                vatta, pitta = map(int, values)
                elapsed_time = time.time() - start_time
                time_values.append(elapsed_time)
                vatta_values.append(vatta)
                pitta_values.append(pitta)
            else:
                print(f"Ignoring invalid data: {data}")
except KeyboardInterrupt:
    print("Data collection stopped.")
    if start_time is not None:
        collect_time = time.time() - start_time
    else:
        collect_time = 0


# Close the serial port
ser.close()

# Calculate BPM for Vatta
vatta_peaks, _ = find_peaks(vatta_values, height=520)  # Adjust the height parameter as needed
vatta_peak_times = [time_values[i] for i in vatta_peaks]
vatta_peak_intervals = [vatta_peak_times[i + 1] - vatta_peak_times[i] for i in range(len(vatta_peak_times) - 1)]

if vatta_peak_intervals:  # Check if vatta_peak_intervals is not empty
    vatta_average_interval = sum(vatta_peak_intervals) / len(vatta_peak_intervals)
    vatta_bpm = 60 / vatta_average_interval
else:
    vatta_bpm = 0

# Calculate BPM for Pitta
pitta_peaks, _ = find_peaks(pitta_values, height=520)  # Adjust the height parameter as needed
pitta_peak_times = [time_values[i] for i in pitta_peaks]
pitta_peak_intervals = [pitta_peak_times[i + 1] - pitta_peak_times[i] for i in range(len(pitta_peak_times) - 1)]

if pitta_peak_intervals:  # Check if pitta_peak_intervals is not empty
    pitta_average_interval = sum(pitta_peak_intervals) / len(pitta_peak_intervals)
    pitta_bpm = 60 / pitta_average_interval
else:
    pitta_bpm = 0

# Create individual PDFs for Vatta and Pitta
with PdfPages('vatta_readings.pdf') as pdf_vatta:
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(time_values, vatta_values, linewidth=0.5)
    ax.plot(vatta_peak_times, [vatta_values[vatta_peaks[i]] for i in range(len(vatta_peaks))], 'ro', markersize=4)
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
    ax.plot(pitta_peak_times, [pitta_values[pitta_peaks[i]] for i in range(len(pitta_peaks))], 'ro', markersize=4)
    ax.set_title(f'Pitta Readings (BPM: {pitta_bpm:.2f})', fontsize=16)
    ax.set_xlabel('Time (seconds)', fontsize=14)
    ax.set_ylabel('Analog Value', fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.set_ylim(0, 1100)
    ax.grid(True, linestyle='--', linewidth=0.5)
    pdf_pitta.savefig(fig, dpi=300, bbox_inches='tight')
    plt.close()

# Create a comparative PDF for Vatta and Pitta
with PdfPages('comparative_readings.pdf') as pdf_comp:
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(time_values, vatta_values, label='Vatta', linewidth=0.5)
    ax.plot(time_values, pitta_values, label='Pitta', linewidth=0.5)
    ax.set_title('Comparative Readings', fontsize=16)
    ax.set_xlabel('Time (seconds)', fontsize=14)
    ax.set_ylabel('Analog Value', fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.set_ylim(0, 1100)
    ax.grid(True, linestyle='--', linewidth=0.5)
    ax.legend()
    pdf_comp.savefig(fig, dpi=300, bbox_inches='tight')
    plt.close()

# Collect user inputs for Excel file
name = input("Enter your name: ")
phone = input("Enter your phone number: ")
vatta1 = int(vatta_bpm)
pitta1 = int(pitta_bpm)

# Save data to Excel
save_to_excel(name, phone, collect_time, vatta1, pitta1)

print("PDF files created successfully.")

import serial
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy.signal import find_peaks

# Configure the serial port
ser = serial.Serial('COM3', 9600)  # Replace 'COM3' with the appropriate port on your system

# Lists to store the data
time_values = []
analog_values = []

# Start time for calculating the elapsed time
start_time = time.time()

# Read data from the serial port and store it
print("Collecting data...")
while True:
    try:
        data = ser.readline().decode().strip()
        if data:
            value = int(data)
            elapsed_time = time.time() - start_time
            time_values.append(elapsed_time)
            analog_values.append(value)
    except KeyboardInterrupt:
        break

# Close the serial port
ser.close()

# Calculate BPM
peaks, _ = find_peaks(analog_values, height=520)  # Adjust the height parameter as needed
peak_times = [time_values[i] for i in peaks]
peak_intervals = [peak_times[i + 1] - peak_times[i] for i in range(len(peak_times) - 1)]
average_interval = sum(peak_intervals) / len(peak_intervals)
bpm = 60 / average_interval if average_interval != 0 else 0

# Create a PDF file and plot the data
with PdfPages('analog_readings.pdf') as pdf:
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(time_values, analog_values, linewidth=0.5)
    ax.plot(peak_times, [analog_values[peaks[i]] for i in range(len(peaks))], 'ro', markersize=4)
    ax.set_title(f'Analog Readings (BPM: {bpm:.2f})', fontsize=16)
    ax.set_xlabel('Time (seconds)', fontsize=14)
    ax.set_ylabel('Analog Value', fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.set_ylim(0, 1100)
    ax.grid(True, linestyle='--', linewidth=0.5)
    pdf.savefig(fig, dpi=300, bbox_inches='tight')
    plt.close()

print("PDF file 'analog_readings.pdf' created successfully.")
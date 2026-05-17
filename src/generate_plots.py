import os
import numpy as np
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt


def generate_and_save_plots():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_path = os.path.dirname(current_dir)

    wav_path = os.path.join(root_path, "data", "raw", "test_11025hz.wav")
    output_dir = os.path.join(root_path, "docs", "assets")
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(wav_path):
        print(f"Error: Missing raw data file at {wav_path}")
        return

    # Load and process data
    sample_rate, data = wav.read(wav_path)
    if len(data.shape) > 1: data = data[:, 0]
    data_norm = data.astype(np.float64) / np.max(np.abs(data))

    # Extract 1-second snippet for analysis
    chunk = data_norm[0:sample_rate]
    fft_out = np.fft.fft(chunk)
    freqs = np.fft.fftfreq(len(fft_out), 1 / sample_rate)

    pos = freqs > 0
    freqs_pos = freqs[pos]
    mags_pos = np.abs(fft_out[pos])

    # Render Plot Architecture
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))

    # Plot Time Domain snippet (first 50ms)
    ax1.plot(data_norm[:int(sample_rate * 0.05)], color='blue')
    ax1.set_title("Raw Satellite Time-Domain Signal (First 50ms View)")
    ax1.set_xlabel("Samples")
    ax1.set_ylabel("Normalized Amplitude")
    ax1.grid(True)

    # Plot Frequency Domain Spectrum
    ax2.plot(freqs_pos, mags_pos, color='green')
    ax2.axvline(x=2400, color='red', linestyle='--', label='2400Hz Subcarrier target')
    ax2.set_title("Frequency Spectrum (FFT Analysis Window)")
    ax2.set_xlabel("Frequency (Hz)")
    ax2.set_ylabel("Magnitude Peak")
    ax2.set_xlim(0, 5000)
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plot_path = os.path.join(output_dir, "signal_analysis_profile.png")
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"Success: Visual asset saved directly to: {plot_path}")


if __name__ == "__main__":
    generate_and_save_plots()

import numpy as np

class PolarH10SensorModel:
    """
    Simulates a dry-electrode ECG chest strap (Polar H10).
    It ingests the raw simulated heart beats, applies sensor resolution limits,
    adds electrode contact noise, and computes time-domain HRV metrics.
    """
    def __init__(self, noise_std_ms=1.0, dropout_rate=0.005):
        self.noise_std_ms = noise_std_ms
        self.dropout_rate = dropout_rate

    def generate_telemetry(self, raw_time, raw_hc):
        """
        Processes continuous heart rate Hc (bps) to extract beat occurrences (RR intervals).
        """
        beats = []
        t = raw_time[0]
        
        # Identify beat times by integrating Hc over time
        # A beat occurs when the integrated phase reaches 1.0
        phase = 0.0
        for i in range(1, len(raw_time)):
            dt = raw_time[i] - raw_time[i-1]
            hc_avg = (raw_hc[i] + raw_hc[i-1]) / 2.0
            phase += hc_avg * dt
            if phase >= 1.0:
                beats.append(raw_time[i])
                phase -= 1.0
                
        beats = np.array(beats)
        if len(beats) < 2:
            return {"times": np.array([]), "rr": np.array([]), "hr": np.array([])}
            
        # Calculate raw RR intervals in milliseconds
        raw_rr = np.diff(beats) * 1000.0
        beat_times = beats[1:]
        
        # Add dry-electrode contact noise (measurement resolution)
        sensor_noise = np.random.normal(0, self.noise_std_ms, size=len(raw_rr))
        measured_rr = raw_rr + sensor_noise
        
        # Simulate occasional dropout/motion artifact
        mask = np.random.uniform(0, 1, size=len(measured_rr)) > self.dropout_rate
        measured_rr = np.where(mask, measured_rr, np.nan)
        
        # Fill dropouts for clinical HR calculations
        filled_rr = np.copy(measured_rr)
        nan_indices = np.isnan(filled_rr)
        if np.any(nan_indices):
            # Simple forward fill for telemetry display
            last_valid = 1000.0 / raw_hc[0]
            for idx in range(len(filled_rr)):
                if np.isnan(filled_rr[idx]):
                    filled_rr[idx] = last_valid
                else:
                    last_valid = filled_rr[idx]
                    
        measured_hr = 60000.0 / filled_rr
        
        # Compute HRV metrics
        valid_rr = measured_rr[~np.isnan(measured_rr)]
        rmssd = np.sqrt(np.mean(np.diff(valid_rr)**2)) if len(valid_rr) > 1 else 0.0
        sdnn = np.std(valid_rr) if len(valid_rr) > 0 else 0.0
        
        return {
            "times": beat_times,
            "rr_intervals": measured_rr,
            "heart_rate": measured_hr,
            "hrv_rmssd": rmssd,
            "hrv_sdnn": sdnn
        }


class PPGWearableSensorModel:
    """
    Simulates a photoplethysmography (PPG) wristband sensor.
    It generates a synthetic green-light PPG waveform from arterial pressure and blood volume,
    including an AC component (cardiac pulse), a DC component (respiratory and sympathetic perfusion),
    and motion artifacts during tilt transitions.
    """
    def __init__(self, fs=50.0, motion_noise_level=0.15):
        self.fs = fs
        self.motion_noise_level = motion_noise_level

    def generate_ppg_signal(self, time_grid, pau, sympathetic_tone):
        """
        Generates a continuous PPG optical waveform.
        - AC component is proportional to the pulsatile upper arterial pressure (pau).
        - DC component is inversely proportional to sympathetic tone (vasoconstriction reduces blood volume/perfusion).
        - Respiration adds a slow modulation at 0.25 Hz.
        """
        # Interpolate input signals to the sensor sampling grid
        t_sensor = np.arange(time_grid[0], time_grid[-1], 1.0 / self.fs)
        pau_interp = np.interp(t_sensor, time_grid, pau)
        sym_interp = np.interp(t_sensor, time_grid, sympathetic_tone)
        
        # AC Component: cardiac pulse wave
        # Normalize pau to [0, 1] range for cardiac contribution
        p_min, p_max = np.min(pau_interp), np.max(pau_interp)
        if p_max > p_min:
            ac_cardiac = (pau_interp - p_min) / (p_max - p_min)
        else:
            ac_cardiac = np.zeros_like(pau_interp)
            
        # DC Component: sympathetic perfusion baseline (lower sympathetic tone = higher perfusion/amplitude)
        dc_base = 2.0 - 0.8 * sym_interp
        
        # Respiratory Modulation (0.25 Hz, i.e., 15 breaths per minute)
        respiration = 0.05 * np.sin(2 * np.pi * 0.25 * t_sensor)
        
        # Combine components
        raw_ppg = ac_cardiac * 0.2 + dc_base + respiration
        
        # Add High frequency measurement noise
        measurement_noise = np.random.normal(0, 0.005, size=len(t_sensor))
        ppg_signal = raw_ppg + measurement_noise
        
        # Add Motion Artifacts during tilt transition (e.g. around t = 200s for 14 seconds)
        # Create a transient motion envelope
        motion_mask = (t_sensor >= 200.0) & (t_sensor <= 214.0)
        motion_noise = np.random.normal(0, self.motion_noise_level, size=len(t_sensor))
        # Fade in and out motion noise
        fade = np.sin(np.pi * (t_sensor - 200.0) / 14.0)
        ppg_signal = np.where(motion_mask, ppg_signal + motion_noise * fade, ppg_signal)
        
        # Normalize final signal
        ppg_signal = (ppg_signal - np.min(ppg_signal)) / (np.max(ppg_signal) - np.min(ppg_signal))
        
        return t_sensor, ppg_signal

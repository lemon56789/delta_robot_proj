%% Create theta command trajectory for Simscape test
% Units: rad

t_end = 10;          % [s]
dt = 0.02;           % [s]
t = (0:dt:t_end)';

theta_base = pi/4;          % 45 deg
theta_amp  = deg2rad(10);   % +/- 10 deg
freq_hz = 0.2;              % slow motion
omega = 2*pi*freq_hz;

theta_common = theta_base + theta_amp * sin(omega * t);

theta1_cmd = theta_common;
theta2_cmd = theta_common;
theta3_cmd = theta_common;

theta1_ts = timeseries(theta1_cmd, t);
theta2_ts = timeseries(theta2_cmd, t);
theta3_ts = timeseries(theta3_cmd, t);

fprintf("Theta trajectory created: %.1f sec, %.3f sec step\n", t_end, dt);
fprintf("theta range = %.2f deg ~ %.2f deg\n", ...
    rad2deg(min(theta_common)), rad2deg(max(theta_common)));
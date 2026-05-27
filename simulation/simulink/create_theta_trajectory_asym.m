%% Create asymmetric theta command trajectory for Simscape test
% Purpose:
%   Test non-symmetric delta robot platform motion.
%
% Units:
%   time  : s
%   theta : rad
%
% Required output variables:
%   theta1_ts, theta2_ts, theta3_ts
%   t_end, dt

%% Trajectory settings
t_end = 10;          % [s]
dt = 0.02;           % [s]
t = (0:dt:t_end)';

theta_base = pi/4;          % 45 deg nominal posture
theta_amp  = deg2rad(5);    % +/- 5 deg, small amplitude for stable first test
freq_hz = 0.2;              % slow motion
omega = 2*pi*freq_hz;

%% Asymmetric theta commands
theta1_cmd = theta_base + theta_amp * sin(omega*t);
theta2_cmd = theta_base + theta_amp * sin(omega*t + 2*pi/3);
theta3_cmd = theta_base + theta_amp * sin(omega*t + 4*pi/3);

%% Create timeseries for Simulink From Workspace blocks
theta1_ts = timeseries(theta1_cmd, t);
theta2_ts = timeseries(theta2_cmd, t);
theta3_ts = timeseries(theta3_cmd, t);

theta1_ts.Name = "theta1_cmd";
theta2_ts.Name = "theta2_cmd";
theta3_ts.Name = "theta3_cmd";

%% Quick summary
fprintf("Asymmetric theta trajectory created.\n");
fprintf("Duration: %.2f s, dt: %.3f s\n", t_end, dt);
fprintf("theta1 range: %.2f deg ~ %.2f deg\n", ...
    rad2deg(min(theta1_cmd)), rad2deg(max(theta1_cmd)));
fprintf("theta2 range: %.2f deg ~ %.2f deg\n", ...
    rad2deg(min(theta2_cmd)), rad2deg(max(theta2_cmd)));
fprintf("theta3 range: %.2f deg ~ %.2f deg\n", ...
    rad2deg(min(theta3_cmd)), rad2deg(max(theta3_cmd)));
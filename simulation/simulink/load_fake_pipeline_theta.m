%% Load fake pipeline theta commands for Simscape
% Purpose:
%   Read current project CSV contract and create Simulink timeseries inputs.
%
% Required CSV columns:
%   time
%   theta1_cmd
%   theta2_cmd
%   theta3_cmd
%
% Units:
%   time: assumed ms if values are large, converted to seconds
%   theta_cmd: assumed deg, converted to rad

%% User setting: CSV path
csv_path = "C:\Users\ddold\OneDrive\문서\MATLAB\data\fake_pipeline\fake_pipeline_sample_2026-05-25_positive_theta.csv";

%[file, folder] = uigetfile("*.csv", "Select fake pipeline CSV");
%if isequal(file, 0)
%    error("No CSV file selected.");
%end
%csv_path = fullfile(folder, file);

%% Read CSV
T = readtable(csv_path);

required_cols = ["time", "theta1_cmd", "theta2_cmd", "theta3_cmd"];
for c = required_cols
    if ~ismember(c, string(T.Properties.VariableNames))
        error("Missing required column: %s", c);
    end
end

%% Time conversion
time_raw = T.time;

% Project logger time is boot_ms, so convert ms -> s.
% If values already look like seconds, this still can be manually adjusted.
t = (time_raw - time_raw(1)) / 1000;

%% Theta conversion: deg -> rad
%% trajectory.slx 사용시 앞에 - 유지, trajectory_axisfix.slx 사용시 - 제거
theta1_cmd = deg2rad(T.theta1_cmd);
theta2_cmd = deg2rad(T.theta2_cmd);
theta3_cmd = deg2rad(T.theta3_cmd);

%% Create timeseries for Simulink
theta1_ts = timeseries(theta1_cmd, t);
theta2_ts = timeseries(theta2_cmd, t);
theta3_ts = timeseries(theta3_cmd, t);

theta1_ts.Name = "theta1_cmd";
theta2_ts.Name = "theta2_cmd";
theta3_ts.Name = "theta3_cmd";

%% Simulation stop time
t_end = t(end);

%% Summary
fprintf("Loaded fake pipeline CSV:\n");
fprintf("  %s\n", csv_path);
fprintf("Rows: %d\n", height(T));
fprintf("Time range: %.3f s ~ %.3f s\n", t(1), t(end));
fprintf("theta1 range: %.3f deg ~ %.3f deg\n", min(T.theta1_cmd), max(T.theta1_cmd));
fprintf("theta2 range: %.3f deg ~ %.3f deg\n", min(T.theta2_cmd), max(T.theta2_cmd));
fprintf("theta3 range: %.3f deg ~ %.3f deg\n", min(T.theta3_cmd), max(T.theta3_cmd));



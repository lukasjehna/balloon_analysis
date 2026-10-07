## Run analysis
jehn_lu@RMC-070761N:~/projects/raspberrypi/balloon_mission$ uv run -m src.balloon_analysis.background_analysis
from .background_analysis_utils import load_data, choose_file
from balloon_analysis.utility import gyro_analysis, pressure_analysis, temperature_analysis, telemetry_analysis
I have to adjust the imports to relative paths 

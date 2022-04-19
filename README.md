# PCMCI

This repository holds a simple script allowing the PCMCI causal discovery approach to be applied to CSV timeseries data files. The script is additionally written in such a way as to allow it to be easily imported by other scripts within the wider project this work was carried out under (see https://github.com/cognitive-robots/autonomous_driving_observation_based_causal_discovery).

## Prerequisites

The code in this repository was designed to work with Python 3, we offer no guarantees on whether the code will run properly on Python 2 even following conversion by a tool such as 3to2.

In order to use this code, please install tigramite via pip:

    pip3 install tigramite
    
Any other python packages should either be installed by default or included as tigramite prerequisites.

## Run PCMCI

The script takes a CSV timeseries data file with each column describing the values taken by a single variable across time. PCMCI is applied to the data and if desired the discovered causal model is output to a specified file path.

    usage: runPCMCI.py [-h] [--output-file-path OUTPUT_FILE_PATH] [--gpdc] [--linalg-error-throw] [--timeout TIMEOUT] scenario_file_path
    
Parameters:
* scenario_file_path: File path specifying the input scenario file.
* -h: Displays the help message for the script.
* --output-file-path: File path specifying where to output the causal model file if desired.
* --gpdc: Use GPDC for the conditional independence test required for PCMCI. A partial correlation approach is used by default. It isn't recommended to use this as it frequently results in linear algebra exceptions, however this may be due to the nature of the data encountered in the autonomous driving domain.
* --linalg-error-throw: Causes linear algebra errors to reach the shell. By default linear algebra errors are caught and provided an output file path has been specified an empty causal model would be output.
* --timeout: Specifies a timeout in seconds after which the causal discovery approach will be abandoned. If this occurs and an output file path has been specified an empty causal model would be output.

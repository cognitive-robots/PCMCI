#!/usr/bin/python3

import os
import argparse
import csv
import json
import time
import signal
import numpy as np
import tigramite.pcmci as tigpcmci
import tigramite.independence_tests as tigit
import tigramite.data_processing as tigdp

tau_min = 1
tau_max = 100
alpha = 0.05

def timeout_sig_handler(signum, frame):
    raise Exception("Timed out!")

def create_PCMCI_config_file(output_file_path, gpdc=False, linalg_error_throw=False, timeout=0.0):
    output_file_path_dir, _ = os.path.split(output_file_path)
    if not os.path.isdir(output_file_path_dir):
        raise ValueError(f"Output file path parent directory {output_file_path_dir} is not a valid directory")

    if gpdc:
        config = {
            "tau_min": str(tau_min),
            "tau_max": str(tau_max),
            "alpha": str(alpha),
            "cond_ind_test": "gpdc",
            "linear_algebra_errors_throw": str(linalg_error_throw),
            "timeout": str(timeout)
        }
    else:
        config = {
            "tau_min": str(tau_min),
            "tau_max": str(tau_max),
            "alpha": str(alpha),
            "cond_ind_test": "parcorr",
            "linear_algebra_errors_throw": str(linalg_error_throw),
            "timeout": str(timeout)
        }

    with open(output_file_path, 'w') as output_file:
        json.dump(config, output_file)

def runPCMCI(scenario_file_path, output_file_path=None, gpdc=False, linalg_error_throw=False, timeout=0.0):
    if timeout > 0.0:
        signal.signal(signal.SIGALRM, timeout_sig_handler)
        signal.alarm(timeout)

    start_time = time.time()

    try:
        if not os.path.isfile(scenario_file_path):
            raise ValueError(f"Scenario CSV file path {scenario_file_path} is not a valid file")

        if output_file_path is not None:
            output_file_path_dir, _ = os.path.split(output_file_path)
            if not os.path.isdir(output_file_path_dir):
                raise ValueError(f"Output file path parent directory {output_file_path_dir} is not a valid directory")

        with open(scenario_file_path, "r") as input_file:
            csv_reader = csv.DictReader(input_file)
            data_rows = []
            variables = []
            for row in csv_reader:
                data_row = np.zeros(len(row.keys()))
                for (i, key) in enumerate(row.keys()):
                    data_row[i] = row[key]
                    if len(data_rows) == 0:
                        variables.append(key)
                        print(f"Data column {i} is variable '{key}'")
                data_rows.append(data_row)
            data = np.stack(data_rows)

            data_frame = tigdp.DataFrame(data)

            if gpdc:
                conditional_independence_test = tigit.GPDC()
            else:
                conditional_independence_test = tigit.ParCorr()

            pcmci = tigpcmci.PCMCI(dataframe=data_frame, cond_ind_test=conditional_independence_test)

            if linalg_error_throw:
                results = pcmci.run_pcmciplus(tau_min=tau_min, tau_max=tau_max, pc_alpha=alpha)
                pcmci.print_significant_links(p_matrix=results["p_matrix"], val_matrix=results["val_matrix"], alpha_level=alpha)
                links_discovered = pcmci.return_significant_links(pq_matrix=results["p_matrix"], val_matrix=results["val_matrix"], alpha_level=alpha)
                link_dict = links_discovered["link_dict"]
            else:
                try:
                    results = pcmci.run_pcmciplus(tau_min=tau_min, tau_max=tau_max, pc_alpha=alpha)
                    pcmci.print_significant_links(p_matrix=results["p_matrix"], val_matrix=results["val_matrix"], alpha_level=alpha)
                    links_discovered = pcmci.return_significant_links(pq_matrix=results["p_matrix"], val_matrix=results["val_matrix"], alpha_level=alpha)
                    link_dict = links_discovered["link_dict"]
                except np.linalg.LinAlgError:
                    # If a linear algebra error gets thrown then produce an empty set of findings
                    link_dict = [[] for variable in variables]
    except np.linalg.LinAlgError as e:
        raise e
    except Exception as e:
        print(e)
        link_dict = [[] for variable in variables]
    finally:
        signal.alarm(0)


    if output_file_path is not None:
        with open(output_file_path, "w") as output_file:
            json_data = { "variables": {}, "runtime": time.time() - start_time }
            for i in range(len(variables)):
                variable = variables[i]
                json_data["variables"][variable] = { "parents": [] }
                for (j, _) in link_dict[i]:
                    if not variables[j] in json_data["variables"][variable]["parents"]:
                        json_data["variables"][variable]["parents"].append(variables[j])
            json.dump(json_data, output_file)
            print(f"Output results to file path {output_file_path}")

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Attempts causal discovery on a scenario CSV file")
    arg_parser.add_argument("scenario_file_path")
    arg_parser.add_argument("--output-file-path")
    arg_parser.add_argument("--gpdc", action="store_true")
    arg_parser.add_argument("--linalg-error-throw", action="store_true")
    arg_parser.add_argument("--timeout", default=0, type=float)
    args = arg_parser.parse_args()

    runPCMCI(args.scenario_file_path, output_file_path=args.output_file_path, gpdc=args.gpdc, linalg_error_throw=args.linalg_error_throw, timeout=args.timeout)

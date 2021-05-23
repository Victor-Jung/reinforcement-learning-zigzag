from multiprocessing import Process, Queue, cpu_count
import matplotlib.pyplot as plt
import numpy as np
import time
import yaml

#from reinforcement_learning_algo.core.state import TemporalMappingState
from temporal_mapping_optimizer.MCMC import *
from temporal_mapping_optimizer.random_search import *
from temporal_mapping_optimizer.cost_esimator import *
from temporal_mapping_optimizer import loop_type_to_ids, ids_to_loop_type


def mcmc_proba_plot(temporal_mapping_ordering, layer_post, layer, im2col_layer, layer_rounded,
                    spatial_loop_comb, input_settings, mem_scheme, ii_su, spatial_unrolling, opt, load=True):
    
    max_iter = 2200 + 2
    min_iter = 100
    iter_interval = 200
    number_of_sample = 100
    plot_path = "temporal_mapping_optimizer/plots"
    plot_data_path = "temporal_mapping_optimizer/plots_data"
    nn_name = "AlexNet"

    data_filename = "go_prob_AlexNet_S100_I200_R100-2202.yaml"
    
    max_lpf = get_max_lpf_size(layer.size_list_output_print, spatial_unrolling)
    tmo = get_lpf_limited_tmo(layer_post, spatial_unrolling, max_lpf)
    mean_prob_list = []
    probs_list = []

    # YAML Dict
    data = dict(
        proba_list = [],
        number_of_iter = []
    )

    # Get the ""Global Optimum""
    global_optimum, tmo, exec_time = mcmc(tmo, 3000, layer, im2col_layer, layer_rounded, spatial_loop_comb, 
                                        input_settings, mem_scheme, ii_su, spatial_unrolling, opt, plot=False)

    if load:
        with open(plot_data_path + "/" + data_filename) as f:
            data = yaml.safe_load(f)
        probs_list = data["probs_list"]
        mean_prob_list = data["mean_prob_list"]

    else:
        for i in range(min_iter, max_iter, iter_interval):
            go_counter = 0
            prob_list = []
            for s in range(number_of_sample):
                utilization, tmo, exec_time = mcmc(tmo, i, layer, im2col_layer, layer_rounded, spatial_loop_comb, 
                                                input_settings, mem_scheme, ii_su, spatial_unrolling, opt, plot=False)
                if utilization == global_optimum:
                    go_counter += 1
                prob_list.append(utilization)

            mean_prob_list.append(go_counter/number_of_sample)
            probs_list.append(prob_list)
            

            print("For", i, "iter of MCMC, mean proba to reach GO is", go_counter/number_of_sample)

        data["probs_list"] = probs_list
        data["mean_prob_list"] = mean_prob_list
        data["number_of_iter"] = [*range(min_iter, max_iter, iter_interval)]

    iter_range = [*range(min_iter, max_iter, iter_interval)]
    #plt.plot([min_iter - iter_interval, max_iter + iter_interval], [global_optimum, global_optimum], '--', label='go')

    flierprops = dict(marker='x', markerfacecolor='green', markeredgecolor='green')
    plt.boxplot(probs_list, positions = iter_range, widths = np.full(len(iter_range), iter_interval*0.75), flierprops=flierprops)

    plt.title("Reliability of MCMC depending on the number of iteration")
    plt.xlabel("Number of iteration")
    plt.ylabel("Utilization")
    plt.legend(loc='lower right')
    
    # Saving Data
    plt.savefig(plot_path + "/go_prob_" + nn_name + "_S" + str(number_of_sample) + "_I" + str(iter_interval) + "_R" + str(min_iter) + "-" + str(max_iter) + ".png")
    
    if not load:
        with open(plot_data_path + "/go_prob_" + nn_name + "_S" + str(number_of_sample) + "_I" + str(iter_interval) + "_R" + str(min_iter) + "-" + str(max_iter) + ".yaml", 'w') as f:
            yaml.dump(data, f)


def rl_temporal_mapping_optimizer(temporal_mapping_ordering, layer_post, layer, im2col_layer, layer_rounded,
                                  spatial_loop_comb, input_settings, mem_scheme, ii_su, spatial_unrolling):

    print("--------- Simulated Annealing Monte Carlo Markov Chain (SA-MCMC) Temporal Mapping Optimization ---------")

    opt = "utilization"
    number_of_thread = 2

    if opt == "energy":
        optimize("energy", number_of_thread, temporal_mapping_ordering, layer_post, layer, im2col_layer, 
                layer_rounded, spatial_loop_comb, input_settings, mem_scheme, ii_su, spatial_unrolling)

    elif opt == "utilization":
        val, tmo, exec_time = optimize("utilization", number_of_thread, temporal_mapping_ordering, layer_post, layer, im2col_layer, 
                layer_rounded, spatial_loop_comb, input_settings, mem_scheme, ii_su, spatial_unrolling)

    elif opt == "pareto":
        optimize("energy", number_of_thread, temporal_mapping_ordering, layer_post, layer, im2col_layer, 
                layer_rounded, spatial_loop_comb, input_settings, mem_scheme, ii_su, spatial_unrolling)
        optimize("utilization", number_of_thread, temporal_mapping_ordering, layer_post, layer, im2col_layer, 
                layer_rounded, spatial_loop_comb, input_settings, mem_scheme, ii_su, spatial_unrolling)
        optimize("pareto", number_of_thread, temporal_mapping_ordering, layer_post, layer, im2col_layer, 
                layer_rounded, spatial_loop_comb, input_settings, mem_scheme, ii_su, spatial_unrolling)
    
    return val, tmo, exec_time

def optimize(opt, number_of_thread, temporal_mapping_ordering, layer_post, layer, im2col_layer, 
            layer_rounded, spatial_loop_comb, input_settings, mem_scheme, ii_su, spatial_unrolling):

    # Initialize mac costs
    mac_costs = calculate_mac_level_costs(layer, layer_rounded, input_settings, mem_scheme, ii_su)

    exec_time_list = []
    best_value_list = []
    pareto_en_list = []
    pareto_ut_list = []

    if opt == "energy" or opt == "pareto":
        best_value = float('inf')
    elif opt == "utilization":
        best_value = 0

    starting_tmo = get_lpf_tmo(layer_post, spatial_unrolling)
    
    # Launch threads
    worker_list = []
    results_queue = Queue()
    for i in range(0, min(number_of_thread, cpu_count())):
        p = Process(target=mcmc, args=(starting_tmo, 2000, layer, im2col_layer, layer_rounded, 
                    spatial_loop_comb, input_settings, mem_scheme, ii_su, spatial_unrolling, opt, results_queue, 0, False))
        worker_list.append(p)
        p.start()

    # Block while all process are not finished
    for worker in worker_list:
        worker.join()

    # Collect results from the queue and extract the best
    for i in range(0, min(number_of_thread, cpu_count())):
        result = results_queue.get()
        if ((opt == "energy" or opt == "pareto") and result[0] < best_value) or (opt == "utilization" and result[0] > best_value):
            best_value = result[0]
            best_tmo = result[1]
            best_exec_time = result[2]

    if opt == "pareto":
        pareto_en, pareto_ut = get_temporal_loop_estimation(best_tmo, input_settings, spatial_loop_comb, mem_scheme, [im2col_layer, layer_rounded], mac_costs)
        pareto_en_list.append(pareto_en.item())
        pareto_ut_list.append(pareto_ut)
    
    if opt == "energy":
        print("Best Energy :", best_value)
    elif opt == "utilization":
        print("Best Utilization :", best_value)
    elif opt == "pareto":
        print("Best Pareto Score :", best_value)

    print("Best tmo :", best_tmo)
    print("Exec time", best_exec_time)  

    '''# Store result in visualisation_data
    with open("temporal_mapping_optimizer/plots_data/visualisation_data.yaml") as f:
        data_doc = yaml.safe_load(f)

    if opt == "energy":
        data_doc["mcmc_en_list"] = best_value
    elif opt == "utilization":
        data_doc["mcmc_ut_list"] = best_value
    elif opt == "pareto":
        data_doc["mcmc_pareto_list"] = best_value
        data_doc["mcmc_pareto_en_list"] = pareto_en_list
        data_doc["mcmc_pareto_ut_list"] = pareto_ut_list

    su = spatial_loop_comb[0].spatial_loop
    for op in ['W', 'I', 'O']:
        for mem_lv_idx, mem_lv in enumerate(su[op]):
            for loop_idx, loop in enumerate(su[op][mem_lv_idx]):
                if type(loop) is tuple:
                    su[op][mem_lv_idx][loop_idx] = list(loop)

    data_doc["mcmc_exec_time_list"] = exec_time_list
    data_doc["su"] = su
    
    with open("temporal_mapping_optimizer/plots_data/visualisation_data.yaml", "w") as f:
        yaml.dump(data_doc, f)'''

    return best_value, best_tmo, best_exec_time

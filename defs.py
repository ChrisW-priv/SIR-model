from SIR_model import Simulator

PARAMS = {
    'n_agents':1000,
    'sick_agents':50,
    'b_shape':(55,55),
    'beta': .3,
    'gamma': .8,
    'death_risk': .01,
    'disease_spread_distance':2,
    'moving_range':5,
    'time_steps':25
}

def sim(n):
    print('Sim started')
    simulator = Simulator(**PARAMS	, nr=n)
    simulator.start_sim()
    return simulator.file_to_store_data

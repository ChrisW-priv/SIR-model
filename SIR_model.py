import random as rd
from array import array
from concurrent.futures import ThreadPoolExecutor
from time import time


def timer(func):
    def wrapper(*args, **kwargs):
        start = time()
        val = func(*args, **kwargs)
        end = time()

        with open('performance.txt', 'a') as file:
            file.write(f'{func.__name__}\t{end-start}\n')
        if func.__name__ == 'main':
            print(f'It took: {end-start} to execute')

        return val

    return wrapper


class Agent:
    def __init__(self, pos_x=0, pos_y=0, plane_shape=(100, 100), sick=False, moving_range=1):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.plane_shape = plane_shape
        self.moving_range = moving_range
        self.susceptible = not sick
        self.is_sick = sick
        self.moving_range = moving_range
        self.last_change = 0

    def __repr__(self):
        return f"({int(self.pos_x)}, {int(self.pos_y)})"

    def move(self):
        # change position - if new position outside plane - do not let it
        self.pos_x += (rd.random()-0.5) * 2 * self.moving_range
        self.pos_y += (rd.random()-0.5) * 2 * self.moving_range
        self.pos_x = max(0, min(self.pos_x, self.plane_shape[0]))
        self.pos_y = max(0, min(self.pos_y, self.plane_shape[1]))


class Simulator:
    def __init__(self, n_agents=10, plane_shape=(100, 100), sick_agents=1, infection_rate=0.75, recovery_rate=0.75, death_risk=0.1, disease_spread_distance=1, moving_range=1,  time_steps=5, sim_number=1):
        self.n_agents = n_agents
        self.plane_shape = plane_shape

        self.susceptible_agents_count = n_agents - sick_agents
        self.sick_agents_count = sick_agents
        self.recovered_count = 0
        self.death_count = 0

        self.infection_rate = infection_rate
        self.recovery_rate = recovery_rate
        self.death_risk = death_risk
        self.disease_spread_distance = disease_spread_distance
        self.moving_range = moving_range
        self.time_steps = time_steps

        self.sick_agents = []
        self.neighbours_by_coordinate = array('h', [-1, 0, 1])

        self.susceptible_agents_grid = {}

        # we initialise tracking changes in a file:
        self.file_to_store_data = f'Disease spread - Sim nr.{sim_number}.csv'
        self.sim_number = sim_number
        with open(self.file_to_store_data, 'w') as new:
            new.write('Time_step,Susceptible,Infected,Recovered,Dead\n')
            new.write(f'0,{self.susceptible_agents_count},{self.sick_agents_count},0,0,0\n')

    def __repr__(self):
        # parameters of this simulation:
        return f'shape of the plane={self.plane_shape}\nrate of getting sick={self.infection_rate}\n' \
            f'recovery rate={self.recovery_rate}\ndeath risk={self.death_risk}\n' \
            f'disease spread distance={self.disease_spread_distance}\nmoving range={self.moving_range}\n' \
            f'time steps={self.time_steps}'

    def run_sim(self):
        self.create_agents()
        for time_step in range(1, self.time_steps+1):
            stop = self.time_step(time_step)
            if stop:
                return True

    def run_sim_with_visualisation(self):
        import matplotlib.pyplot as plt

        def vis_time_step(time_step):
            with ThreadPoolExecutor() as executor:
                # plot all the susceptible agents
                for key in self.susceptible_agents_grid:
                    for agent in self.susceptible_agents_grid.get(key):
                        x = agent.pos_x
                        y = agent.pos_y
                        executor.submit(plt.scatter(x, y, c='green', edgecolors='none', s=30))

                # plot all the sick agents
                for a in self.sick_agents:
                    executor.submit(plt.scatter(a.pos_x, a.pos_y, c='red', edgecolors='none', s=30))

            offset = 3
            plt.xlim([0-offset, self.plane_shape[0] + offset])
            plt.ylim([0-offset, self.plane_shape[1] + offset])
            plt.savefig(f"./images/state{time_step}.png")
            plt.close('all')

        self.create_agents()
        vis_time_step(0)
        for time_step in range(1, self.time_steps + 1):
            self.time_step(time_step)
            vis_time_step(time_step)

    @timer
    def create_agents(self):
        def create_agent(sick=False):
            agent_properties = {
                'pos_x': (rd.random() * self.plane_shape[0]),
                'pos_y': (rd.random() * self.plane_shape[1]),
                'plane_shape': self.plane_shape,
                'sick': sick,
                'moving_range': self.moving_range
            }
            agent = Agent(**agent_properties)
            if sick:
                self.sick_agents.append(agent)
            else:
                x = agent.pos_x//self.disease_spread_distance
                y = agent.pos_y//self.disease_spread_distance
                block = self.susceptible_agents_grid.get((x, y))
                if block:
                    block.append(agent)
                else:
                    self.susceptible_agents_grid[(x, y)] = [agent]

        for _ in range(self.sick_agents_count):
            create_agent(sick=True)
        for _ in range(self.susceptible_agents_count):
            create_agent(sick=False)

    @timer
    def time_step(self, time_step):
        self.agents_spread_disease(time_step)
        self.agent_dies_or_recovers(time_step)
        self.agents_move()

        if self.sick_agents_count == 0:
            print(f'function stropped at time step: {time_step}, due to lack of sick agents')
            return True

        # tract the changes and store them in the file
        with open(self.file_to_store_data, 'a') as file:
            file.write(f'{time_step},{self.susceptible_agents_count},{self.sick_agents_count},{self.recovered_count},{self.death_count}\n')

    @timer
    def agent_dies_or_recovers(self, time_step):
        def decide_on_agent_dies(agent):
            if rd.random() < self.death_risk:
                self.sick_agents.remove(agent)
                self.death_count += 1
                self.sick_agents_count -= 1
            elif rd.random() < self.recovery_rate:
                self.sick_agents.remove(agent)
                self.recovered_count += 1
                self.sick_agents_count -= 1

        with ThreadPoolExecutor() as executor:
            for sick_agent in self.sick_agents:
                if sick_agent.last_change != time_step:
                    executor.submit(decide_on_agent_dies(sick_agent))

    @timer
    def agents_move(self):
        def move_agent_on_block_grid(agent):
            grid_x = agent.pos_x // self.disease_spread_distance
            grid_y = agent.pos_y // self.disease_spread_distance
            agent.move()
            n_grid_x = agent.pos_x // self.disease_spread_distance
            n_grid_y = agent.pos_y // self.disease_spread_distance

            if grid_x != n_grid_x or grid_y != n_grid_y:
                self.susceptible_agents_grid.get((grid_x, grid_y)).remove(agent)
                block = self.susceptible_agents_grid.get((n_grid_x, n_grid_y))
                if block:
                    block.append(agent)
                else:
                    self.susceptible_agents_grid[(n_grid_x, n_grid_y)] = [agent]

        with ThreadPoolExecutor() as executor:
            # susceptible agents move
            for susceptible_agent in [agent for key in self.susceptible_agents_grid for agent in self.susceptible_agents_grid.get(key)]:
                executor.submit(move_agent_on_block_grid(susceptible_agent))

            # sick agents move
            for sick_agent in self.sick_agents:
                executor.submit(sick_agent.move())

    @timer
    def agents_spread_disease(self, current_step):
        def agent_spreads_disease(sick_agent):
            x1 = sick_agent.pos_x
            y1 = sick_agent.pos_y
            sick_grid_x = x1 // self.disease_spread_distance
            sick_grid_y = y1 // self.disease_spread_distance

            for cell in self.get_all_cells_next_to_cell_block(sick_grid_x, sick_grid_y):
                for susceptible_agent in cell:
                    x2 = susceptible_agent.pos_x
                    y2 = susceptible_agent.pos_y

                    # calculates distance and determines if gets infected or not
                    if ((x2 - x1)**2 + (y2 - y1)**2) <= self.disease_spread_distance**2 and rd.random() <= self.infection_rate:
                        susceptible_agent.last_change = current_step
                        cell.remove(susceptible_agent)
                        self.sick_agents.append(susceptible_agent)
                        susceptible_agent.is_sick = True
                        susceptible_agent.susceptible = False
                        self.sick_agents_count += 1
                        self.susceptible_agents_count -= 1

        with ThreadPoolExecutor() as executor:
            for sick_agent in self.sick_agents:
                if sick_agent.last_change != current_step:
                    executor.submit(agent_spreads_disease(sick_agent))

    def get_all_cells_next_to_cell_block(self, grid_x, grid_y):
        for i in self.neighbours_by_coordinate:
            for j in self.neighbours_by_coordinate:
                new_x = grid_x + i
                new_y = grid_y + j
                yield self.susceptible_agents_grid.get((new_x, new_y), [])


if __name__ == '__main__':
    PARAMS = {
        'n_agents': 100000,
        'plane_shape': (50000, 50000),
        'sick_agents': 10000,
        'infection_rate': 0.5,
        'recovery_rate': 0.5,
        'death_risk': .01,
        'disease_spread_distance': 10,
        'moving_range': 50,
        'time_steps': 25
    }

    with open('performance.txt', 'w') as new:
        pass

    rd.seed(256)
    @timer
    def main():
        simulator = Simulator(**PARAMS)
        simulator.run_sim()

    print('Simulation Initialised!')
    main()
    print('Simulation ended!')

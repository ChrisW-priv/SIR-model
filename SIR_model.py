import random as rd
from concurrent.futures import ThreadPoolExecutor


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

        self.susceptible_agents = []
        self.sick_agents = []

        # we initialise tracking changes in a file:
        self.file_to_store_data = f'Disease spread - Sim nr.{sim_number}.csv'
        self.sim_number = sim_number
        with open(self.file_to_store_data, 'w') as new:
            new.write('Time_step,susceptible,Infected,Recovered,Dead\n')
            new.write(f'0,{self.susceptible_agents_count},{self.sick_agents_count},0,0,0\n')

    def __repr__(self):
        # parameters of this simulation:
        return f'shape of the plane={self.plane_shape}\nrate of getting sick={self.infection_rate}\n' \
            f'recovery rate={self.recovery_rate}\ndeath risk={self.death_risk}\n' \
            f'disease spread distance={self.disease_spread_distance}\nmoving range={self.moving_range}\n' \
            f'time steps={self.time_steps}'

    def start_sim(self):
        self.create_agents()
        for time_step in range(1, self.time_steps+1):
            self.time_step(time_step)

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
                self.susceptible_agents.append(agent)

        for _ in range(self.sick_agents_count):
            create_agent(sick=True)
        for _ in range(self.susceptible_agents_count):
            create_agent(sick=False)

    def time_step(self, time_step):
        self.agents_spread_disease(time_step)
        self.agent_dies_or_recovers()
        self.agents_move()

        # tract the changes and store them in the file
        with open(self.file_to_store_data, 'a') as file:
            file.write(f'{time_step},{self.susceptible_agents_count},{self.sick_agents_count},{self.recovered_count},{self.death_count}\n')

    def agent_dies_or_recovers(self):
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
            for agent in self.sick_agents:
                executor.submit( decide_on_agent_dies(agent) )

    def agents_move(self):
        with ThreadPoolExecutor() as executor:
            for agent in self.susceptible_agents:
                executor.submit(agent.move())
            for agent in self.sick_agents:
                executor.submit(agent.move())

    def agents_spread_disease(self, current_step):
        def agent_spreads_disease(sick_agent):
            x1 = sick_agent.pos_x
            y1 = sick_agent.pos_y
            for agent in self.susceptible_agents:
                x2 = agent.pos_x
                y2 = agent.pos_y

                # calculates distance and determines if gets infected or not
                if sick_agent.last_change != current_step and ((x2 - x1) ** 2 + (y2 - y1) ** 2) <= self.disease_spread_distance**2 and rd.random() < self.infection_rate:
                    agent.last_change = current_step
                    self.susceptible_agents.remove(agent)
                    self.sick_agents.append(agent)
                    agent.susceptible = False
                    agent.is_sick = True
                    self.sick_agents_count += 1
                    self.susceptible_agents_count -= 1

        with ThreadPoolExecutor() as executor:
            for sick_agent in self.sick_agents:
                executor.submit( agent_spreads_disease(sick_agent) )

    def run_sim_with_visualisation(self):
        import matplotlib.pyplot as plt

        def vis_time_step(time_step):
            # Create data
            susceptible_coordinates = [(a.pos_x, a.pos_y) for a in self.susceptible_agents]
            sick_coordinates = [(a.pos_x, a.pos_y) for a in self.sick_agents]

            # Create plot
            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)

            for data in susceptible_coordinates:
                x, y = data
                ax.scatter(x, y, alpha=0.8, c='green', edgecolors='none', s=30)

            for data in sick_coordinates:
                x, y = data
                ax.scatter(x, y, alpha=0.8, c='red', edgecolors='none', s=30)

            plt.savefig(f"./images/state{time_step}.png")
            plt.close(fig)

        self.create_agents()
        for time_step in range(self.time_steps):
            vis_time_step(time_step)
            self.time_step(time_step+1)
        vis_time_step(time_step)


if __name__ == '__main__':
    PARAMS = {
        'n_agents': 1000,
        'plane_shape': (500, 500),
        'sick_agents': 10,
        'infection_rate': .75,
        'recovery_rate': .25,
        'death_risk': .01,
        'disease_spread_distance': 8,
        'moving_range': 100,
        'time_steps': 15
    }
    rd.seed(256)

    print('Simulation Initialised!')
    simulator = Simulator(**PARAMS)
    simulator.run_sim_with_visualisation()
    print('Simulation ended!')

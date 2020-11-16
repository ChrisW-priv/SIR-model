import random as rd
from concurrent.futures import ThreadPoolExecutor
import os


class Agent:
	def __init__(self, pos=(0,0), b_shape=(10,10), sick=False, moving_range=1):
		self.pos = pos
		self.max_x_range = b_shape[0]
		self.max_y_range = b_shape[1]
		self.moving_range = moving_range
		self.susceptible = not sick
		self.is_sick = sick
		self.is_dead = False
		self.recovered = False

	def move(self):
		x = rd.randint(-self.moving_range, self.moving_range)
		y = rd.randint(-self.moving_range, self.moving_range)
		self.pos = ( max(0, min(self.pos[0]+x, self.max_x_range)), max(0, min(self.pos[1]+y, self.max_x_range)) )


class Simulator:
	def __init__(self, n_agents=10, b_shape=(10,10), sick_agents=1, beta=0.75, gamma=0.75, death_risk=0.1, disease_spread_distance=1, moving_range=1,  time_steps=5, nr=1):
		self.n_agents = n_agents
		self.b_shape = b_shape
		
		self.susceptibles = n_agents - sick_agents
		self.sick_agents = sick_agents
		self.recovered=0
		self.dead=0

		self.beta=beta
		self.gamma=gamma
		self.death_risk = death_risk
		self.disease_spread_distance = disease_spread_distance
		self.moving_range=moving_range
		self.time_steps = time_steps

		self.file_to_store_data = f'Disease spread - Sim nr.{nr}.csv'
		self.nr = nr

		self.agents = []

	def __del__(self):
		os.remove(self.file_to_store_data)

	def start_sim(self):
		print('Simulation Started!')

		with open(self.file_to_store_data, 'w') as new:
			new.write('Time_step,Susceptibles,Infected,Recovered,Dead\n')
			new.write(f'0,{self.susceptibles},{self.sick_agents},0,0\n')

		self.crate_agents()	

		for time_step in range(1, self.time_steps+1):
			self.time_step(time_step)

		print('Simulation Finished!')

	def crate_agents(self):
		print('Creating Agents!')

		for _ in range(self.sick_agents):
			agent_properties={
				'pos':(rd.randrange(self.b_shape[0]), rd.randrange(self.b_shape[1])),
				'b_shape':self.b_shape,
				'sick':True,
				'moving_range':self.moving_range,
			}
			agent = Agent(**agent_properties)
			self.agents.append(agent)

		for _ in range(self.susceptibles):
			agent_properties={
				'pos':(rd.randrange(self.b_shape[0]), rd.randrange(self.b_shape[1])),
				'b_shape':self.b_shape,
				'sick':False,
				'moving_range':self.moving_range,
			}
			agent = Agent(**agent_properties)
			self.agents.append(agent)

		print('Done Creating Agents!')

	def time_step(self, time_step):
		print('Sim:', time_step)
		self.agents_die()
		self.agents_recover()
		self.agents_move()
		self.agents_spread_disease()

		with open(self.file_to_store_data, 'a') as file:
			file.write(f'{time_step},{self.susceptibles},{self.sick_agents},{self.recovered},{self.dead}\n')

	def agents_move(self):
		def agent_move(agent):
			if not agent.is_dead and not agent.recovered:
				agent.move()

		with ThreadPoolExecutor() as executor:
			for agent in self.agents:
				executor.submit( agent_move(agent) )

	def agents_die(self):
		def agent_dies(agent):
			if agent.is_sick:
				if rd.random()<self.death_risk:
					agent.is_dead=True
					agent.is_sick=False
					self.dead+=1
					self.sick_agents-=1

		with ThreadPoolExecutor() as executor:
			for agent in self.agents:
				executor.submit( agent_dies(agent) )

	def agents_recover(self):
		def agent_recovers(agent):
			if agent.is_sick:
				if rd.random()<self.gamma:
					agent.recovered=True
					agent.is_sick=False
					self.recovered+=1
					self.sick_agents-=1
		
		with ThreadPoolExecutor() as executor:
			for agent in self.agents:
				executor.submit( agent_recovers(agent) )

	def agents_spread_disease(self):
		def agent_spreads_desease(agent):
			if agent.is_sick:
				cx,cy = agent.pos
				for agent in self.agents:
					x,y = agent.pos
					if agent.susceptible and ((cx-x)**2+(cy-y)**2)<=(self.disease_spread_distance)**2 and rd.random()<self.beta:
						agent.susceptible=False
						agent.is_sick=True
						self.sick_agents+=1
						self.susceptibles-=1

		with ThreadPoolExecutor() as executor:
			for agent in self.agents:
				executor.submit( agent_spreads_desease(agent) )

	def plot_changes(self):
		from pandas import read_csv
		df = read_csv(self.file_to_store_data)
		df.set_index('Time_step', drop=True, inplace=True)

		plot = df.plot.line( color={'Susceptibles':'blue','Infected':'red','Recovered':'green', 'Dead':'black'} )
		fig = plot.get_figure()
		fig.savefig(f"Disease spread - Sim nr.{self.nr}.png")


if __name__ == "__main__":
	sim_properties = {
		'n_agents':250,
		'sick_agents':50,
		'b_shape':(25,25),
		'beta': .65,
		'gamma': .1,
		'death_risk': .05,
		'disease_spread_distance':1,
		'moving_range':5,
		'time_steps':15
	}

	simulator = Simulator(**sim_properties) 
	simulator.start_sim()
	simulator.plot_changes()

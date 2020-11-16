import random as rd

class Agent:
	def __init__(self, pos=(0,0), b_shape=(10,10), sick=False, moving_range=1):
		self.pos = pos
		self.max_x_range = b_shape[0]
		self.max_y_range = b_shape[1]
		self.is_sick = sick
		self.moving_range = moving_range
		self.recovered = False

	def move(self):
		valid = False
		while not valid:
			try:
				x = rd.randrange(self.moving_range)
				y = rd.randrange(self.moving_range)
				assert self.pos[0]+x <= self.max_x_range
				assert self.pos[1]+y <= self.max_y_range
			except AssertionError:
				pass
			else:
				self.pos = ( self.pos[0]+x, self.pos[1]+y )
				valid = True


class Controller:
	def __init__(self, n_agents=10, b_shape=(10,10), sick_agents=1, beta=0.6, gamma=0.6, disease_spread_distance=1,  time_steps=5):
		self.n_agents = n_agents
		self.b_shape = b_shape
		
		self.susceptibles = n_agents - sick_agents
		self.sick_agents = sick_agents
		self.recovered=0

		self.disease_spread_distance = disease_spread_distance
		self.beta=beta
		self.gamma=gamma
		self.time_steps = time_steps
		
		self.agents = []

	def start_sim(self):
		with open('Disease_spread.csv', 'w') as new:
			new.write('Time step,Susceptibles,Infected,Recovered\n')
			new.write(f'0,{self.susceptibles},{self.sick_agents},0\n')

		self.crate_agents()	

		for time_step in range(1, self.time_steps+1):
			self.time_step(time_step)

	def crate_agents(self):
		for _ in range(self.sick_agents):
			agent_properties={
				'pos':(rd.randrange(self.b_shape[0]), rd.randrange(self.b_shape[1])),
				'b_shape':self.b_shape,
				'sick':True,
				'moving_range':1,
			}
			agent = Agent(**agent_properties)
			self.agents.append(agent)

		for _ in range(self.susceptibles):
			agent_properties={
				'pos':(rd.randrange(self.b_shape[0]), rd.randrange(self.b_shape[1])),
				'b_shape':self.b_shape,
				'sick':False,
				'moving_range':1,
			}
			agent = Agent(**agent_properties)
			self.agents.append(agent)

	def agents_move(self):
		for agent in self.agents:
			agent.move()

	def agents_spread_disease(self):
		for agent in self.agents:
			if agent.is_sick:
				cx,cy = agent.pos
				for agent in self.agents:
					x,y = agent.pos
					if not agent.is_sick and not agent.recovered and ((cx-x)**2+(cy-y)**2)**0.5<=self.disease_spread_distance and rd.random()>self.beta:
						agent.is_sick=True
						self.susceptibles-=1
						self.sick_agents+=1

	def agents_recover(self):
		for agent in self.agents:
			if agent.is_sick and rd.random()>self.gamma:
				agent.is_sick=False
				agent.recovered=True
				self.sick_agents-=1
				self.recovered+=1

	def time_step(self, time_step):
		self.agents_move()
		self.agents_spread_disease()
		self.agents_recover()

		with open('Disease_spread.csv', 'a') as file:
			file.write(f'{time_step},{self.susceptibles},{self.sick_agents},{self.recovered}\n')


if __name__ == "__main__":
	sim_properties = {
		'n_agents':10,
		'sick_agents':1,
		'b_shape':(10,10),
		'beta': .6,
		'gamma': .6,
		'disease_spread_distance':1,
		'time_steps':5
	}
	contoller = Controller(**sim_properties) 
	contoller.start_sim()

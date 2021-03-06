import logging

from keras.optimizers import RMSprop
from keras.utils import plot_model
from pyfiction.agents.ssaqn_agent import SSAQNAgent
from pyfiction.simulators.games.machineofdeath_simulator import MachineOfDeathSimulator

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

"""
An example SSAQN agent for Machine of Death (including paraphrased) that uses online learning and prioritized sampling
"""

simulator = MachineOfDeathSimulator(paraphrase_actions=False)
simulator_paraphrased = MachineOfDeathSimulator(paraphrase_actions=True)
# Create the agent and specify maximum lengths of descriptions (in words)
agent = SSAQNAgent(train_simulators=simulator, test_simulators=[simulator, simulator_paraphrased])

# Learn the vocabulary (the function samples the game using a random policy)
agent.initialize_tokens('vocabulary.txt')

optimizer = RMSprop(lr=0.00001)

embedding_dimensions = 16
lstm_dimensions = 32
dense_dimensions = 8

agent.create_model(embedding_dimensions=embedding_dimensions,
                   lstm_dimensions=lstm_dimensions,
                   dense_dimensions=dense_dimensions,
                   optimizer=optimizer)

# Visualize the model
try:
    plot_model(agent.model, to_file='model.png', show_shapes=True)
except ImportError as e:
    logger.warning("Couldn't print the model image: {}".format(e))

# Iteratively train the agent on a batch of previously seen examples while continuously expanding the experience buffer
# This example seems to converge to nearly optimal rewards in at least  two out of three game branches
epochs = 1
for i in range(epochs):
    logger.info('Epoch %s', i)
    agent.train_online(episodes=8192, batch_size=256, gamma=0.95, epsilon_decay=0.999,
                       prioritized_fraction=0.25, test_interval=8, test_steps=5)

model = agent.model

# transfer
agent2 = SSAQNAgent(train_simulators=[simulator_paraphrased], test_simulators=[simulator_paraphrased, simulator])
agent2.initialize_tokens('vocabulary.txt')

optimizer = RMSprop(lr=0.00001)

embedding_dimensions = 16
lstm_dimensions = 32
dense_dimensions = 8

agent2.create_model(embedding_dimensions=embedding_dimensions,
                    lstm_dimensions=lstm_dimensions,
                    dense_dimensions=dense_dimensions,
                    optimizer=optimizer)
agent2.model = model

agent2.train_online(episodes=8192, batch_size=256, gamma=0.95, epsilon=1, epsilon_decay=0.99,
                    prioritized_fraction=0.25, test_interval=16, test_steps=5, log_prefix='paraphrased')

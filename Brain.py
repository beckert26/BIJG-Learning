import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.preprocessing import MinMaxScaler

class Brain:
    def __init__(self):
        # Configuration paramaters for the whole setup
        self.seed = 42
        self.gamma = 0.99  # Discount factor for past rewards
        self.epsilon = 1.0  # Epsilon greedy parameter
        self.epsilon_min = 0.05  # Minimum epsilon greedy parameter
        self.epsilon_max = 1.0  # Maximum epsilon greedy parameter
        self.epsilon_interval = (
                self.epsilon_max - self.epsilon_min
        )  # Rate at which to reduce chance of random action being taken
        self.batch_size = 32  # Size of batch taken from replay buffer
        self.max_steps_per_episode = 10000
        self.num_actions = 9

        self.ep_test = 0
        # The first model makes the predictions for Q-values which are used to
        # make a action.
        self.model = self.create_q_model(self.num_actions)
        # Build a target model for the prediction of future rewards.
        # The weights of a target model get updated every 10000 steps thus when the
        # loss between the Q-values is calculated the target Q-value is stable.
        self.model_target = self.create_q_model(self.num_actions)

        # In the Deepmind paper they use RMSProp however then Adam optimizer
        # improves training time
        self.optimizer = keras.optimizers.Adam(learning_rate=0.001, clipnorm=1.0)

        # Experience replay buffers
        self.action_history = []
        self.state_history = []
        self.state_next_history = []
        self.rewards_history = []
        self.done_history = []
        self.episode_reward_history = []
        self.running_reward = 0
        self.episode_count = 0
        self.frame_count = 0
        # Number of frames to take random action and observe output
        self.epsilon_random_frames = 50000
        # Number of frames for exploration
        self.epsilon_greedy_frames = 100000.0
        # Maximum replay length
        # Note: The Deepmind paper suggests 1000000 however this causes memory issues
        self.max_memory_length = 100000
        # Train the model after 4 actions
        self.update_after_actions = 10
        # How often to update the target network
        self.update_target_network = 10000
        # Using huber loss for stability
        self.loss_function = keras.losses.Huber()
        self.state = None
        self.timestep = 1
        self.episode_reward = 0

    def decision(self, inp):
        inputs = inp

        #while True:  # Run until solved
        state = inputs
        self.state = state
        #episode_reward = 0

        #for timestep in range(1, self.max_steps_per_episode):
        #if self.timestep < self.max_steps_per_episode:
        # env.render(); Adding this line would show the attempts
        # of the agent in a pop up window.
        self.frame_count += 1

        # Use epsilon-greedy for exploration
        if self.frame_count < self.epsilon_random_frames or self.epsilon > np.random.rand(1)[0]:
            # Take random action
            action = np.random.choice(self.num_actions)
        else:
            # Predict action Q-values
            # From environment state
            state_tensor = tf.convert_to_tensor(state)
            state_tensor = tf.expand_dims(state_tensor, 0)
            action_probs = self.model(state_tensor, training=False)
            # Take best action
            action = tf.argmax(action_probs[0]).numpy()

        # Decay probability of taking random action
        self.epsilon -= self.epsilon_interval / self.epsilon_greedy_frames
        self.epsilon = max(self.epsilon, self.epsilon_min)

        return action

    def update(self, action, state, state_next, reward, done):
        #print(self.frame_count)
        #state_next = inp_next
        # Apply the sampled action in our environment
        #state_next, reward, done, _ = env.step(action)
        #scaler = MinMaxScaler(feature_range=(-1, 1))
        #state = scaler.fit_transform(state)
        #state_next = scaler.fit_transform(state_next)

        self.episode_reward += reward
        # Save actions and states in replay buffer
        self.action_history.append(action)
        self.state_history.append(state)
        self.state_next_history.append(state_next)
        self.done_history.append(done)
        self.rewards_history.append(reward)
        self.state = state_next

        # Update every fourth frame and once batch size is over 32
        if self.frame_count % self.update_after_actions == 0 and len(self.done_history) > self.batch_size:
            if(self.ep_test == 0 and self.epsilon < 0.1):
                print("epsilon low")
                self.ep_test = 1
            # Get indices of samples for replay buffers
            indices = np.random.choice(range(len(self.done_history)), size=self.batch_size)

            # Using list comprehension to sample from replay buffer
            state_sample = np.array([self.state_history[i] for i in indices])
            state_next_sample = np.array([self.state_next_history[i] for i in indices])
            rewards_sample = [self.rewards_history[i] for i in indices]
            action_sample = [self.action_history[i] for i in indices]
            done_sample = tf.convert_to_tensor(
                [float(self.done_history[i]) for i in indices]
            )

            # Build the updated Q-values for the sampled future states
            # Use the target model for stability
            future_rewards = self.model_target(state_next_sample)
            # Q value = reward + discount factor * expected future reward
            updated_q_values = rewards_sample + self.gamma * tf.reduce_max(
                future_rewards, axis=1
            )

            # If final frame set the last value to -1
            updated_q_values = updated_q_values * (1 - done_sample) - done_sample

            # Create a mask so we only calculate loss on the updated Q-values
            masks = tf.one_hot(action_sample, self.num_actions)

            with tf.GradientTape() as tape:
                # Train the model on the states and updated Q-values
                q_values = self.model(state_sample)
                #print(q_values)
                # Apply the masks to the Q-values to get the Q-value for action taken
                q_action = tf.reduce_sum(tf.multiply(q_values, masks), axis=1)
                # Calculate loss between new Q-value and old Q-value
                loss = self.loss_function(updated_q_values, q_action)

            # Backpropagation
            grads = tape.gradient(loss, self.model.trainable_variables)
            self.optimizer.apply_gradients(zip(grads, self.model.trainable_variables))

        if self.frame_count % self.update_target_network == 0:

            self.episode_reward_history.append(self.episode_reward)
            self.episode_count += 1
            if len(self.episode_reward_history) > 100:
                del self.episode_reward_history[:1]
            self.running_reward = np.mean(self.episode_reward_history)

            # update the the target network with new weights
            self.model_target.set_weights(self.model.get_weights())
            # Log details
            template = "running reward: {:.2f} episode reward: {:.2f} at episode {}, move count {}"
            print(template.format(self.running_reward, self.episode_reward, self.episode_count, self.frame_count))
            self.episode_reward = 0

        # Limit the state and reward history
        if len(self.rewards_history) > self.max_memory_length:
            del self.rewards_history[:1]
            del self.state_history[:1]
            del self.state_next_history[:1]
            del self.action_history[:1]
            del self.done_history[:1]



        #if done:

            """
            # Update running reward to check condition for solving
            self.episode_reward_history.append(self.episode_reward)
            
            if len(self.episode_reward_history) > 100:
                del self.episode_reward_history[:1]
            self.running_reward = np.mean(self.episode_reward_history)

            self.episode_count += 1
            """


    def create_q_model(self,num_actions):
        # Network defined by the Deepmind paper
        inputs = layers.Input(shape=(32,))

        # Convolutions on the frames on the screen
        layer1 = layers.Dense(32, activation="relu")(inputs)
        layer2 = layers.Dense(32, activation="relu")(layer1)
        layer3 = layers.Dense(32, activation="relu")(layer2)
        #layer4 = layers.Dense(32, activation="relu")(layer3)
        #layer5 = layers.Dense(32, activation="relu")(layer4)
        #layer6 = layers.Dense(32, activation="relu")(layer5)
        #layer7 = layers.Dense(32, activation="relu")(layer6)
        #layer8 = layers.Dense(32, activation="relu")(layer7)
        #layer9 = layers.Dense(32, activation="relu")(layer8)
        #layer10 = layers.Dense(32, activation="relu")(layer9)
        #layer11 = layers.Dense(32, activation="relu")(layer10)
        #layer12 = layers.Dense(32, activation="relu")(layer11)
        #layer13 = layers.Dense(32, activation="relu")(layer12)
        #layer14 = layers.Dense(32, activation="relu")(layer13)
        #layer15 = layers.Dense(32, activation="relu")(layer14)
        #layer16 = layers.Dense(32, activation="relu")(layer15)

        #layer4 = layers.Flatten()(layer3)

        #layer4 = layers.Dense(16, activation="relu")(layer3)
        #layer5 = layers.Dense(16, activation="relu")(layer4)
        action = layers.Dense(num_actions, activation="linear")(layer3)

        return keras.Model(inputs=inputs, outputs=action)


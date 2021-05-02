from copy import deepcopy
from itertools import count

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 

import numpy as np
import torch
import torch.nn.functional as F
from torch.autograd import Variable
from torch.distributions import Categorical
from torch.utils.tensorboard import SummaryWriter

from reinforcement_learning_algo.core.action import Action
from reinforcement_learning_algo.core.environment import Environment
from reinforcement_learning_algo.cost_esimator import *


class PolicyGradient:
    """
    Create policy network which takes state features as input and outputs denormalized
    action values.
    """

    def __init__(self, neural_network, temporal_mapping_ordering, layer,
                 im2col_layer, layer_rounded, spatial_loop_comb, input_settings, mem_scheme, ii_su, spatial_unrolling):

        super(PolicyGradient, self).__init__()

        # Init our policy net
        self.policy_net = neural_network

        # Starting Temporal Mapping
        self.starting_temporal_mapping = temporal_mapping_ordering

        # Cost Estimation Parameters
        self.loss = 0
        self.layer = layer
        self.layer_post = layer.size_list_output_print
        self.im2col_layer = im2col_layer
        self.layer_rounded = layer_rounded
        self.spatial_loop_comb = spatial_loop_comb
        self.input_settings = input_settings
        self.mem_scheme = mem_scheme
        self.ii_su = ii_su
        self.full_layer = [self.im2col_layer, self.layer_rounded]
        self.mac_costs = calculate_mac_level_costs(self.layer, self.layer_rounded,
                                                   self.input_settings, self.mem_scheme, self.ii_su)
        self.spatial_unrolling = spatial_unrolling

    def optimize(self, writer, episode, steps, reward_pool, log_probability_list, verbose=0):
        pass

    def filter_legal_actions(self, state, action_probs):
        temporal_mapping = state["temporal_mapping"]
        # compressed_temporal_mapping
        # print(state)

    def select_action(self, state, observation_state_length):
        encoded_padded_state = deepcopy(state)
        encoded_padded_state = encoded_padded_state['temporal_mapping']
        encoded_padded_state = encoded_padded_state.make_encoded_state_vector(observation_state_length)
        action_probs = self.policy_net(encoded_padded_state)
        # legal_actions = self.filter_legal_actions(state, action_probs)
        # print(action_probs)
        action = Action(action_list_size=observation_state_length)
        state = state['temporal_mapping'].value
        action_probs = action.filter_action_list(state=state, action_probs=action_probs)
        # print(action_probs)
        best_legal_action = F.softmax(action_probs, dim=0)
        # print(best_legal_action)
        layer = [x for x in best_legal_action if x > 0]
        # print("p",len(layer))
        m = Categorical(best_legal_action)
        # print(m)
        action_id = m.sample()
        self.policy_net.saved_log_probs.append(m.log_prob(action_id))
        action_id = action_id.tolist()
        # print(action_id)
        # return action.item()
        entropy = - (best_legal_action * best_legal_action.log()).sum()
        log_prob = best_legal_action.log()
        action.set_idx(action_id)
        return action, log_prob, entropy

    def calculate_rewards(self, episode=None, gamma=0.9) -> list:
        R = 0
        t_steps = np.arange(len(self.policy_net.rewards))
        discounted_rewards = self.policy_net.rewards * gamma ** t_steps
        discounted_rewards = discounted_rewards[::-1].cumsum()[::-1]
        discounted_rewards = discounted_rewards / gamma ** t_steps
        # returns = []
        # for timestamp, reward in enumerate(self.policy_net.rewards[::-1]):
        #     # R = reward + pow(gamma, -episode) * R
        #     discounted_reward += pow(gamma, )
        #     returns.insert(0, R)
        # returns = torch.tensor(returns)
        # normalize rewards
        # if (returns.std() + eps) > 0:
        #     returns = (returns - returns.mean()) / (returns.std() + eps)
        return discounted_rewards

    def calculate_loss(self, returns) -> list:
        policy_loss = []
        for log_prob, reward in zip(self.policy_net.saved_log_probs, returns):
            policy_loss.append(-log_prob * reward)
        return policy_loss

    def finish_episode(self, episode, gamma=0.9):
        """
        Function for calculating rewards, loss and doing backward propagation.
        :return:
            policy_loss - summarized loss
        """
        # returns = self.calculate_rewards(episode, gamma)
        # policy_loss = self.calculate_loss(returns)

        R = torch.zeros(231)
        loss = 0
        for i in reversed(range(len(self.policy_net.rewards))):
            R = gamma * R + self.policy_net.rewards[i]
            log_probs_tensor = Variable(R).expand_as(self.log_probs[i])
            advantage = (self.log_probs[i] * log_probs_tensor).sum()
            loss = loss - advantage - (0.0001 * self.entropies[i]).sum()
            policy_loss = loss / len(self.policy_net.rewards)

        self.optimizer.zero_grad()
        # policy_loss = torch.stack(policy_loss).sum()
        policy_loss.backward()
        # utils.clip_grad_norm(self.policy_net.parameters(), 40)
        self.optimizer.step()
        # clean memory
        del self.policy_net.rewards[:]
        del self.policy_net.saved_log_probs[:]
        return policy_loss

    def training(self, learning_rate=1e-2, reward_stop_condition=0.5, gamma=0.9, log_interval=1,
                 observation_state_length=22, episode_utilization_stop_condition=0.8, timestamp_number=50,
                 render=True):
        writer = SummaryWriter()
        self.optimizer = torch.optim.Adam(self.policy_net.parameters(), lr=learning_rate)
        env = Environment(layer=self.layer, im2col_layer=self.im2col_layer, layer_rounded=self.layer_rounded,
                          spatial_loop_comb=self.spatial_loop_comb, input_settings=self.input_settings,
                          mem_scheme=self.mem_scheme, ii_su=self.ii_su, spatial_unrolling=self.spatial_unrolling, mac_costs=self.mac_costs,
                          observation_state_length=observation_state_length,
                          utilization_threshold=episode_utilization_stop_condition,
                          timestamp_threshold=timestamp_number)

        step = 0
        best_result = ()
        max_reward = 0
        result_reward = 0
        running_reward = 0
        for i_episode in count(1):
            done = False
            state, episode_reward = env.reset(), 0
            episode_rewards = []
            self.log_probs = []
            self.entropies = []
            
            for timestamp in range(1, 10000):  # Don't do infinite loop while learning

                action, log_prob, entropy = self.select_action(state, observation_state_length)
                writer.add_scalar("Action", action.idx, step)
                state, reward, done, info = env.step(action, timestep=timestamp)
                if render:
                    env.render_frame()
                if done:
                    break

                if reward > max_reward:
                    max_reward = reward
                    best_result = state
                self.policy_net.rewards.append(reward)
                self.entropies.append(entropy)
                self.log_probs.append(log_prob)
                episode_reward += reward
                episode_rewards.append(reward)
                print('Episode {}\tTimestamp: {}\tReward: {:.2f}\tAction: {}\tInfo: {}'.format(
                    i_episode, timestamp, reward, action.idx, info))
                step += 1
                writer.add_scalar("Episode reward", reward, step)

            writer.add_scalar("Episode mean reward", np.mean(episode_rewards), step)
            result_reward += episode_reward
            writer.add_scalar("Cumulative reward", result_reward, step)
            mean_reward = np.mean(episode_rewards)
            running_reward = 0.05 * result_reward + (1 - 0.05) * running_reward
            writer.add_scalar("Running reward", running_reward, i_episode)
            writer.add_scalar("Max reward", max(episode_rewards), step)

            loss = self.finish_episode(i_episode, gamma)
            if render:
                env.render()

            if i_episode % log_interval == 0:
                print('Episode {}\tLast reward: {:.2f}\tAverage reward: {:.2f} Loss{}'.format(
                    i_episode, episode_reward, running_reward, loss))
                writer.add_scalar("Loss", loss, i_episode)
                writer.add_scalar("Reward", running_reward, i_episode)

            if best_result['temporal_mapping'].utilization >= reward_stop_condition:
                print("Solved! Running reward is now {} and "
                      "the last episode runs to {} time st  eps!".format(running_reward, timestamp))
                print(f"Best result: {best_result['temporal_mapping'].value}\treward {best_result['temporal_mapping'].utilization}")
                print('Episode {}\tLast reward: {:.2f}\tAverage reward: {:.2f} Max reward{}\tLoss{}'.format(
                    i_episode, mean_reward, running_reward, max(episode_rewards), loss))
                if timestamp > 1:
                    writer.add_scalar("Loss", loss, i_episode)
                    writer.add_scalar("Reward", running_reward, i_episode)
                if render:
                    env.display()
                    print("displayed")
                self.policy_net.save()

    def run_episode(self, starting_temporal_mapping, episode_max_step):
        self.policy_net.load()
        print(self.policy_net)

        encoded_padded_state = deepcopy(starting_temporal_mapping)
        encoded_padded_state = encoded_padded_state['temporal_mapping']
        encoded_padded_state = encoded_padded_state.make_encoded_state_vector()
        action_probs = self.policy_net(encoded_padded_state)

        print()
        # value = self.policy_net(starting_temporal_mapping)
        # print(value)

        pass

from __future__ import division, print_function

import pprint
import pandas as pd
import numpy as np
import itertools
import requests
import random
import math
from sklearn import preprocessing
import scipy.stats as stats
import matplotlib.mlab as mlab
import evaluation
import getcontext
import statsmodels.api as sm

from scipy.stats import multivariate_normal

credentials = {'teamid' : 'Coffeeblack',
               'teampw' : '23e88f60c155804c79cfd1af83e47fc8'}

def logit_link(x):
    """
    Link function for Stochastic Gradient Descent (SGD)
    """

    return 1 / (1 + math.exp(-1 * x))


 
class OnlineBootstrap(object):

    def __init__(self, arms, context_path):


        # Load context
        self.context = self.create_dummy_context(context_path)
        self.context['Age'] =  self.context['Age'] / 50.

        self.context.drop(['ID'], axis=1, inplace=True)

        # Length of context
        self.d_c = len(self.context.ix[0, :])

        # All arm properties
        self.df_arms = pd.DataFrame(arms)
        
        self.K = len(self.df_arms)
        
        # Number of pulls for each arm
        self.pulls = [0] * len(self.df_arms)

        # Expected reward of each arm
        self.values = [0.0] * len(self.df_arms)  

        # Number of bootstrap duplicates
        self.J = 1000

        # Create bootstrap duplicates for each arm
        self.B = self.create_bootstrap_replicates()

        # Properties of arm (for sending them to the server)
        self.properties = None

        # Create backup of arms data frame
        self.df_arms_original = self.df_arms.copy()

        # With normalized price
        self.df_arms['price'] = self.df_arms.price / 50.

        
        # Adaptive learning rate per arm and bootstrap
        self.n = np.matrix(np.ones((self.K, self.J)))

        # Time steps
        self.t = 0

        # Current best arm
        self.i_star = 0

        self.epsilon_phase = 2200

        
    def create_bootstrap_replicates(self):

        """
        Create bootstrap replicates for each arm
        """

        replicates = np.zeros((self.K, self.J, self.d_c))

        return replicates
        

    def update(self, arm, reward, alpha=0.01, l=0.05):

        """
        Update the value of a chosen arm
        """


        # Epsilon-greedy phase
        if self.t < self.epsilon_phase:
        
            self.pulls[arm] += 1

            # New number of pull
            n = self.pulls[arm]

            # Old value
            old_val = self.values[arm]

            # New value (online weighted average)
            new_val = ((n - 1) / n) * old_val + (1 / n) * reward

            # Update value
            self.values[arm] = new_val

        # Bootstrap phase           
        else:

            # Get context for time t
            context = self.context.loc[self.t, :]

            # Make reward 0 or 1
            reward = int(bool(reward))
            
            self.pulls[arm] += 1

            if self.t == self.epsilon_phase:

                # Indeces of 15 best arms
                ind = np.argpartition(np.array(self.values), -15)[-15:]
                self.df_arms = self.df_arms.loc[ind, :]
                
                # Update time step
                self.t += 1
                
                return

            for j in range(self.J):

                # The pseudocode for this part can be found in:
                # Tang, Liang, et al. "Personalized Recommendation
                # via Parameter-Free Contextual Bandits." (2015).
                    
                p = np.random.binomial(self.pulls[i], 1 / self.pulls[i])

                for z in range(p):

                    n = 1 / np.sqrt(self.n[i, j] + 1)
                        
                    bs_theta = self.B[i, j]

                    hypothesis = np.dot(bs_theta, context.values)

                    hypothesis = logit_link(hypothesis)

                    loss = reward - hypothesis

                    self.B[i, j] += n * loss * context.values
                    self.n[i, j] += 1
                
        # Update time step
        self.t += 1

        
    def draw(self, runid, i):

        """
        Draw the random sample arm (i.e. send JSON to server and receive
        reward)
        """

        ids = {'runid': runid, 'i': i }

        payload = dict(self.properties.items() + ids.items())

        payload.update(credentials)  # Add credentials

        print(payload)

        # Propose page and get JSON answer
        r = requests.get("http://krabspin.uci.ru.nl/proposePage.json/",
                         params=payload)

        r_json = r.json()['effect']

        if r_json['Error'] is not None:
            print("Error in id:", i)

        return r_json['Success'] * payload['price']


    # Create dummies for context
    def create_dummy_context(self, path):

        # Read in df
        context_df = pd.read_csv(path)

        # Create dummy variables

        context_df['Intercept'] = 1

        df = pd.get_dummies(context_df, columns=['Agent',
                                                 'Language',
                                                 'Referer'
        ])

        return df

    

    def select_arm(self):

        """
        Return index of the arm that we want to draw in this round.
        """


        # Use epsilon policy for the first 2300 rounds (see self.epsilon_phase)
        if self.t <= self.epsilon_phase:
        
            p = random.uniform(0, 1)

            if p > 0.8:
                # Exploitation
                bestarm = np.argmax(self.values)

            else:
                # Exploration
                bestarm = random.randrange(len(self.values))
           
        else:        

            # Bootstrap samples collector
            bs_samples_collector = np.ones((self.K, self.d_c)) * (-10)

            # Draw samples from bootstrap replicates for each arm (at uniform random probability)
            for i in self.df_arms.index:# range(self.K):

                # Theta_tilde_a_i is the bootstrap sample for arm i
                theta_tilde_a_i = random.choice(self.B[i])

                bs_samples_collector[i] = theta_tilde_a_i

            # Make predictions (arm max f(x, theta)
            hypotheses = np.inner(bs_samples_collector, self.context.loc[self.t, :].values)

            # Create a vectorized form of the logit link function
            logit_link_vec = np.vectorize(logit_link)

            # Use logit link for each entry in hypotheses 
            hypotheses = logit_link_vec(hypotheses)

            # Weigh hypotheses with their prices
            hypotheses = np.multiply(hypotheses, (self.df_arms_original.price.values))

            bestarm = np.argmax(hypotheses)

            print("Max is", np.max(hypotheses))

            
        # Update properties (for drawing arm)
        self.properties = self.df_arms_original.loc[bestarm, :].to_dict()

        # i_star is the best arm
        self.i_star = bestarm

        return bestarm

           
        
def arm_product(dicts):

    """
    Helper function for create_all_arm_properties
    """
    
    return (dict(itertools.izip(dicts, x)) for x in itertools.product(*dicts.itervalues()))


def create_all_arm_properties():

    """
    Create all combinations of possible actions
    """

    combined = {
        'header': [5, 15, 35],
        'adtype': ['skyscraper', 'square', 'banner'],
        'color': ['green', 'blue', 'red', 'black', 'white'],
        'price': [float(str(np.around(x, 2))) for x in np.arange(2, 50.01, 3.00)],  # in 3 Euro steps
        'productid': range(10, 26)
        }

    
    arms = list(arm_product(combined))

    return arms        

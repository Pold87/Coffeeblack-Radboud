import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

all_rewards = np.array([])
all_times = np.array([])

for runid in range(10001, 10018, 1):

    df = pd.read_csv("final_results/new_results" + str(runid) + "-4.csv")

    mean_reward = df.rewards.mean()
    
    duration = df.times[len(df.times) - 1] - df.times[0]
    all_times = np.append(all_times, [duration])
    all_rewards = np.append(all_rewards, [mean_reward])

em = pd.expanding_mean(all_rewards)
em_times = pd.expanding_mean(all_times)

x = np.arange(0, len(em), 1)

print("Overall mean time per runid (in sec)", all_times.mean())
print("Overall mean cumulative reward", all_rewards.mean())
print("SE of the times (in sec)", stats.sem(all_times))
print("SE of the mean cumulative rewards", stats.sem(all_rewards))

plt.plot(x, em)
plt.show()





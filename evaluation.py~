import pandas as pd
import numpy as np
import bandits
import time
import getcontext

def test_policy(policy, runid, ids):

    """
    Test a given policy on a certain runid
    """

    # Arms that are chosen
    chosen_arms = [0] * len(ids)

    # Rewards that are received
    rewards = [0] * len(ids)

    # When was an action done?
    times = [0] * len(ids)

    for idx in ids:

        # Print progress
        if idx % 1000 == 0:
            print(idx)

        # Select and save arm
        chosen_arm = policy.select_arm()
        chosen_arms[idx] = chosen_arm

        # Get and save reward
        reward = policy.draw(runid, idx)
        
        rewards[idx] = reward

        times[idx] = int(time.time())

        policy.update(chosen_arm, reward)

    results = pd.DataFrame({"chosen_arms": chosen_arms,
                            "rewards": rewards,
                            "times": times})

    # Save to folder final_results
    results.to_csv("final_results/new_results" + str(runid) + "-4.csv", index=False)

    return results


def main():

    # Create all possible arms
    all_arm_properties = bandits.create_all_arm_properties()

    # Initialize ids
    ids = range(10000)

    # Iterative over test set
    for context in range(70000, 70001, 1):

        # Get and save context
        getcontext.process_all_threads(context, getcontext.process_thread)
        big_df = getcontext.join_df(context)
        big_df.to_csv("final_contexts/context_" + str(context) + ".csv", index=False)
        
        # Use policy
        bootstrap = bandits.OnlineBootstrap(all_arm_properties, "final_contexts/context_" + str(context) + ".csv")
        test_policy(bootstrap, context, ids)


if __name__ == "__main__":

    main()

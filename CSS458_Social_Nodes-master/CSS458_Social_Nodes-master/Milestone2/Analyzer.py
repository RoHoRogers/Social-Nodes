# -*- coding: utf-8 -*-
import Model as M
import Visualizer as V

"""
Sample class to do simple analysis on how different personalities affect data.
"""

personalities = ["Introvert", "Extrovert"]
models = []

#Run simulation many times, and change personality
for num in range(len(personalities)):
    m = None
    if num == 0:
        m = M.Model(time_to_run=20, num_agents=100, force_personalities=M.static_introvert_personalities_who_like_distant_people,
              visualizer = True)
    elif num == 1:
        m = M.Model(time_to_run=20, num_agents=100, force_personalities=M.static_extrovert_personalities_who_like_distant_people ,
              visualizer = True)
                   
    m.run_simulation()
    
V.Visualizer.sharedVisualizer.showWithPersonalities(personalities)
    
Launch file to view the robot
```
ros2 launch demo_arm_description display.launch.py 
```

<img width="1219" height="683" alt="image" src="https://github.com/user-attachments/assets/01dc42db-b25e-4a64-8e07-f9a68212c852" />


First launch the gazebo world
```
ros2 launch demo_arm_description gazebo.launch.py
```

<img width="1219" height="683" alt="image" src="https://github.com/user-attachments/assets/c3a407c5-1005-44b2-ba90-80d50ad26656" />

Then launch moveit environment
```
ros2 launch arm_moveit moveit.launch.py 
```
Then add meshes in moving scene
```
ros2 run py_moveit2 ex_collision_object.py
```

<img width="1029" height="519" alt="image" src="https://github.com/user-attachments/assets/21e0a390-3966-4c26-9992-747ee7c3c23e" />

### References
https://github.com/IFRA-Cranfield/IFRA_LinkAttacher

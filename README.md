Launch file to view the robot
```
ros2 launch demo_arm_description display.launch.py 
```

<img width="1219" height="683" alt="image" src="https://github.com/user-attachments/assets/01dc42db-b25e-4a64-8e07-f9a68212c852" />


First launch the gazebo world
```
ros2 launch demo_arm_description gazebo.launch.py
```
Then launch moveit environment
```
ros2 launch arm_moveit moveit.launch.py 
```

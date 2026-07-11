\# Stabilization and Motion Control in Two-Wheeled Self-Balancing Robots



\[!\[TÜBİTAK 2209-B Support](https://img.shields.io/badge/Supported-TÜBİTAK%202209--B-blue)]()



This project presents an innovative approach to the stabilization and motion control of a two-wheeled self-balancing robot\[cite: 1]. The system contains an inverted pendulum, which has a nonlinear and difficult-to-control structure\[cite: 1]. By combining model-based state estimation, a cascaded PID control strategy, and a Kalman Filter for sensor fusion, the project ensures high stability and a safe driving experience even under external disturbances and inclined surfaces\[cite: 1].



\---



\## 1. Mathematical Modeling and Inherent Instability



The robot's body is modeled as an inverted pendulum to understand its physical anatomy\[cite: 1]. To simplify the nonlinear equations of motion, a small-angle approximation was applied to derive the state-space matrices\[cite: 1]. 



!\[Impulse Response](assets/impulse\_response.png)



\* \*\*Open-Loop Response:\*\* Simulations demonstrate that without a control mechanism, an impulse input causes the pitch angle to diverge exponentially, proving the system's inherent instability\[cite: 1].

\* \*\*Root Locus Analysis:\*\* The system's root locus plot reveals a pole situated in the right half of the s-plane, which mathematically dictates that a closed-loop controller is strictly required to achieve stability\[cite: 1].



!\[Root Locus](assets/root\_locus.png)



\---



\## 2. Hardware Architecture \& 3D Chassis Design



To maintain an optimal center of gravity, a three-layer chassis architecture was designed\[cite: 1]. This symmetrical mass distribution ensures that the center of gravity aligns with the turning point of the wheels\[cite: 1].



\* \*\*Bottom Layer:\*\* Houses the 12V 450 RPM DC motors with encoders and the 4S 18650 Li-ion battery pack, keeping the heaviest components as low as possible\[cite: 1].

!\[Bottom Layer](assets/bottom\_layer.png)



\* \*\*Middle Layer:\*\* Acts as the central processing unit, containing the 32-bit dual-core Raspberry Pi Pico H, the high-efficiency MOSFET-based TB6612FNG motor driver, and tiered 12V/5V step-down voltage regulators to isolate logic components from voltage fluctuations\[cite: 1].

!\[Middle Layer](assets/middle\_layer.png)



\* \*\*Top Layer:\*\* Houses the MPU6050 IMU sensor to maximize accelerometer sensitivity, along with the HC-06 Bluetooth module for remote telemetry and control\[cite: 1].

!\[Top Layer](assets/top\_layer.png)



\---



\## 3. Sensor Fusion and Kalman Filtering



Obtaining a clean pitch angle is the most critical stage for control\[cite: 1]. The MPU6050's accelerometer is susceptible to high-frequency mechanical noise from the motors, while the gyroscope suffers from low-frequency drift over time due to numerical integration\[cite: 1].



!\[Raw Sensor Data](assets/raw\_data.png)



\* \*\*Why Kalman Filter?\*\* Raw sensor data fed directly into the PID controller leads to aggressive motor behavior and system crashes\[cite: 1]. A Kalman Filter was implemented instead of a simpler Complementary Filter because it dynamically calculates the Kalman gain to provide an optimal estimate based on real-time uncertainty\[cite: 1].

\* \*\*Filter Tuning:\*\* The measurement noise covariance (`R\_measure = 1.0`) was tuned relatively high to heavily filter out mechanical vibrations from the DC motors\[cite: 1]. The process noise covariance (`Q\_angle = 0.001`, `Q\_bias = 0.003`) was kept very low to trust the gyroscope's immediate short-term predictions, successfully compensating for drift\[cite: 1].



!\[Kalman Performance](assets/kalman\_performance.png)



\---



\## 4. Cascade PID Control Architecture



Controlling both vertical balance and horizontal velocity simultaneously cannot be achieved with a single standard PID loop\[cite: 1]. Therefore, a Cascade Control Architecture was implemented to decouple the system's dynamics\[cite: 1].



!\[Control Block Diagram](assets/block\_diagram.png)



\* \*\*Outer Loop (Velocity PI):\*\* Processes encoder feedback to calculate the actual linear velocity using a low-pass filter to reduce mathematical noise\[cite: 1]. It compares this with the user's velocity command\[cite: 1]. The PI controller accumulates velocity errors over time (Integral gain) to generate the necessary target angle (setpoint) to overcome continuous loads like ramps\[cite: 1].

\* \*\*Inner Loop (Balance PD):\*\* Tracks the target angle dictated by the outer loop using the filtered MPU6050 data\[cite: 1]. It is designed as a pure PD controller to prevent phase lag\[cite: 1]. The high proportional gain (`Kp = 11.5`) acts as a stiff virtual spring, while the derivative gain acts as a braking mechanism to provide fast mechanical reflexes without accumulating past errors\[cite: 1].



\---



\## 5. Experimental Results and Performance Analysis



The real-world performance of the cascaded architecture was validated through dynamic field tests, including external disturbances and inclined surfaces\[cite: 1].



\### Zero-Velocity Command (Station Keeping)

When instructed to stop on a flat surface, the robot maintains its angle within a narrow band of -1.5° and 1.5°\[cite: 1]. The small continuous motor oscillations (within a range of \\pm 40 pulses) are caused by mechanical realities, such as gear backlash inside the DC motor gearboxes, which the highly sensitive controller continuously corrects\[cite: 1].

!\[Zero Command](assets/zero\_command.png)



\### External Disturbance Rejection

When a sudden external physical force is applied, the pitch angle deviates up to \\pm 8°\[cite: 1]. The inner loop reacts instantaneously, driving the motors to peaks of 300 to 400 pulses to catch the falling center of gravity\[cite: 1]. The robot exhibits a critically damped response, absorbing the hit and returning to its 0° baseline in less than 1 second without swinging back and forth\[cite: 1].

!\[External Disturbance](assets/external\_disturbance.png)



\### Forward / Backward Motion Tracking

To initiate forward motion, the outer loop calculates a negative reference angle\[cite: 1]. The robot intentionally "falls" forward, dropping to approximately -3.5°, and then settles between -1° and -2° to maintain a steady speed of 130 pulses\[cite: 1]. Backward motion mirrors this dynamic, settling at positive angles to sustain reverse velocity\[cite: 1].

!\[Forward Command](assets/forward\_command.png)



\### Ramp Performance and Equilibrium (22° Incline)

To test extreme dynamic limits, the robot was driven onto a 22° ramp\[cite: 1]. 

\* \*\*Climbing:\*\* Upon hitting the ramp's entrance bump, the motor velocity oscillates heavily to overcome the physical barrier before the system forces a severe pitch of -25° to generate leverage against the slope\[cite: 1].

!\[Ramp Test](assets/ramp.png)

\* \*\*Equilibrium on Ramp:\*\* When given a stop command on the incline, the integral term of the outer loop accumulates the gravitational error\[cite: 1]. Instead of sliding backward, the robot locks into a permanent forward tilt of -24°, successfully keeping its center of mass directly over the wheels' contact point\[cite: 1].

!\[Equilibrium on Ramp](assets/equilibrium.png)





\## 🎥 Real-World Performance Videos



Click on the thumbnail images below to watch the dynamic performance and stability tests of the robot.



\*\*1. Equilibrium (Zero-Velocity) Test\*\*

\[!\[Equilibrium Test](https://img.youtube.com/vi/lMF--UhxCo0/0.jpg)](https://www.youtube.com/watch?v=lMF--UhxCo0)



\*\*2. Forward/Backward Motion Control\*\*

\[!\[Motion Test](https://img.youtube.com/vi/uI9pQXXA0wc/0.jpg)](https://www.youtube.com/watch?v=uI9pQXXA0wc)



\*\*3. External Disturbance Rejection\*\*

\[!\[Disturbance Test](https://img.youtube.com/vi/UOZk5o-JTDY/0.jpg)](https://www.youtube.com/watch?v=UOZk5o-JTDY)



\*\*4. Station Keeping on Incline\*\*

\[!\[Station Keeping Test](https://img.youtube.com/vi/slhCB4x3sgQ/0.jpg)](https://www.youtube.com/watch?v=slhCB4x3sgQ)



\*\*5. 22° Ramp Climb and Descent\*\*

\[!\[Ramp Test](https://img.youtube.com/vi/cuVFi5KD84g/0.jpg)](https://www.youtube.com/watch?v=cuVFi5KD84g)














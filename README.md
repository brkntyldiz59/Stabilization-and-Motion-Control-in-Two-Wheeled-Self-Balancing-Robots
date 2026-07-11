\# Stabilization and Motion Control in Two-Wheeled Self-Balancing Robots



\[!\[TÜBİTAK 2209-B Support](https://img.shields.io/badge/Supported-TÜBİTAK%202209--B-blue)]()



This project presents an innovative approach to the stabilization and motion control of a two-wheeled self-balancing robot. The system contains an inverted pendulum, which has a nonlinear and difficult-to-control structure. By combining model-based state estimation, a cascaded PID control strategy, and a Kalman Filter for sensor fusion, the project ensures high stability and a safe driving experience even under external disturbances and inclined surfaces.



!\[Self-Balancing Robot](https://github.com/brkntyldiz59/Stabilization-and-Motion-Control-in-Two-Wheeled-Self-Balancing-Robots/blob/main/assets/robot_view.jpg)



\---



\## 1. Mathematical Modeling and Inherent Instability



The robot's body is modeled as an inverted pendulum to understand its physical anatomy. To simplify the nonlinear equations of motion, a small-angle approximation was applied to derive the state-space matrices.



!\[Impulse Response](assets/impulse\_response.jpg)



\* \*\*Open-Loop Response:\*\* Simulations demonstrate that without a control mechanism, an impulse input causes the pitch angle to diverge exponentially, proving the system's inherent instability.

\* \*\*Root Locus Analysis:\*\* The system's root locus plot reveals a pole situated in the right half of the s-plane, which mathematically dictates that a closed-loop controller is strictly required to achieve stability.



!\[Root Locus](assets/root\_locus.jpg)



\---



\## 2. Hardware Architecture \& 3D Chassis Design



To maintain an optimal center of gravity, a three-layer chassis architecture was designed. This symmetrical mass distribution ensures that the center of gravity aligns with the turning point of the wheels.



\* \*\*Bottom Layer:\*\* Houses the 12V 450 RPM DC motors with encoders and the 4S 18650 Li-ion battery pack, keeping the heaviest components as low as possible.

!\[Bottom Layer](assets/bottom\_layer.jpg)



\* \*\*Middle Layer:\*\* Acts as the central processing unit, containing the 32-bit dual-core Raspberry Pi Pico H, the high-efficiency MOSFET-based TB6612FNG motor driver, and tiered 12V/5V step-down voltage regulators to isolate logic components from voltage fluctuations.

!\[Middle Layer](assets/middle\_layer.jpg)



\* \*\*Top Layer:\*\* Houses the MPU6050 IMU sensor to maximize accelerometer sensitivity, along with the HC-06 Bluetooth module for remote telemetry and control.

!\[Top Layer](assets/top\_layer.jpg)



\---



\## 3. Sensor Fusion and Kalman Filtering



Obtaining a clean pitch angle is the most critical stage for control. The MPU6050's accelerometer is susceptible to high-frequency mechanical noise from the motors, while the gyroscope suffers from low-frequency drift over time due to numerical integration.



!\[Raw Sensor Data](assets/raw\_data.jpg)



\* \*\*Why Kalman Filter?\*\* Raw sensor data fed directly into the PID controller leads to aggressive motor behavior and system crashes. A Kalman Filter was implemented instead of a simpler Complementary Filter because it dynamically calculates the Kalman gain to provide an optimal estimate based on real-time uncertainty.

\* \*\*Filter Tuning:\*\* The measurement noise covariance (R\_measure = 1.0) was tuned relatively high to heavily filter out mechanical vibrations from the DC motors. The process noise covariance (Q\_angle = 0.001, Q\_bias = 0.003) was kept very low to trust the gyroscope's immediate short-term predictions, successfully compensating for drift.



!\[Kalman Performance](assets/kalman\_performance.jpg)



\---



\## 4. Cascade PID Control Architecture



Controlling both vertical balance and horizontal velocity simultaneously cannot be achieved with a single standard PID loop. Therefore, a Cascade Control Architecture was implemented to decouple the system's dynamics.



!\[Control Block Diagram](assets/block\_diagram.jpg)



\* \*\*Outer Loop (Velocity PI):\*\* Processes encoder feedback to calculate the actual linear velocity using a low-pass filter to reduce mathematical noise. It compares this with the user's velocity command. The PI controller accumulates velocity errors over time (Integral gain) to generate the necessary target angle (setpoint) to overcome continuous loads like ramps.

\* \*\*Inner Loop (Balance PD):\*\* Tracks the target angle dictated by the outer loop using the filtered MPU6050 data. It is designed as a pure PD controller to prevent phase lag. The high proportional gain (Kp = 11.5) acts as a stiff virtual spring, while the derivative gain acts as a braking mechanism to provide fast mechanical reflexes without accumulating past errors.



\---



\## 5. Experimental Results and Performance Analysis



The real-world performance of the cascaded architecture was validated through dynamic field tests, including external disturbances and inclined surfaces.



\### Zero-Velocity Command (Station Keeping)

When instructed to stop on a flat surface, the robot maintains its angle within a narrow band of -1.5° and 1.5°. The small continuous motor oscillations (within a range of ± 40 pulses) are caused by mechanical realities, such as gear backlash inside the DC motor gearboxes, which the highly sensitive controller continuously corrects.

!\[Zero Command](assets/zero\_command.jpg)



\### External Disturbance Rejection

When a sudden external physical force is applied, the pitch angle deviates up to ± 8°. The inner loop reacts instantaneously, driving the motors to peaks of 300 to 400 pulses to catch the falling center of gravity. The robot exhibits a critically damped response, absorbing the hit and returning to its 0° baseline in less than 1 second without swinging back and forth.

!\[External Disturbance](assets/external\_disturbance.jpg)



\### Forward / Backward Motion Tracking

To initiate forward motion, the outer loop calculates a negative reference angle. The robot intentionally "falls" forward, dropping to approximately -3.5°, and then settles between -1° and -2° to maintain a steady speed of 130 pulses. Backward motion mirrors this dynamic, settling at positive angles to sustain reverse velocity.

!\[Forward Command](assets/forward\_command.jpg)



\### Ramp Performance and Equilibrium (22° Incline)

To test extreme dynamic limits, the robot was driven onto a 22° ramp.

\* \*\*Climbing:\*\* Upon hitting the ramp's entrance bump, the motor velocity oscillates heavily to overcome the physical barrier before the system forces a severe pitch of -25° to generate leverage against the slope.

!\[Ramp Test](assets/ramp.png)

\* \*\*Equilibrium on Ramp:\*\* When given a stop command on the incline, the integral term of the outer loop accumulates the gravitational error. Instead of sliding backward, the robot locks into a permanent forward tilt of -24°, successfully keeping its center of mass directly over the wheels' contact point.

!\[Equilibrium on Ramp](assets/equilibriumjpg)



\---



\## 🎥 Real-World Performance Videos



Click the links below to watch the dynamic performance and stability tests of the robot (YouTube Shorts):



\* \[▶️ Watch: Equilibrium (Zero-Velocity) Test](https://youtube.com/shorts/lMF--UhxCo0)

\* \[▶️ Watch: Forward/Backward Motion Control](https://www.youtube.com/shorts/uI9pQxXA0wc)

\* \[▶️ Watch: External Disturbance Rejection](https://youtube.com/shorts/UOZk5o-JTDY)

\* \[▶️ Watch: Station Keeping on Incline](https://youtube.com/shorts/slhCB4x3sgQ)

\* \[▶️ Watch: 22° Ramp Climb and Descent](https://youtube.com/shorts/cuVFi5KD84g)










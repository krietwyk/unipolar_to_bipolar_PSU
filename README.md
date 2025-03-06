# unipolar_to_bipolar_PSU
A little box to convert 3 identical power supplies from being unipolar to bipolar. 

Imagine using a set of 3 concentric Helmholtz coil to create a uniform, stable magnetic field with a controlled strength and direction, only to find that the 3 power supplies (PS) to power the coils were unipolar. Instead of being able to switch the current direction to create magnetic field vector at any angle, the coils are limited to positive currents and the magnetic field vector stuck in a single octant (1/8th of the sphere). 
[Diagram of coils]

The remedy, a H-bridge using a DPDT relay for each power supply, with the switching controlled using a pi pico 2. Each H-bridge works by having poles 1 and 2 of each relay connected to the +’ve and –‘ve terminal from a power supply of one of the Helmholtz coils. The normally connected (NC) contacts for poles 1 and 2 a connected to +’ve and –‘ve terminal of a coil. The normally open (NO) contacts are connected in reverse, pole 1 NO is shorted to pole 2 NC and –‘ve Helmholtz coils terminal and pole 2 NO is shorted to pole NC and the +’ve Helmholtz coil terminal. So in the normal state, the +’ve terminal of the Helmholtz coil receives a +’ve voltage and the –‘ve is connected to –‘ve. When the pole is thrown to the NO state, the +’ve terminal from the PS is connected to the –‘ve terminal of the Helmholtz coils and the –‘ve terminal from the PS is connected to the +‘ve terminal of the Helmholtz coils, reverse the current flow through the coil. The choice of DPDT, bistable relays was to ensure that the power supply couldn’t be accidently shorted and to prevent the polarity from changing unexpectedly if the pico connection was interrupted. 
[Diagram of H-bridge]

Each of the relays are triggered by a 1 s low pulse by a gpio from the pico to the trigger pin on the relay module, except the pico can’t supply sufficient current to trigger directly and the current was amplified. To amplified the current, I used a 2N7000 N-channel MOSFET and the same 5 V source I used for the relays. For each relay, the GPIO is connect gate via a 220 ohm resistor to prevent excessive currents and the GPIO is grounded via a 10 kohm resistor to pull down the gate for more stable operation. The drain is connected to the trigger and the source is grounded. The pico is also grounded to the 5 V, using a 10 kohm resistor

A short coming of the relays is that it isn’t possible to know the state of relay directly. Fortunately, the relay modules have a diode that indicates whether the relay is in NO or NC. To read the state I connected the diode from each relay to a VADC pin on the pico to read the voltage across the diode to check if it is on (NO) or off (NC). Unfortunately, the diodes run at ~5 V while the pico can read up to only 3.3 V. A voltage divider circuit was used to reduce the voltage. I used a R1 = 10 kohm and R2 = 6 kohm and (roughly) resistor to reduce Vout = 10/(10+6) × 5 V to ~3.1 V.  This works well enough, the voltage measurements vary wildly and is a known issue with picos but small enough to be able to check if a diode is on or off.

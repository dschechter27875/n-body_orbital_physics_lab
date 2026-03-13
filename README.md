# 🪐 N-Body Orbital Physics Simulator

Interactive computational physics lab for exploring **Newtonian gravity, orbital mechanics, and chaotic multi-body dynamics** using a **Velocity Verlet integrator**.

Live interactive demo:

https://huggingface.co/spaces/dschechter27/N-Body_Orbital_Physics_Lab

This project implements a full **N-body gravitational simulation engine**, interactive **parameter exploration UI**, and **energy diagnostics** to verify the physical correctness of the simulation.

The simulator is deployed as an interactive app using **Gradio + Hugging Face Spaces**.

---

## Demo

![Simulation Demo](assets/screenshotlab.png)

Example animation:

![Three Body Demo](assets/three_body_demo.gif)

---

# Overview

This project simulates the gravitational motion of multiple bodies interacting through Newton's law of universal gravitation.

Users can experiment with:

• Two-body orbital systems  
• Chaotic three-body dynamics  
• Custom gravitational experiments  
• Energy conservation diagnostics  
• Adjustable numerical simulation parameters  

The engine uses a **Velocity Verlet integrator**, a numerical method commonly used in:

• astrophysics simulations  
• molecular dynamics  
• orbital mechanics  
• particle simulations  

---

# Physics Model

The simulator models the **classical N-body gravitational problem**.

For N bodies interacting gravitationally, each body experiences the combined gravitational force of all other bodies.

---

# Newton's Law of Gravitation

The gravitational force between two masses is:

\[
F = G \frac{m_i m_j}{r^2}
\]

Where

• \(G\) — gravitational constant  
• \(m_i, m_j\) — masses  
• \(r\) — distance between bodies  

---

# Vector Form Used in the Simulation

Because the system is simulated in 2-D space, we use the vector formulation of Newtonian gravity:

\[
\mathbf{F}_{ij} =
G \frac{m_i m_j}{|\mathbf{r}_{ij}|^3}
\mathbf{r}_{ij}
\]

Where

\[
\mathbf{r}_{ij} = \mathbf{r}_j - \mathbf{r}_i
\]

This automatically produces both the **magnitude and direction** of the gravitational force.

---

# From Force to Acceleration

Using Newton's Second Law:

\[
F = ma
\]

we compute acceleration directly:

\[
\mathbf{a}_i =
\sum_{j \ne i}
G \frac{m_j}{|\mathbf{r}_{ij}|^3}
\mathbf{r}_{ij}
\]

Each body accumulates acceleration contributions from **all other bodies**.

---

# Orbital Mechanics

For a stable circular orbit, gravitational force must equal centripetal force.

Centripetal force:

\[
F_c = \frac{mv^2}{r}
\]

Gravitational force:

\[
F_g = G \frac{Mm}{r^2}
\]

Setting them equal:

\[
G \frac{Mm}{r^2} = \frac{mv^2}{r}
\]

Solving for orbital velocity:

\[
v = \sqrt{\frac{GM}{r}}
\]

This equation is used to initialize **stable circular orbits** in the simulation.

---

# Numerical Integration

Real physical motion is continuous, but computers simulate time in **discrete steps**.

We must approximate:

\[
\frac{d\mathbf{r}}{dt} = \mathbf{v}
\]

\[
\frac{d\mathbf{v}}{dt} = \mathbf{a}
\]

---

# Semi-Implicit Euler (baseline method)

A simple integration method is:

\[
v(t+\Delta t) = v(t) + a(t)\Delta t
\]

\[
r(t+\Delta t) = r(t) + v(t+\Delta t)\Delta t
\]

However this method can cause **energy drift** in orbital simulations.

---

# Velocity Verlet Integrator

To improve stability, this simulator uses the **Velocity Verlet algorithm**.

Position update:

\[
\mathbf{r}_{t+\Delta t}
=
\mathbf{r}_t
+
\mathbf{v}_t \Delta t
+
\frac{1}{2}\mathbf{a}_t \Delta t^2
\]

Acceleration is then recomputed.

Velocity update:

\[
\mathbf{v}_{t+\Delta t}
=
\mathbf{v}_t
+
\frac{1}{2}
(\mathbf{a}_t + \mathbf{a}_{t+\Delta t})
\Delta t
\]

Advantages:

• better **energy conservation**  
• improved **numerical stability**  
• widely used in **astrophysics and molecular dynamics**

---

# Energy Diagnostics

To validate the simulation we track total system energy.

### Kinetic Energy

\[
K = \frac{1}{2}mv^2
\]

### Gravitational Potential Energy

\[
U =
- G \frac{m_i m_j}{r_{ij}}
\]

### Total Energy

\[
E = K + U
\]

For a physically correct simulation:

• kinetic and potential energy **oscillate**  
• total energy remains **nearly constant**

The UI displays an **energy diagnostic plot** to verify this.

---

# Chaotic Three-Body Dynamics

Unlike the two-body problem, the **three-body problem has no general analytic solution**.

Small changes in initial conditions lead to dramatically different trajectories.

This simulator demonstrates:

• chaotic orbital motion  
• gravitational slingshots  
• unstable orbital configurations  

---

# Softening Parameter

To avoid numerical instability when two bodies pass extremely close to each other, the simulation uses **gravitational softening**:

\[
r^2 \rightarrow r^2 + \epsilon^2
\]

This prevents singularities when \(r \to 0\).

---

# Computational Complexity

The naive gravitational calculation evaluates every pair of bodies:

\[
O(N^2)
\]

For small systems this is acceptable, but large astrophysical simulations often use algorithms like:

• Barnes–Hut trees  
• Fast multipole methods  

---

# Implementation Architecture

Core components of the simulation:

### Body class

Stores:

• mass  
• position  
• velocity  
• acceleration  
• visual trail  

---

### Physics engine

Computes:

• pairwise gravitational accelerations  
• velocity updates  
• position updates  

---

### Simulation engine

Controls:

• time stepping  
• integration method  
• physics parameters  

---

### Visualization

Matplotlib is used to render:

• orbital trajectories  
• animated simulations  
• energy diagnostic plots  

---

### Interactive UI

The Hugging Face interface allows users to modify:

• timestep  
• gravitational constant  
• softening parameter  
• number of frames  
• physics steps per frame  
• body masses and velocities  

---

# Repository Structure

```
nbody-orbital-simulator
│
├── physics_engine_lab.ipynb
├── app.py
├── requirements.txt
├── README.md
└── assets
    ├── screenshotlab.png
    └── three_body_demo.gif
```

---

# Technologies Used

• Python  
• NumPy  
• Matplotlib  
• Gradio  
• Hugging Face Spaces  

---

# Future Extensions

Possible improvements:

• Barnes–Hut tree algorithm (O(N log N))  
• Lyapunov exponent chaos measurement  
• phase-space visualizations  
• 3-D orbital simulation  
• galaxy formation simulations  

---

# Author

David Schechter  
Incoming MIT '30  
Interested in physics, machine learning, and computational modeling.

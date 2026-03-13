import os
import tempfile
from dataclasses import dataclass, field

import gradio as gr
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation


# -----------------------------
# Core physics data structures
# -----------------------------
@dataclass
class Body:
    name: str
    mass: float
    position: np.ndarray
    velocity: np.ndarray
    color: str = "white"
    size: float = 8.0
    acceleration: np.ndarray = field(default_factory=lambda: np.zeros(2, dtype=float))
    trail: list = field(default_factory=list)

    def __post_init__(self):
        self.position = np.array(self.position, dtype=float)
        self.velocity = np.array(self.velocity, dtype=float)
        self.acceleration = np.array(self.acceleration, dtype=float)

    def record_position(self):
        self.trail.append(self.position.copy())


# -----------------------------
# Physics engine
# -----------------------------
def compute_accelerations(bodies, G=1.0, softening=1e-3):
    n = len(bodies)
    accelerations = [np.zeros(2, dtype=float) for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i == j:
                continue

            displacement = bodies[j].position - bodies[i].position
            distance_sq = np.dot(displacement, displacement) + softening**2
            distance = np.sqrt(distance_sq)

            accelerations[i] += G * bodies[j].mass * displacement / (distance_sq * distance)

    return accelerations


def step_velocity_verlet(bodies, dt, G=1.0, softening=1e-3):
    old_accelerations = compute_accelerations(bodies, G=G, softening=softening)

    for body, acc in zip(bodies, old_accelerations):
        body.acceleration = acc
        body.position = body.position + body.velocity * dt + 0.5 * acc * dt**2

    new_accelerations = compute_accelerations(bodies, G=G, softening=softening)

    for body, old_acc, new_acc in zip(bodies, old_accelerations, new_accelerations):
        body.velocity = body.velocity + 0.5 * (old_acc + new_acc) * dt
        body.acceleration = new_acc
        body.record_position()


class SimulationVV:
    def __init__(self, bodies, dt=0.001, G=1.0, softening=1e-3):
        self.bodies = bodies
        self.dt = dt
        self.G = G
        self.softening = softening
        self.time = 0.0

        for body in self.bodies:
            if len(body.trail) == 0:
                body.record_position()

    def step(self):
        step_velocity_verlet(
            self.bodies,
            dt=self.dt,
            G=self.G,
            softening=self.softening,
        )
        self.time += self.dt


# -----------------------------
# Diagnostics
# -----------------------------
def compute_kinetic_energy(bodies):
    total_ke = 0.0
    for body in bodies:
        total_ke += 0.5 * body.mass * np.dot(body.velocity, body.velocity)
    return total_ke


def compute_potential_energy(bodies, G=1.0, softening=1e-3):
    total_pe = 0.0
    n = len(bodies)

    for i in range(n):
        for j in range(i + 1, n):
            displacement = bodies[j].position - bodies[i].position
            distance = np.sqrt(np.dot(displacement, displacement) + softening**2)
            total_pe += -G * bodies[i].mass * bodies[j].mass / distance

    return total_pe


# -----------------------------
# Presets
# -----------------------------
def make_two_body_system(G=1.0):
    M = 1000.0
    r = 1.0
    v = np.sqrt(G * M / r)

    sun = Body(
        name="Sun",
        mass=M,
        position=[0.0, 0.0],
        velocity=[0.0, 0.0],
        color="gold",
        size=18,
    )

    earth = Body(
        name="Earth",
        mass=1.0,
        position=[r, 0.0],
        velocity=[0.0, v],
        color="deepskyblue",
        size=8,
    )

    return [sun, earth]


def make_three_body_system():
    body1 = Body(
        name="Body 1",
        mass=500.0,
        position=[-0.8, 0.0],
        velocity=[0.0, -10.0],
        color="orange",
        size=14,
    )

    body2 = Body(
        name="Body 2",
        mass=500.0,
        position=[0.8, 0.0],
        velocity=[0.0, 10.0],
        color="cyan",
        size=14,
    )

    body3 = Body(
        name="Body 3",
        mass=5.0,
        position=[0.0, 1.2],
        velocity=[18.0, 0.0],
        color="magenta",
        size=8,
    )

    return [body1, body2, body3]


def make_custom_two_body(central_mass, orbit_radius, planet_mass, planet_speed, tangential_direction):
    sun = Body(
        name="Central Body",
        mass=central_mass,
        position=[0.0, 0.0],
        velocity=[0.0, 0.0],
        color="gold",
        size=18,
    )

    vy = planet_speed if tangential_direction == "Counterclockwise" else -planet_speed

    planet = Body(
        name="Planet",
        mass=planet_mass,
        position=[orbit_radius, 0.0],
        velocity=[0.0, vy],
        color="deepskyblue",
        size=8,
    )

    return [sun, planet]


# -----------------------------
# Rendering
# -----------------------------
def simulate_system(
    preset,
    dt,
    frames,
    steps_per_frame,
    G,
    softening,
    trail_length,
    central_mass,
    orbit_radius,
    planet_mass,
    planet_speed,
    tangential_direction,
):
    if preset == "Two-Body Circular Orbit":
        bodies = make_two_body_system(G=G)
    elif preset == "Three-Body Chaotic System":
        bodies = make_three_body_system()
    else:
        bodies = make_custom_two_body(
            central_mass=central_mass,
            orbit_radius=orbit_radius,
            planet_mass=planet_mass,
            planet_speed=planet_speed,
            tangential_direction=tangential_direction,
        )

    sim = SimulationVV(bodies, dt=dt, G=G, softening=softening)

    kinetic_history = []
    potential_history = []
    total_history = []

    fig, (ax_orbit, ax_energy) = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor("#0f1117")
    ax_orbit.set_facecolor("black")
    ax_energy.set_facecolor("white")

    max_range = max(2.5, orbit_radius * 1.8)
    ax_orbit.set_xlim(-max_range, max_range)
    ax_orbit.set_ylim(-max_range, max_range)
    ax_orbit.set_aspect("equal")
    ax_orbit.set_title("Orbital Dynamics", color="white", fontsize=14)
    ax_orbit.tick_params(colors="white")
    for spine in ax_orbit.spines.values():
        spine.set_color("white")
    ax_orbit.grid(alpha=0.15, color="white")

    ax_energy.set_title("Energy Diagnostics", fontsize=14)
    ax_energy.set_xlabel("Frame")
    ax_energy.set_ylabel("Energy")
    ax_energy.grid(alpha=0.3)

    scatters = []
    trail_lines = []

    for body in sim.bodies:
        scatter = ax_orbit.scatter([], [], color=body.color, s=body.size * 18, edgecolors="white", linewidths=0.5)
        line, = ax_orbit.plot([], [], color=body.color, alpha=0.7, linewidth=1.5)
        scatters.append(scatter)
        trail_lines.append(line)

    ke_line, = ax_energy.plot([], [], label="Kinetic Energy", linewidth=2)
    pe_line, = ax_energy.plot([], [], label="Potential Energy", linewidth=2)
    te_line, = ax_energy.plot([], [], label="Total Energy", linewidth=2)
    ax_energy.legend()

    def init():
        for scatter, line in zip(scatters, trail_lines):
            scatter.set_offsets(np.array([[np.nan, np.nan]]))
            line.set_data([], [])
        ke_line.set_data([], [])
        pe_line.set_data([], [])
        te_line.set_data([], [])
        return scatters + trail_lines + [ke_line, pe_line, te_line]

    def update(_frame):
        for _ in range(steps_per_frame):
            sim.step()

        ke = compute_kinetic_energy(sim.bodies)
        pe = compute_potential_energy(sim.bodies, G=G, softening=softening)
        kinetic_history.append(ke)
        potential_history.append(pe)
        total_history.append(ke + pe)

        for i, body in enumerate(sim.bodies):
            scatters[i].set_offsets(body.position.reshape(1, 2))
            trail = np.array(body.trail[-trail_length:])
            if len(trail) > 1:
                trail_lines[i].set_data(trail[:, 0], trail[:, 1])

        x = np.arange(len(total_history))
        ke_line.set_data(x, kinetic_history)
        pe_line.set_data(x, potential_history)
        te_line.set_data(x, total_history)

        ax_energy.relim()
        ax_energy.autoscale_view()

        return scatters + trail_lines + [ke_line, pe_line, te_line]

    anim = FuncAnimation(
        fig,
        update,
        frames=frames,
        init_func=init,
        interval=40,
        blit=False,
    )

    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "nbody_simulation.gif")
    anim.save(output_path, writer="pillow", fps=20)
    plt.close(fig)

    return output_path


# -----------------------------
# Gradio UI
# -----------------------------
DESCRIPTION = """
## N-Body Orbital Physics Lab

Explore Newtonian gravity with an interactive **Velocity Verlet** simulation.

### Included
- Two-body circular orbit
- Three-body chaotic dynamics
- Custom two-body experiment mode
- Energy diagnostics
- Adjustable timestep, softening, and trail length
"""

with gr.Blocks(title="N-Body Orbital Physics Lab", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🪐 N-Body Orbital Physics Lab")
    gr.Markdown(DESCRIPTION)

    with gr.Row():
        with gr.Column():
            preset = gr.Dropdown(
                choices=[
                    "Two-Body Circular Orbit",
                    "Three-Body Chaotic System",
                    "Custom Two-Body Experiment",
                ],
                value="Two-Body Circular Orbit",
                label="Preset",
            )

            dt = gr.Slider(0.0001, 0.005, value=0.0005, step=0.0001, label="Time Step (dt)")
            frames = gr.Slider(100, 400, value=250, step=50, label="Rendered Frames")
            steps_per_frame = gr.Slider(1, 8, value=4, step=1, label="Physics Steps per Frame")
            G = gr.Slider(0.1, 5.0, value=1.0, step=0.1, label="Gravitational Constant (G)")
            softening = gr.Slider(0.0001, 0.05, value=0.001, step=0.0001, label="Softening")
            trail_length = gr.Slider(20, 300, value=100, step=10, label="Trail Length")

            gr.Markdown("### Custom Two-Body Controls")
            central_mass = gr.Slider(100, 5000, value=1000, step=50, label="Central Mass")
            orbit_radius = gr.Slider(0.5, 3.0, value=1.0, step=0.1, label="Orbit Radius")
            planet_mass = gr.Slider(0.1, 20.0, value=1.0, step=0.1, label="Planet Mass")
            planet_speed = gr.Slider(1.0, 80.0, value=31.6, step=0.1, label="Planet Tangential Speed")
            tangential_direction = gr.Radio(
                choices=["Counterclockwise", "Clockwise"],
                value="Counterclockwise",
                label="Orbit Direction",
            )

            run_button = gr.Button("Run Simulation", variant="primary")

        with gr.Column():
            output_gif = gr.Image(label="Simulation Output", type="filepath")

    run_button.click(
        fn=simulate_system,
        inputs=[
            preset,
            dt,
            frames,
            steps_per_frame,
            G,
            softening,
            trail_length,
            central_mass,
            orbit_radius,
            planet_mass,
            planet_speed,
            tangential_direction,
        ],
        outputs=output_gif,
    )

if __name__ == "__main__":
    demo.launch()
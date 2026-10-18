import matplotlib.pyplot as plt

def plot_tec_history(victim, adversary) -> None:
    plt.figure(figsize=(10, 6))
    ecus = [victim, adversary]
    for ecu in ecus:
        if not ecu.tec_history:
            print(f"Warning: No TEC history for ECU {ecu.node_id}")
            continue

        times = [entry['time'] for entry in ecu.tec_history]
        tec_values = [entry['tec'] for entry in ecu.tec_history]

        normalized_times = [t - times[0] for t in times]

        if ecu.is_adversary:
            plt.plot(normalized_times,tec_values,label=f"ECU {ecu.node_id} (Adversary)",linestyle='--')
        else:
            plt.plot(normalized_times,tec_values,label=f"ECU {ecu.node_id} (Normal)")

    plt.xlabel("Time (seconds)")
    plt.ylabel("Transmit Error Counter (TEC)")
    plt.title("TEC Evolution of ECUs")
    plt.legend()
    plt.grid(True)

    plt.savefig('tec_plot.png', dpi=200, bbox_inches='tight')
    print(f"Plot saved as tec_plot.png")

    plt.show()
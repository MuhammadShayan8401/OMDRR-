import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import FancyBboxPatch
import mplcursors
import csv

class SchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OMDRR+ Scheduler")
        self.root.geometry("1100x780")
        self.root.configure(bg="#e6eef4")

        self.bg = "#e6eef4"
        self.fg = "#000000"
        self.color_map = {}
        self.last_gantt_figure = None
        self.timeline = []

        self.algorithm_var = tk.StringVar(value="OMDRR+")
        self.process_entries = []

        self.setup_widgets()

    def setup_widgets(self):
        font_opts = ("Segoe UI", 10)

        tk.Label(self.root, text="Process ID", bg=self.bg, font=font_opts).grid(row=0, column=0)
        tk.Label(self.root, text="Arrival Time", bg=self.bg, font=font_opts).grid(row=0, column=1)
        tk.Label(self.root, text="Burst Time", bg=self.bg, font=font_opts).grid(row=0, column=2)

        for i in range(5):
            pid_entry = tk.Entry(self.root)
            at_entry = tk.Entry(self.root)
            bt_entry = tk.Entry(self.root)
            pid_entry.insert(0, f"P{i+1}")
            pid_entry.grid(row=i+1, column=0, padx=4, pady=2)
            at_entry.grid(row=i+1, column=1, padx=4, pady=2)
            bt_entry.grid(row=i+1, column=2, padx=4, pady=2)
            bt_entry.bind("<KeyRelease>", lambda e: self.update_suggested_quantum())
            self.process_entries.append((pid_entry, at_entry, bt_entry))

        ttk.Label(self.root, text="Algorithm:").grid(row=7, column=0, pady=10)
        algo_dropdown = ttk.Combobox(self.root, textvariable=self.algorithm_var, values=["OMDRR+", "Round Robin"])
        algo_dropdown.grid(row=7, column=1, pady=10)

        ttk.Button(self.root, text="Run Scheduler", command=self.run_scheduler).grid(row=7, column=2, pady=10)

        self.suggested_quantum_label = tk.Label(self.root, text="Suggested Quantum: N/A", bg=self.bg, font=("Segoe UI", 10))
        self.suggested_quantum_label.grid(row=7, column=3, columnspan=2)

    def update_suggested_quantum(self):
        try:
            bursts = [int(bt.get()) for _, _, bt in self.process_entries if bt.get()]
            if bursts:
                tq = self.compute_dynamic_tq(bursts)
                self.suggested_quantum_label.config(text=f"Suggested Quantum: {tq}")
        except ValueError:
            self.suggested_quantum_label.config(text="Suggested Quantum: Invalid Input")

    def compute_dynamic_tq(self, bursts):
        harmonic = len(bursts) / sum(1 / b for b in bursts)
        arithmetic = sum(bursts) / len(bursts)
        return int((2 * harmonic + arithmetic) / 3)

    def run_scheduler(self):
        try:
            processes = []
            for pid_entry, at_entry, bt_entry in self.process_entries:
                pid = pid_entry.get().strip()
                at = int(at_entry.get())
                bt = int(bt_entry.get())
                if pid and bt >= 0:
                    processes.append((pid, at, bt))

            processes.sort(key=lambda x: x[1])  # Sort by arrival

            selected_algo = self.algorithm_var.get()
            if selected_algo == "Round Robin":
                quantum = self.compute_dynamic_tq([bt for _, _, bt in processes])
                timeline, wt, tat, rt, ct, st = self.round_robin(processes, quantum)
            else:  # OMDRR+
                timeline, wt, tat, rt, ct, st = self.omdrr_plus(processes)

            self.timeline = timeline
            self.waiting_times = wt
            self.turnaround_times = tat
            self.response_times = rt
            self.completion_times = ct
            self.start_times = st

            self.show_gantt_chart_animated(timeline)
            self.show_metrics_summary()

        except ValueError:
            messagebox.showerror("Input Error", "Please ensure all values are valid integers.")

    def round_robin(self, processes, tq):
        queue = []
        time = 0
        timeline = []
        waiting_times = {}
        turnaround_times = {}
        response_times = {}
        start_times = {}
        completion_times = {}
        remaining = {pid: bt for pid, _, bt in processes}
        arrival_map = {pid: at for pid, at, _ in processes}
        arrived = []

        processes.sort(key=lambda x: x[1])  # Sort by arrival
        i = 0
        while remaining:
            while i < len(processes) and processes[i][1] <= time:
                arrived.append(processes[i])
                i += 1

            if arrived:
                pid, at, _ = arrived.pop(0)
                bt = remaining[pid]
                if pid not in start_times:
                    start_times[pid] = time
                    response_times[pid] = time - at

                exec_time = min(tq, bt)
                timeline.append((time, time + exec_time, pid))
                time += exec_time
                remaining[pid] -= exec_time

                while i < len(processes) and processes[i][1] <= time:
                    arrived.append(processes[i])
                    i += 1

                if remaining[pid] > 0:
                    arrived.append((pid, at, bt))
                else:
                    completion_times[pid] = time
                    turnaround_times[pid] = time - at
                    waiting_times[pid] = turnaround_times[pid] - bt
            else:
                time += 1

        return timeline, waiting_times, turnaround_times, response_times, completion_times, start_times

    def omdrr_plus(self, processes):
        time = 0
        timeline = []
        waiting_times = {}
        turnaround_times = {}
        response_times = {}
        start_times = {}
        completion_times = {}
        remaining = {pid: bt for pid, _, bt in processes}
        arrival_map = {pid: at for pid, at, _ in processes}
        arrived = []
        processes.sort(key=lambda x: x[1])
        i = 0

        while remaining:
            while i < len(processes) and processes[i][1] <= time:
                arrived.append(processes[i])
                i += 1

            if arrived:
                burst_list = [remaining[pid] for pid, _, _ in arrived]
                tq = self.compute_dynamic_tq(burst_list) if burst_list else 1
                pid, at, _ = arrived.pop(0)
                bt = remaining[pid]

                if pid not in start_times:
                    start_times[pid] = time
                    response_times[pid] = time - at

                exec_time = min(tq, bt)
                timeline.append((time, time + exec_time, pid))
                time += exec_time
                remaining[pid] -= exec_time

                while i < len(processes) and processes[i][1] <= time:
                    arrived.append(processes[i])
                    i += 1

                if remaining[pid] > 0:
                    arrived.append((pid, at, bt))
                else:
                    completion_times[pid] = time
                    turnaround_times[pid] = time - at
                    waiting_times[pid] = turnaround_times[pid] - bt
            else:
                time += 1

        return timeline, waiting_times, turnaround_times, response_times, completion_times, start_times

    def show_metrics_summary(self):
        win = tk.Toplevel(self.root)
        win.title("Metrics Summary")
        win.geometry("500x400")
        win.configure(bg=self.bg)

        tk.Label(win, text="PID\tArrival\tBurst\tStart\tComplete\tWT\tTAT\tRT", bg=self.bg, fg=self.fg).pack(anchor="w")

        total_wt = total_tt = total_rt = 0
        n = len(self.waiting_times)

        for pid in self.waiting_times:
            at = self.start_times[pid] - self.waiting_times[pid]
            bt = self.turnaround_times[pid] - self.waiting_times[pid]
            st = self.start_times[pid]
            ct = self.completion_times[pid]
            wt = self.waiting_times[pid]
            tat = self.turnaround_times[pid]
            rt = self.response_times[pid]
            total_wt += wt
            total_tt += tat
            total_rt += rt
            tk.Label(win, text=f"{pid}\t{at}\t{bt}\t{st}\t{ct}\t{wt}\t{tat}\t{rt}", bg=self.bg, fg=self.fg).pack(anchor="w")

        tk.Label(win, text=f"\nAverage WT: {total_wt / n:.2f}", bg=self.bg, fg=self.fg).pack()
        tk.Label(win, text=f"Average TAT: {total_tt / n:.2f}", bg=self.bg, fg=self.fg).pack()
        tk.Label(win, text=f"Average RT: {total_rt / n:.2f}", bg=self.bg, fg=self.fg).pack()

    def show_gantt_chart_animated(self, timeline):
        fig, ax = plt.subplots(figsize=(10, 2))
        fig.patch.set_facecolor(self.bg)
        ax.set_facecolor(self.bg)
        ax.tick_params(colors=self.fg)
        ax.set_xlabel("Time", color=self.fg)
        ax.set_yticks([])
        ax.set_title("Gantt Chart", color=self.fg)

        self.color_map.clear()
        colors = plt.cm.tab20.colors
        for i, (_, _, pid) in enumerate(timeline):
            if pid not in self.color_map:
                self.color_map[pid] = colors[i % len(colors)]

        patches = []
        for start, end, pid in timeline:
            width = end - start
            color = self.color_map[pid]
            box = FancyBboxPatch((start, 0.25), width, 0.5, boxstyle="round,pad=0.1", color=color, ec="black")
            ax.add_patch(box)
            patches.append(box)

        ax.set_xlim(0, timeline[-1][1] + 2)
        mplcursors.cursor(patches).connect("add", lambda sel: sel.annotation.set_text(
            f"{timeline[sel.index][2]}\nStart: {timeline[sel.index][0]}\nEnd: {timeline[sel.index][1]}"
        ))

        for i, pid in enumerate(self.color_map):
            ax.text(timeline[-1][1] + 1, 1 - i * 0.15, f"{pid}", color=self.color_map[pid], fontsize=8)

        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.get_tk_widget().grid(row=9, column=0, columnspan=6, pady=10)
        canvas.draw()

        self.last_gantt_figure = fig

        ttk.Button(self.root, text="Export Gantt PNG", command=self.export_png).grid(row=10, column=0)
        ttk.Button(self.root, text="Export Metrics CSV", command=self.export_csv).grid(row=10, column=1)

    def export_png(self):
        if not self.last_gantt_figure:
            messagebox.showwarning("Export Failed", "Run the scheduler first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])
        if path:
            self.last_gantt_figure.savefig(path)
            messagebox.showinfo("Saved", f"Saved to {path}")

    def export_csv(self):
        if not self.waiting_times:
            messagebox.showwarning("Export Failed", "Run the scheduler first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if path:
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Process ID", "Arrival Time", "Burst Time", "Start Time", "Completion Time",
                                 "Waiting Time", "Turnaround Time", "Response Time"])
                for pid in self.waiting_times:
                    at = self.start_times[pid] - self.waiting_times[pid]
                    bt = self.turnaround_times[pid] - self.waiting_times[pid]
                    st = self.start_times[pid]
                    ct = self.completion_times[pid]
                    wt = self.waiting_times[pid]
                    tat = self.turnaround_times[pid]
                    rt = self.response_times[pid]
                    writer.writerow([pid, at, bt, st, ct, wt, tat, rt])
            messagebox.showinfo("Saved", f"CSV saved to {path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerGUI(root)
    root.mainloop()

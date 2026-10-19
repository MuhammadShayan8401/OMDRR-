# OMDRR+ Process Scheduler GUI

A desktop application built with Python (Tkinter and Matplotlib) designed to simulate, visualize, and compare CPU scheduling algorithms, featuring the OMDRR+ (Optimized Median-Dynamic Round Robin) algorithm alongside traditional Round Robin.

---

## Features

- Interactive GUI: User-friendly interface to configure process ID, arrival time, and burst time for up to 5 processes (expandable).
- Dynamic Quantum Computation: Automatically calculates an optimal Time Quantum (TQ) on-the-fly using a combination of harmonic and arithmetic means of process burst times.
- Multiple Scheduling Algorithms:
  - OMDRR+: Dynamic quantum scheduling optimized for turnaround and waiting times.
  - Round Robin: Standard fixed or dynamic quantum round-robin baseline.
- Interactive Gantt Chart: Built using Matplotlib with customized rounded task blocks and interactive tooltips powered by mplcursors.
- Comprehensive Metrics Summary: Automatically computes and displays Waiting Time (WT), Turnaround Time (TAT), Response Time (RT), Start Time, and Completion Time with averages.
- Export Capabilities:
  - Export the Gantt chart visualization as a high-resolution PNG image.
  - Export detailed scheduling metrics to a structured CSV file.

---

## Prerequisites & Dependencies

Ensure you have Python 3.x installed along with the required libraries. You can install the necessary dependencies using pip:

```bash
pip install matplotlib mplcursors

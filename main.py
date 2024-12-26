import numpy as np
import tkinter as tk
from tkinter import ttk
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1) 
except Exception:
    pass


def scale_matrix(sx, sy, sz):
    return np.array([
        [sx, 0,  0,  0],
        [0, sy,  0,  0],
        [0,  0, sz,  0],
        [0,  0,  0,  1]
    ])

def translate_matrix(tx, ty, tz):
    return np.array([
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0,  1]
    ])

def rotation_matrix(axis, angle):
    c, s = np.cos(angle), np.sin(angle)
    if axis == 'x':
        return np.array([
            [1, 0,  0, 0],
            [0, c, -s, 0],
            [0, s,  c, 0],
            [0, 0,  0, 1]
        ])
    elif axis == 'y':
        return np.array([
            [ c, 0, s, 0],
            [ 0, 1, 0, 0],
            [-s, 0, c, 0],
            [ 0, 0, 0, 1]
        ])
    elif axis == 'z':
        return np.array([
            [c, -s, 0, 0],
            [s,  c, 0, 0],
            [0,  0, 1, 0],
            [0,  0, 0, 1]
        ])

def transform(vertices, matrix):
    return np.dot(matrix, vertices.T).T

def create_letter_g():
    vertices = np.array([
        [0, 0, 0], [2, 0, 0], [2, 10, 0], [0, 10, 0],
        [0, 0, 2], [2, 0, 2], [2, 10, 2], [0, 10, 2], 
        [2, 0, 0], [8, 0, 0], [8, 2, 0], [2, 2, 0], 
        [2, 0, 2], [8, 0, 2], [8, 2, 2], [2, 2, 2]  
    ])

    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7),
        (8, 9), (9, 10), (10, 11), (11, 8),
        (12, 13), (13, 14), (14, 15), (15, 12),
        (8, 12), (9, 13), (10, 14), (11, 15)
    ]

    vertices = np.hstack((vertices, np.ones((vertices.shape[0], 1))))
    return vertices, edges


def orthographic_projection(vertices, plane):
    if plane == "xy":
        return vertices[:, :2]
    elif plane == "xz":
        return vertices[:, [0, 2]]
    elif plane == "yz":
        return vertices[:, 1:]


class VisualizationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Visualization")

        self.vertices, self.edges = create_letter_g()
        self.transformed_vertices = self.vertices.copy()

        self.figure = plt.figure(figsize=(6, 6), facecolor='#f0f0f0')
        self.ax = self.figure.add_subplot(111, projection='3d')
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        controls = tk.Frame(root, bg='#d9d9d9')
        controls.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Label(controls, text="Transformations", font=("Arial", 14, "bold"), background='#d9d9d9').pack(pady=10)

        self.scale_x = self.create_scale_control(controls, "Scale X", 1.0)
        self.scale_y = self.create_scale_control(controls, "Scale Y", 1.0)
        self.scale_z = self.create_scale_control(controls, "Scale Z", 1.0)

        self.trans_x = self.create_scale_control(controls, "Translate X", 0.0)
        self.trans_y = self.create_scale_control(controls, "Translate Y", 0.0)
        self.trans_z = self.create_scale_control(controls, "Translate Z", 0.0)

        self.rot_x = self.create_scale_control(controls, "Rotate X", 0.0, -180, 180)
        self.rot_y = self.create_scale_control(controls, "Rotate Y", 0.0, -180, 180)
        self.rot_z = self.create_scale_control(controls, "Rotate Z", 0.0, -180, 180)

        ttk.Button(controls, text="Apply", command=self.apply_transformations).pack(pady=10)
        ttk.Button(controls, text="Projections", command=self.show_projections).pack(pady=10)
        ttk.Button(controls, text="Reset", command=self.reset_transformations).pack(pady=10)

        self.update_plot()

    def create_scale_control(self, parent, label, initial, from_=0.1, to=10.0):
        ttk.Label(parent, text=label, background='#d9d9d9').pack()
        scale = ttk.Scale(parent, from_=from_, to=to, value=initial, orient=tk.HORIZONTAL, length=200)
        scale.pack(pady=5)
        return scale

    def apply_transformations(self):
        sx, sy, sz = self.scale_x.get(), self.scale_y.get(), self.scale_z.get()
        tx, ty, tz = self.trans_x.get(), self.trans_y.get(), self.trans_z.get()
        rx, ry, rz = np.radians(self.rot_x.get()), np.radians(self.rot_y.get()), np.radians(self.rot_z.get())

        scale = scale_matrix(sx, sy, sz)
        translate = translate_matrix(tx, ty, tz)
        rotate_x = rotation_matrix('x', rx)
        rotate_y = rotation_matrix('y', ry)
        rotate_z = rotation_matrix('z', rz)

        transform_matrix = translate @ rotate_z @ rotate_y @ rotate_x @ scale
        self.transformed_vertices = transform(self.vertices, transform_matrix)

        self.update_plot()

    def update_plot(self):
        self.ax.clear()
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.set_xlim([-10, 10])
        self.ax.set_ylim([-10, 10])
        self.ax.set_zlim([-10, 10])

        for edge in self.edges:
            p1, p2 = self.transformed_vertices[edge[0]], self.transformed_vertices[edge[1]]
            self.ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], color='b')

        self.canvas.draw()

    def show_projections(self):
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        planes = ['xy', 'xz', 'yz']
        titles = ['Projection on XY', 'Projection on XZ', 'Projection on YZ']

        for ax, plane, title in zip(axes, planes, titles):
            proj = orthographic_projection(self.transformed_vertices, plane)
            ax.set_title(title)
            ax.scatter(proj[:, 0], proj[:, 1], color='red')
            ax.grid()
            ax.axis('equal')

        plt.show()

    def reset_transformations(self):
        self.transformed_vertices = self.vertices.copy()
        self.scale_x.set(1.0)
        self.scale_y.set(1.0)
        self.scale_z.set(1.0)
        self.trans_x.set(0.0)
        self.trans_y.set(0.0)
        self.trans_z.set(0.0)
        self.rot_x.set(0.0)
        self.rot_y.set(0.0)
        self.rot_z.set(0.0)
        self.update_plot()

if __name__ == "__main__":
    root = tk.Tk()
    app = VisualizationApp(root)
    root.mainloop()

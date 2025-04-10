import tkinter as tk
from tkinter import ttk, colorchooser
import math

class VerticalNotebook(ttk.Notebook):
    def __init__(self, master=None, **kw):
        ttk.Notebook.__init__(self, master, **kw)
        self.__vertical_init()

    def __vertical_init(self):
        style = ttk.Style()
        style.configure("Vertical.TNotebook", tabposition="wn")
        style.configure("Vertical.TNotebook.Tab", padding=[10, 5], width=15)
        self.configure(style="Vertical.TNotebook")

class ScrollableNotebookFrame(tk.Frame):
    def __init__(self, master, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

class Building:
    def __init__(self, canvas, name, x, y, width=100, height=60, color="lightgray"):
        self.canvas = canvas
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.rect = self.canvas.create_rectangle(
            x, y, x + width, y + height, fill=color, outline="black"
        )
        self.text = self.canvas.create_text(
            x + width / 2, y + height / 2, text=name, fill="black", font=("Arial", 8)
        )
        self.power_consumption = 0
        self.heat_consumption = 0
        self.power_generation = 0
        self.connected = True
        self.turbines = []

    def update(self, x=None, y=None, width=None, height=None, color=None):
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        if color is not None:
            self.color = color
        self.canvas.coords(
            self.rect, self.x, self.y, self.x + self.width, self.y + self.height
        )
        self.canvas.itemconfig(self.rect, fill=self.color)
        self.canvas.coords(
            self.text, self.x + self.width / 2, self.y + self.height / 2
        )

class Turbine:
    def __init__(self, canvas, id, x, y, power=16):
        self.canvas = canvas
        self.id = id
        self.power = power
        self.active = True
        self.runtime = 0
        self.last_maintenance = 0
        self.x = x
        self.y = y
        self.indicator = self.canvas.create_oval(
            x, y, x + 10, y + 10,
            fill="green", outline="black"
        )
        self.text = self.canvas.create_text(
            x + 15, y + 5, text=f"Турбина {id}", anchor="w", font=("Arial", 8)
        )

    def toggle(self):
        self.active = not self.active
        self.canvas.itemconfig(self.indicator, fill="green" if self.active else "red")

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Расчет параметров электроснабжения и отопления")
        self.geometry("1400x800")
        
        # Данные из таблицы
        self.objects_data = {
            "ГТЭС": {"power": 114, "heat": 2.74, "distance": 0, "summer_load": 0, "winter_load": 0},
            "ЦПС": {"power": 22, "heat": 0, "distance": 0.3, "summer_load": 70, "winter_load": 55},
            "УКПГ": {"power": 30.0, "heat": 3.04, "distance": 0.50, "summer_load": 90, "winter_load": 95},
            "ОБП": {"power": 9.0, "heat": 0.64, "distance": 3.0, "summer_load": 80, "winter_load": 90},
            "ВЖК": {"power": 2.0, "heat": 0.35, "distance": 3.50, "summer_load": 100, "winter_load": 100},
            "ПЖК": {"power": 3.0, "heat": 2.58, "distance": 4.0, "summer_load": 100, "winter_load": 100},
            "ПСП": {"power": 10.0, "heat": 1.91, "distance": 100.0, "summer_load": 100, "winter_load": 100},
        }
        
        # Добавляем кусты
        for i in range(1, 27):
            self.objects_data[f"Куст {i}"] = {
                "power": 0.7 + (i % 10) * 0.1 if i > 1 else 0.7,
                "heat": 0,
                "distance": 1.0 + (i-1) * 0.5 if i <= 19 else 17 + (i-20) * 1.0,
                "summer_load": 50,
                "winter_load": 100
            }

        # Левая часть - схема (в рамке)
        self.scheme_frame = tk.Frame(self, width=700, height=800, bg="white", bd=2, relief=tk.GROOVE)
        self.scheme_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(self.scheme_frame, bg="white", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Основные здания
        self.buildings = []
        
        # Центр (ГТЭС)
        center_x, center_y = 350, 350
        gtes = Building(self.canvas, "ГТЭС", center_x-50, center_y-30, width=100, height=60, color="#a8d8ea")
        gtes.power_generation = 114
        gtes.power_consumption = 0
        gtes.heat_consumption = 2.74
        
        # Добавляем турбины для ГТЭС с индикаторами
        self.turbines = []
        for i in range(9):
            x = center_x - 40 + (i % 3) * 30
            y = center_y + 40 + (i // 3) * 30
            turbine = Turbine(self.canvas, i+1, x, y)
            self.turbines.append(turbine)
            gtes.turbines.append(turbine)
        
        gtes.power_generation = sum(t.power for t in gtes.turbines if t.active)
        self.buildings.append(gtes)

        # Расположим объекты по расстоянию от ГТЭС с проверкой на пересечения
        objects_to_place = [
            ("ЦПС", 0.3, "#f7c5cc"),
            ("УКПГ", 0.5, "#c4dfaa"),
            ("ОБП", 3.0, "#ffd59e"),
            ("ВЖК", 3.5, "#d3b5e5"),
            ("ПЖК", 4.0, "#ffaaa5"),
            ("ПСП", 100.0, "#b5e8e0")
        ]

        # Распределим углы с учетом предотвращения наложений
        angles = [0, 60, 120, 180, 240, 300]  # Равномерное распределение по кругу
        radius_step = 80  # Шаг увеличения радиуса при обнаружении пересечений
        
        placed_buildings = []
        
        for i, (name, distance, color) in enumerate(objects_to_place):
            # Базовый радиус в зависимости от расстояния
            base_radius = min(distance * 50, 250) if distance < 50 else 300
            radius = base_radius
            angle = angles[i]
            
            # Пытаемся разместить здание без пересечений
            while True:
                x = center_x + radius * math.cos(math.radians(angle)) - 50
                y = center_y + radius * math.sin(math.radians(angle)) - 30
                
                # Проверяем пересечения с уже размещенными зданиями
                intersects = False
                for (bx, by, bw, bh) in placed_buildings:
                    if (x < bx + bw and x + 100 > bx and
                        y < by + bh and y + 60 > by):
                        intersects = True
                        break
                
                if not intersects:
                    break
                
                # Если есть пересечение, увеличиваем радиус
                radius += radius_step
            
            building = Building(self.canvas, name, x, y, width=100, height=60, color=color)
            building.power_consumption = self.objects_data[name]["power"]
            building.heat_consumption = self.objects_data[name]["heat"]
            self.buildings.append(building)
            placed_buildings.append((x, y, 100, 60))

        # Кусты - расположим по расстоянию от ГТЭС с проверкой на пересечения
        self.wells = []
        placed_wells = []
        
        for i in range(1, 27):
            distance = self.objects_data[f"Куст {i}"]["distance"]
            # Золотой угол для равномерного распределения
            angle = (i * 137.5) % 360
            
            # Масштабируем расстояние
            base_radius = min(distance * 20, 250) if distance < 15 else 300
            radius = base_radius
            
            # Пытаемся разместить куст без пересечений
            while True:
                x = center_x + radius * math.cos(math.radians(angle)) - 30
                y = center_y + radius * math.sin(math.radians(angle)) - 15
                
                # Проверяем пересечения
                intersects = False
                for (bx, by, bw, bh) in placed_buildings + placed_wells:
                    if (x < bx + bw and x + 60 > bx and
                        y < by + bh and y + 30 > by):
                        intersects = True
                        break
                
                if not intersects:
                    break
                
                # Если есть пересечение, немного увеличиваем радиус и корректируем угол
                radius += 10
                angle = (angle + 5) % 360
            
            well = Building(self.canvas, f"Куст {i}", x, y, width=60, height=30, color="#e8f4f8")
            well.power_consumption = self.objects_data[f"Куст {i}"]["power"]
            self.wells.append(well)
            placed_wells.append((x, y, 60, 30))

        # Правая часть - параметры
        self.params_frame = tk.Frame(self, width=500, height=800, bg="#f0f0f0")
        self.params_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.main_container = ScrollableNotebookFrame(self.params_frame)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self.notebook = VerticalNotebook(self.main_container.scrollable_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tabs = {}
        for building in self.buildings + self.wells:
            tab = tk.Frame(self.notebook)
            self.tabs[building.name] = tab
            self.notebook.add(tab, text=building.name)
            self.create_building_tab(tab, building)

        # Панель управления
        self.control_frame = tk.Frame(self.params_frame, bg="#f0f0f0")
        self.control_frame.pack(fill=tk.X, pady=10)
        
        self.stats_frame = tk.LabelFrame(self.control_frame, text="Энергетический баланс", bg="#f0f0f0")
        self.stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.generation_label = tk.Label(self.stats_frame, text="Выработка: 0 МВт", bg="#f0f0f0")
        self.generation_label.pack(anchor="w")
        
        self.consumption_label = tk.Label(self.stats_frame, text="Потребление: 0 МВт", bg="#f0f0f0")
        self.consumption_label.pack(anchor="w")
        
        self.balance_label = tk.Label(self.stats_frame, text="Баланс: 0 МВт", bg="#f0f0f0")
        self.balance_label.pack(anchor="w")
        
        btn_save = tk.Button(
            self.control_frame,
            text="Сохранить параметры",
            command=self.save_parameters,
        )
        btn_save.pack(pady=5)

        if self.buildings:
            self.notebook.select(0)

        self.main_container.canvas.bind_all("<MouseWheel>", 
            lambda e: self.main_container.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        self.update_stats()

    def create_building_tab(self, tab, building):
        main_frame = tk.Frame(tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Label(main_frame, text=f"Параметры {building.name}").grid(row=0, column=0, columnspan=2, pady=5)

        if building.name == "ГТЭС":
            tk.Label(main_frame, text="Генерируемая мощность (МВт):").grid(row=1, column=0, sticky="w")
            power_label = tk.Label(main_frame, text=f"{building.power_generation}")
            power_label.grid(row=1, column=1, sticky="e")
        else:
            tk.Label(main_frame, text="Потребляемая мощность (МВт):").grid(row=1, column=0, sticky="w")
            power_label = tk.Label(main_frame, text=f"{building.power_consumption}")
            power_label.grid(row=1, column=1, sticky="e")

        if building.heat_consumption > 0:
            tk.Label(main_frame, text="Нагрузка на отопление (Гкал/ч):").grid(row=2, column=0, sticky="w")
            heat_label = tk.Label(main_frame, text=f"{building.heat_consumption}")
            heat_label.grid(row=2, column=1, sticky="e")

        tk.Label(main_frame, text="Расстояние от ГТЭС (км):").grid(row=3, column=0, sticky="w")
        distance = self.objects_data[building.name]["distance"] if building.name in self.objects_data else 0
        distance_label = tk.Label(main_frame, text=f"{distance}")
        distance_label.grid(row=3, column=1, sticky="e")

        if building.name in self.objects_data:
            tk.Label(main_frame, text="Загрузка (лето/зима):").grid(row=4, column=0, sticky="w")
            load_label = tk.Label(main_frame, 
                                text=f"{self.objects_data[building.name]['summer_load']}% / {self.objects_data[building.name]['winter_load']}%")
            load_label.grid(row=4, column=1, sticky="e")

        if building.name == "ГТЭС":
            tk.Label(main_frame, text="\nУправление турбинами:").grid(row=5, column=0, columnspan=2, pady=(10,0))
            
            turbines_frame = tk.Frame(main_frame)
            turbines_frame.grid(row=6, column=0, columnspan=2, sticky="ew")
            
            for i, turbine in enumerate(building.turbines):
                row = i // 3
                col = i % 3
                
                turbine_frame = tk.Frame(turbines_frame, bd=1, relief=tk.GROOVE, padx=5, pady=5)
                turbine_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                
                tk.Label(turbine_frame, text=f"Турбина {turbine.id}").pack()
                tk.Label(turbine_frame, text=f"{turbine.power} МВт").pack()
                
                btn_state = tk.Button(
                    turbine_frame,
                    text="Выключить" if turbine.active else "Включить",
                    command=lambda t=turbine: self.toggle_turbine(t),
                    width=10
                )
                btn_state.pack(pady=2)
                
                status_indicator = tk.Canvas(turbine_frame, width=20, height=20, highlightthickness=0)
                status_indicator.create_oval(2, 2, 18, 18, fill="green" if turbine.active else "red", outline="black")
                status_indicator.pack()

        if building.name != "ГТЭС":
            tk.Label(main_frame, text="\nСостояние объекта:").grid(row=7, column=0, columnspan=2, pady=(10,0))
            
            self.connection_var = tk.BooleanVar(value=building.connected)
            connection_btn = tk.Checkbutton(
                main_frame,
                text="Подключен к сети",
                variable=self.connection_var,
                command=lambda: self.toggle_building_connection(building),
                indicatoron=False,
                selectcolor="lightgreen" if building.connected else "lightcoral",
                width=15
            )
            connection_btn.grid(row=8, column=0, columnspan=2, pady=5)

        btn_color = tk.Button(
            main_frame,
            text="Изменить цвет",
            command=lambda: self.change_building_color(building),
        )
        btn_color.grid(row=9, column=0, columnspan=2, pady=5)

    def toggle_turbine(self, turbine):
        turbine.toggle()
        gtes = next(b for b in self.buildings if b.name == "ГТЭС")
        gtes.power_generation = sum(t.power for t in gtes.turbines if t.active)
        self.update_stats()
        self.update_building_tab("ГТЭС")

    def toggle_building_connection(self, building):
        building.connected = not building.connected
        self.update_stats()
        self.update_building_tab(building.name)

    def update_building_tab(self, building_name):
        tab = self.tabs[building_name]
        for widget in tab.winfo_children():
            widget.destroy()
        building = next((b for b in self.buildings + self.wells if b.name == building_name), None)
        if building:
            self.create_building_tab(tab, building)

    def change_building_color(self, building):
        color = colorchooser.askcolor()[1]
        if color:
            building.update(color=color)

    def update_stats(self):
        total_generation = sum(b.power_generation for b in self.buildings if hasattr(b, 'power_generation'))
        total_consumption = sum(b.power_consumption for b in self.buildings + self.wells if b.connected and b.name != "ГТЭС")
        balance = total_generation - total_consumption
        
        self.generation_label.config(text=f"Выработка: {total_generation:.1f} МВт")
        self.consumption_label.config(text=f"Потребление: {total_consumption:.1f} МВт")
        self.balance_label.config(text=f"Баланс: {balance:.1f} МВт", 
                                fg="green" if balance >= 0 else "red")

    def save_parameters(self):
        print("Параметры сохранены")

if __name__ == "__main__":
    app = Application()
    app.mainloop()

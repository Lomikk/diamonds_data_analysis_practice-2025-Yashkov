import tkinter as tk
from tkinter import filedialog, messagebox
import data_utils
from pandastable import Table

#pip install pandas pandastable

class EDAApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EDA Application")

        # Хранить DataFrame
        self.df = None

        # Создать основные компоненты интерфейса
        self._create_widgets()

    # ───────────────────────────────── UI ──────────────────────────────────
    def _create_widgets(self):
        # Фрейм для верхних кнопок
        top_frame = tk.Frame(self)
        top_frame.pack(fill=tk.X, padx=5, pady=5)

        # Кнопка загрузки CSV
        load_btn = tk.Button(top_frame, text="Загрузить CSV",
                             command=self._on_load_csv)
        load_btn.pack(side=tk.LEFT, padx=5)

        # Кнопка информации (структура и размер данных)
        info_btn = tk.Button(top_frame, text="Информация о данных",
                             command=self._on_show_info)
        info_btn.pack(side=tk.LEFT, padx=5)

        # Фрейм фильтров (категориальные + числовые)
        self.filter_frame = tk.LabelFrame(self, text="Фильтры")
        self.filter_frame.pack(fill=tk.X, padx=5, pady=5)

        # Плейсхолдер до загрузки данных
        self._filters_placeholder = tk.Label(
            self.filter_frame,
            text="Загрузите CSV, чтобы задать фильтры",
            fg="gray"
        )
        self._filters_placeholder.pack(padx=10, pady=15)

        # Подфрейм категориальных фильтров
        self.cat_frame = tk.LabelFrame(self.filter_frame, text="Категориальные фильтры")
        self.cat_frame.pack(fill=tk.X, padx=5, pady=5)

        # Подфрейм числовых фильтров
        self.num_frame = tk.LabelFrame(self.filter_frame, text="Числовые фильтры")
        self.num_frame.pack(fill=tk.X, padx=5, pady=5)

        # Фрейм для кнопок в одну строку
        button_row = tk.Frame(self)
        button_row.pack(fill=tk.X, padx=5, pady=5)

        # Кнопка применения фильтра
        apply_btn = tk.Button(button_row, text="Применить фильтр",
                              command=self._on_apply_filter)
        apply_btn.pack(side=tk.LEFT, padx=5)

        # Кнопка рекомендаций
        reco_btn = tk.Button(button_row, text="Вывод рекомендаций",
                             command=self._on_show_recommendations)
        reco_btn.pack(side=tk.LEFT, padx=5)

        # Отключить кнопки до загрузки данных
        info_btn.config(state=tk.DISABLED)
        apply_btn.config(state=tk.DISABLED)
        reco_btn.config(state=tk.DISABLED)

        # Сохранить ссылки на кнопки
        self.info_btn = info_btn
        self.apply_btn = apply_btn
        self.reco_btn = reco_btn

        # Строка статуса: сколько записей выбрано
        self.status_label = tk.Label(self, text="Данные не загружены",
                                     anchor="w", fg="gray")
        self.status_label.pack(fill=tk.X, padx=5, pady=(0, 5))

    # ──────────────────────────── Загрузка CSV ────────────────────────────
    def _on_load_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            df = data_utils.load_csv(file_path)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить CSV:\n{e}")
            return

        self.df = df

        # Обновить статус-лейбл
        self.status_label.config(
            text=f"Загружено {len(self.df)} строк",
            fg="black"
        )

        # Включить кнопки
        self.info_btn.config(state=tk.NORMAL)
        self.apply_btn.config(state=tk.NORMAL)
        self.reco_btn.config(state=tk.NORMAL)

        # Перестроить фильтры
        self._build_filters_ui()

    # ─────────────────────── Построение панели фильтров ────────────────────
    def _build_filters_ui(self):
        # Удалить плейсхолдер, если он есть
        if hasattr(self, '_filters_placeholder'):
            self._filters_placeholder.destroy()

        # Очистить старые виджеты
        for child in self.cat_frame.winfo_children():
            child.destroy()
        for child in self.num_frame.winfo_children():
            child.destroy()

        if self.df is None:
            return

        # Категориальные фильтры
        self.selected_cuts = {}
        self.selected_colors = {}
        self.selected_clarities = {}

        cut_frame = tk.LabelFrame(self.cat_frame, text="cut")
        cut_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)

        color_frame = tk.LabelFrame(self.cat_frame, text="color")
        color_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)

        clarity_frame = tk.LabelFrame(self.cat_frame, text="clarity")
        clarity_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)

        if 'cut' in self.df.columns:
            for val in sorted(self.df['cut'].astype(str).unique()):
                var = tk.BooleanVar(value=True)
                tk.Checkbutton(cut_frame, text=val, variable=var).pack(anchor='w')
                self.selected_cuts[val] = var

        if 'color' in self.df.columns:
            for val in sorted(self.df['color'].astype(str).unique()):
                var = tk.BooleanVar(value=True)
                tk.Checkbutton(color_frame, text=val, variable=var).pack(anchor='w')
                self.selected_colors[val] = var

        if 'clarity' in self.df.columns:
            for val in sorted(self.df['clarity'].astype(str).unique()):
                var = tk.BooleanVar(value=True)
                tk.Checkbutton(clarity_frame, text=val, variable=var).pack(anchor='w')
                self.selected_clarities[val] = var

        # Числовые фильтры — carat
        carat_frame = tk.Frame(self.num_frame)
        carat_frame.pack(fill=tk.X, padx=5, pady=2)

        carat_var = tk.BooleanVar(value=False)
        carat_check = tk.Checkbutton(carat_frame, text="carat", variable=carat_var)
        carat_check.pack(side=tk.LEFT)

        carat_min_val = float(self.df['carat'].min()) if 'carat' in self.df.columns else 0.0
        carat_max_val = float(self.df['carat'].max()) if 'carat' in self.df.columns else 0.0

        carat_min_spin = tk.Spinbox(carat_frame, from_=0.0, to=carat_max_val,
                                    increment=0.01, width=8)
        carat_min_spin.pack(side=tk.LEFT, padx=2)
        carat_min_spin.delete(0, tk.END)
        carat_min_spin.insert(0, f"{carat_min_val:.2f}")

        carat_max_spin = tk.Spinbox(carat_frame, from_=0.0, to=carat_max_val,
                                    increment=0.01, width=8)
        carat_max_spin.pack(side=tk.LEFT, padx=2)
        carat_max_spin.delete(0, tk.END)
        carat_max_spin.insert(0, f"{carat_max_val:.2f}")

        def toggle_carat_spin():
            state = tk.NORMAL if carat_var.get() else tk.DISABLED
            carat_min_spin.config(state=state)
            carat_max_spin.config(state=state)

        carat_check.config(command=toggle_carat_spin)
        toggle_carat_spin()

        # Числовые фильтры — price
        price_frame = tk.Frame(self.num_frame)
        price_frame.pack(fill=tk.X, padx=5, pady=2)

        price_var = tk.BooleanVar(value=False)
        price_check = tk.Checkbutton(price_frame, text="price", variable=price_var)
        price_check.pack(side=tk.LEFT)

        price_min_val = float(self.df['price'].min()) if 'price' in self.df.columns else 0.0
        price_max_val = float(self.df['price'].max()) if 'price' in self.df.columns else 0.0

        price_min_spin = tk.Spinbox(price_frame, from_=0, to=price_max_val,
                                    increment=1, width=8)
        price_min_spin.pack(side=tk.LEFT, padx=2)
        price_min_spin.delete(0, tk.END)
        price_min_spin.insert(0, f"{int(price_min_val)}")

        price_max_spin = tk.Spinbox(price_frame, from_=0, to=price_max_val,
                                    increment=1, width=8)
        price_max_spin.pack(side=tk.LEFT, padx=2)
        price_max_spin.delete(0, tk.END)
        price_max_spin.insert(0, f"{int(price_max_val)}")

        def toggle_price_spin():
            state = tk.NORMAL if price_var.get() else tk.DISABLED
            price_min_spin.config(state=state)
            price_max_spin.config(state=state)

        price_check.config(command=toggle_price_spin)
        toggle_price_spin()

        # Сохранить ссылки
        self.carat_var = carat_var
        self.price_var = price_var
        self.carat_min_spin = carat_min_spin
        self.carat_max_spin = carat_max_spin
        self.price_min_spin = price_min_spin
        self.price_max_spin = price_max_spin

    # ────────────────────── Окно «Информация о данных» ─────────────────────
    def _on_show_info(self):
        if self.df is None:
            return

        info_text = data_utils.get_info_string(self.df)

        info_window = tk.Toplevel(self)
        info_window.title("Информация о данных")

        text_widget = tk.Text(info_window, wrap=tk.NONE)
        text_widget.insert(tk.END, info_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True)

    # ──────────────────────── Применение фильтров ───────────────────────────
    def _on_apply_filter(self):
        if self.df is None:
            return

        # Категориальные фильтры
        selected_cuts = [v for v, var in self.selected_cuts.items() if var.get()]
        selected_colors = [v for v, var in self.selected_colors.items() if var.get()]
        selected_clarities = [v for v, var in self.selected_clarities.items() if var.get()]

        # Числовые фильтры
        use_carat = self.carat_var.get()
        use_price = self.price_var.get()

        carat_min = float(self.carat_min_spin.get()) if use_carat else None
        carat_max = float(self.carat_max_spin.get()) if use_carat else None
        price_min = float(self.price_min_spin.get()) if use_price else None
        price_max = float(self.price_max_spin.get()) if use_price else None

        # Функция фильтрации из data_utils
        filtered_df = data_utils.filter_data(
            self.df,
            selected_cuts, selected_colors, selected_clarities,
            carat_min, carat_max, use_carat,
            price_min, price_max, use_price
        )

        # Окно с результатами через pandastable
        result_window = tk.Toplevel(self)
        result_window.title("Результаты фильтрации")

        table_frame = tk.Frame(result_window)
        table_frame.pack(fill=tk.BOTH, expand=True)

        table = Table(
            table_frame,
            dataframe=filtered_df,
            showtoolbar=True,
            showstatusbar=True
        )
        table.show()

        toolbar = table.toolbar

        # Список названий кнопок, которые нужно убрать
        to_remove = [
            "Load table",
           # "Save",
            "Import",
            "Load excel",
            "Copy",
            "Paste",
           # "Plot",
            "Transpose",
           # "Aggregate",
            "Pivot",
            "Melt",
            "Merge",
            "Table from selection",
            "Query",
            "Evaluate function",
            "Stats models",
            "Clear"
        ]

        for btn in toolbar.winfo_children():
            if btn.cget("text") in to_remove:
                btn.destroy()

        # Обновить статус-лейбл
        total_rows = len(self.df)
        filtered_rows = len(filtered_df)
        percent = (filtered_rows / total_rows) * 100 if total_rows else 0
        self.status_label.config(
            text=f"Отфильтровано {filtered_rows} из {total_rows} строк ({percent:.1f} %)",
            fg="black"
        )

    # ─────────────────────────── Окно рекомендаций ─────────────────────────
    def _on_show_recommendations(self):
        if self.df is None:
            return

        rows = data_utils.get_recommendations(self.df)

        reco = tk.Toplevel(self)
        reco.title("Рекомендации")

        # ── таблица «показатель – значение» ───────────────────────────
        for ind, val in rows:
            line = tk.Frame(reco)
            line.pack(fill=tk.X, padx=10, pady=2)

            tk.Label(line, text=ind, width=24, anchor="w",
                     font=("Arial", 10, "bold")).pack(side=tk.LEFT)
            tk.Label(line, text=val, anchor="w") \
                .pack(side=tk.LEFT, fill=tk.X, expand=True)

        # ── разделитель ───────────────────────────────────────────────
        tk.Frame(reco, height=2, bd=1, relief=tk.SUNKEN) \
            .pack(fill=tk.X, padx=10, pady=8)

        # ── статическое пояснение значений ────────────────────────────
        explanation = (
            "Пояснения:\n"
            "• Вес (carat) — главный фактор формирования цены.\n"
            "• Огранка (cut) влияет на блеск и ликвидность; полезно знать, какая\n"
            "  огранка самая массовая и какая приносит наибольшую среднюю цену.\n"
            "• Цвет (color) и чистота (clarity) показывают распределение\n"
            "  ассортимента; топ‑категории помогают ориентировать закупки.\n"
            "• Диапазон цен (IQR и медиана) показывает «ценовой коридор» для 50% сделок,\n"
            "  позволяя сразу увидеть, в каком сегменте сосредоточен основной объём продаж."

        )

        tk.Label(reco, text=explanation, justify="left",
                 anchor="w", wraplength=520).pack(fill=tk.X, padx=10, pady=(0, 10))


# ───────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = EDAApplication()
    app.mainloop()

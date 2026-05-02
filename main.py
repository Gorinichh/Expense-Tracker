import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

# Константы
DATA_FILE = "expenses.json"
CATEGORIES = ["Еда", "Транспорт", "Развлечения", "Жилье", "Здоровье", "Другое"]

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("800x600")

        # Список расходов
        self.expenses = []

        # Загрузка данных
        self.load_data()

        # --- Интерфейс ввода ---
        input_frame = ttk.LabelFrame(root, text="Добавить расход", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Сумма
        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, sticky="w", padx=5)
        self.amount_entry = ttk.Entry(input_frame)
        self.amount_entry.grid(row=0, column=1, padx=5)

        # Категория
        ttk.Label(input_frame, text="Категория:").grid(row=0, column=2, sticky="w", padx=5)
        self.category_var = tk.StringVar(value=CATEGORIES[0])
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, values=CATEGORIES, state="readonly")
        self.category_combo.grid(row=0, column=3, padx=5)

        # Дата
        ttk.Label(input_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=4, sticky="w", padx=5)
        self.date_entry = ttk.Entry(input_frame)
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        self.date_entry.grid(row=0, column=5, padx=5)

        # Кнопка добавления
        add_btn = ttk.Button(input_frame, text="Добавить расход", command=self.add_expense)
        add_btn.grid(row=0, column=6, padx=10)

        # --- Интерфейс фильтрации и итогов ---
        filter_frame = ttk.LabelFrame(root, text="Фильтры и Итоги", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Фильтр по категории:").grid(row=0, column=0, sticky="w", padx=5)
        self.filter_category_var = tk.StringVar(value="Все")
        filter_categories = ["Все"] + CATEGORIES
        self.filter_category_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category_var, values=filter_categories, state="readonly")
        self.filter_category_combo.grid(row=0, column=1, padx=5)
        self.filter_category_combo.bind("<<ComboboxSelected>>", self.apply_filters)

        ttk.Label(filter_frame, text="Дата с (ДД.ММ.ГГГГ):").grid(row=0, column=2, sticky="w", padx=5)
        self.start_date_entry = ttk.Entry(filter_frame, width=12)
        self.start_date_entry.grid(row=0, column=3, padx=5)

        ttk.Label(filter_frame, text="Дата по (ДД.ММ.ГГГГ):").grid(row=0, column=4, sticky="w", padx=5)
        self.end_date_entry = ttk.Entry(filter_frame, width=12)
        self.end_date_entry.grid(row=0, column=5, padx=5)

        filter_btn = ttk.Button(filter_frame, text="Применить фильтр даты", command=self.apply_filters)
        filter_btn.grid(row=0, column=6, padx=5)

        reset_btn = ttk.Button(filter_frame, text="Сброс", command=self.reset_filters)
        reset_btn.grid(row=0, column=7, padx=5)

        # Итоговая сумма
        self.total_label = ttk.Label(filter_frame, text="Итого: 0.00", font=("Arial", 12, "bold"), foreground="blue")
        self.total_label.grid(row=1, column=0, columnspan=8, sticky="w", pady=(10, 0))

        # --- Таблица ---
        table_frame = ttk.Frame(root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("ID", "Date", "Category", "Amount")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Date", text="Дата")
        self.tree.heading("Category", text="Категория")
        self.tree.heading("Amount", text="Сумма")

        self.tree.column("ID", width=50)
        self.tree.column("Date", width=100)
        self.tree.column("Category", width=150)
        self.tree.column("Amount", width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.pack(side=tk.RIGHT, fill="y")

        # Кнопка удаления
        del_btn = ttk.Button(root, text="Удалить выбранный", command=self.delete_expense)
        del_btn.pack(pady=5)

        # Первоначальная отрисовка
        self.refresh_table()

    def validate_input(self, amount_str, date_str):
        """Проверка корректности ввода"""
        # Проверка суммы
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Сумма должна быть положительной")
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Введите корректную положительную сумму.")
            return None

        # Проверка даты
        try:
            date_obj = datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Неверный формат даты. Используйте ДД.ММ.ГГГГ.")
            return None

        return amount, date_obj

    def add_expense(self):
        amount_str = self.amount_entry.get()
        category = self.category_var.get()
        date_str = self.date_entry.get()

        result = self.validate_input(amount_str, date_str)
        if not result:
            return

        amount, date_obj = result
        
        new_expense = {
            "id": len(self.expenses) + 1, # Простой ID, можно улучшить
            "amount": amount,
            "category": category,
            "date": date_obj.strftime("%d.%m.%Y"),
            "timestamp": date_obj.timestamp() # Для удобной сортировки/фильтрации
        }
        
        self.expenses.append(new_expense)
        self.save_data()
        self.refresh_table()
        
        # Очистка поля суммы
        self.amount_entry.delete(0, tk.END)

    def delete_expense(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return
        
        item = self.tree.item(selected_item[0])
        record_id = item['values'][0]
        
        # Удаляем из списка
        self.expenses = [e for e in self.expenses if e['id'] != record_id]
        
        # Пересчитываем ID (опционально, чтобы не было дыр)
        for i, e in enumerate(self.expenses):
            e['id'] = i + 1
            
        self.save_data()
        self.refresh_table()

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=4)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.expenses = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.expenses = []

    def get_filtered_expenses(self):
        filtered = self.expenses[:]
        
        # Фильтр по категории
        cat_filter = self.filter_category_var.get()
        if cat_filter != "Все":
            filtered = [e for e in filtered if e['category'] == cat_filter]
            
        # Фильтр по дате
        start_date_str = self.start_date_entry.get()
        end_date_str = self.end_date_entry.get()
        
        start_date = None
        end_date = None
        
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%d.%m.%Y")
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат 'Дата с'")
                return []
                
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%d.%m.%Y")
                # Добавляем конец дня
                end_date = end_date.replace(hour=23, minute=59, second=59)
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат 'Дата по'")
                return []

        if start_date or end_date:
            temp_filtered = []
            for e in filtered:
                exp_date = datetime.strptime(e['date'], "%d.%m.%Y")
                if start_date and exp_date < start_date:
                    continue
                if end_date and exp_date > end_date:
                    continue
                temp_filtered.append(e)
            filtered = temp_filtered
            
        return filtered

    def apply_filters(self, event=None):
        self.refresh_table()

    def reset_filters(self):
        self.filter_category_var.set("Все")
        self.start_date_entry.delete(0, tk.END)
        self.end_date_entry.delete(0, tk.END)
        self.refresh_table()

    def refresh_table(self):
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        filtered_expenses = self.get_filtered_expenses()
        
        total = 0
        for expense in filtered_expenses:
            self.tree.insert("", tk.END, values=(
                expense['id'],
                expense['date'],
                expense['category'],
                f"{expense['amount']:.2f}"
            ))
            total += expense['amount']
            
        self.total_label.config(text=f"Итого: {total:.2f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()

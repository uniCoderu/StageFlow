# Файл handlers/__init__.py

import os
import importlib

# Автоматически импортируем всё из папки handlers
for module in os.listdir(os.path.dirname(__file__)):
    if module.endswith('.py') and module != '__init__.py':
        module_name = module[:-3]  # Убираем .py
        globals()[module_name] = importlib.import_module(f'.{module_name}', package='handlers')
import logging

# Создаем обработчик для консоли
handler = logging.StreamHandler()

# Создаем форматтер
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Привязываем форматтер к обработчику
handler.setFormatter(formatter)

# Настраиваем корневой логгер
logger = logging.getLogger('my_app')
logger.setLevel(logging.INFO)
logger.addHandler(handler)

logger.info('Приложение запустилось')

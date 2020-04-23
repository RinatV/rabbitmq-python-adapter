# Rabbitmq тесты на Python

Изначально я просто хотел сделать перевод статьи [Connecting Python with RabbitMQ](https://medium.com/@odelucca/recommendation-algorithm-using-python-and-rabbitmq-part-2-connecting-with-rabbitmq-aa0ec933e195)
так как с английским у меня не очень, но основная цель была все же применить rabbitmq 
в деле. Но во время попытки перевода при попощи google переводчика, возникла сложность
такого действия т.к. я не переводчик, а разработчик. Потому проще сделать свою статью.

## О системах обмена сообщениями

Если надо делать обмен между процессами, то конечно есть различные к этому процессу.
Но воспользоваться готовой системой, пусть даже она может больше чем Вам необходимо,
проще, тем более это все сейчас доступно. Есть конечно вероятность неправильного 
использования или пользования сырыми аспектами, но раз уж имеется протокол AMQP,
это должно быть довольно таки надежно.

## Не перевод, а скорее всего конспект

Пусть будет в стиле инструкции, создайте такую структуру проекта:

    RabbitMQ-Python-Adapter/
    │
    ├── rabbitmq_adapter/
    │ ├── __init__.py
    │ └── # Any other file of our module
    │
    ├── config/
    │ ├── config.py
    │ └── # Any config file
    │
    ├── tests/
    │ ├── __init__.py
    │ └── # All integration and unit tests
    │
    └── requirements.txt

Если это делать на Pycharm, то надо добавить: 
* 2 пакета `rabbitmq_adapter` и `tests`
  * в оригинале `rabbitmq-adapter` через тире, возможно под маками или линуксами
  это прокатит, я долго мучался с этим т.к. до этого питон я долго не видел и
  избегал
* файл `requirements.txt`
* и директория `config` с файлом `config.py`
  * директорию надо обозначить как *Source root* чтобы среда Pycharm понимала,
  что это дополнительное место поиска кода т.к. в этом проекте она идет
  как настройки для тестов, тем самым отвязываются тесты от разрабатываемого
  пакета.

Добавьте в тесты файл `tests/test_integration.py`:

    def test_rabbitmq_factory():
        # Должно быть в состоянии создать соединение RabbitMQ
        assert True

    def test_rabbitmq_listen_to_queue():
        # Должен быть в состоянии слушать очередь RabbitMQ
        assert True

    def test_rabbitmq_queue_one_to_many_queue_handler():
        # Должно быть в состоянии иметь отношение «один ко многим» между очередью и функцией-обработчиком.
        assert True

    def test_rabbitmq_send_message():
        # Должен быть в состоянии отправить сообщение в заданной очереди
        assert True
        
В Pycharm надо настроить интеграцию, во вкладке [`File | Settings | Tools | Python Integrated Tools`](jetbrains://Python/settings?name=Tools--Python+Integrated+Tools)
, в параграфе *Testing* надо параметр *Default test runner* выбрать *pytest*. Если pytest
уже установлен, то тесты уже можно запустить, они пройдут успешно.

Если не `pytest` не установлен, то можно его установить или же как в статье привести
файл `requirements.txt` к виду и выполнить `pip install -r requirements.txt` (я сразу
описал окончательную версия):

    pytest
    pytest-env
    pyyaml
    dotmap
    pika
    
    
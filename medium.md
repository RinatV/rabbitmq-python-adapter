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
    
Теперь напишем юнит-тест, т.е. тест который проверяет внутренний код разрабатываемого
пакета `tests/test_channel.py``:

    import pytest
    import rabbitmq_adapter
    import sys
    import os
    from unittest.mock import Mock
    # from tests.__mocks__ import pika
    
    # sys.path.append(os.environ['CONFIG'])
    from config import *
    
    @pytest.mark.unit
    def test_channel_sets_parameters(monkeypatch):
        mocked_pika = Mock()
        mocked_pika.URLParameters.return_value = 'MORTY'
        monkeypatch.setattr('rabbitmq_adapter.channel.pika', mocked_pika)
    
        rabbitmq_adapter.channel.create('MORTY HOST')
    
        mocked_pika.URLParameters.assert_called_once_with('MORTY HOST')
    
    @pytest.mark.unit
    def test_channel_creates_connection(monkeypatch):
        mocked_pika = Mock()
        mocked_pika.URLParameters.return_value = 'MORTY'
        # mocked_pika.BlockingConnection.return_value = pika.Connection()
        monkeypatch.setattr('rabbitmq_adapter.channel.pika', mocked_pika)
    
        rabbitmq_adapter.channel.create('MORTY HOST')
    
        mocked_pika.BlockingConnection.assert_called_once_with('MORTY')    
    
С помощью mockов - заглушек проверяется взаимодействие тестируемого кода
с используемыми интерфейсами, для этого нет необходимости знать внутреннее устройство
реализаций интерфейса, а достаточно проверять контракт. Остается разработать наш 
класс адаптер `rabbitmq_adapter/channel.py`:

    import pika
    
    def create(host):
        params = pika.URLParameters(host)
        # connection = pika.BlockingConnection(params)
    
        # return connection.channel()

Первая строка метода `create` проверяется тестом `test_channel_sets_parameters(monkeypatch)`,
следующая строка вторым юнит-тестом, возвращаемый объект видимо пригодится уже в 
интеграционных тестах, с реальным сервером. Из исходной статьи на этом этапе пока не 
используется файл `tests/__mocks__/pika.py` из теста у меня убрано его использование,
тесты без этого пока тоже проходят, если коментить входные параметры, то тесты
проваливаются, думаю выясним для чего нужны эти файлы в дальнейщем. Также закоменчена
строка использования переменной среды `CONFIG`, т.к. пока она не вычисляется, и в ней
нет необходимости.

Зарядим первый интеграционный тест:

    import pytest
    import rabbitmq_adapter
    import sys
    import os
    from time import sleep
    
    # sys.path.append(os.environ['CONFIG'])
    from config import *
    
    def setup_listener(
        channel,
        on_message_callback,
        queue=config.rabbitmq.queue,
        exchange=config.rabbitmq.exchange,
        durable=False,
        prefetch_count=config.rabbitmq.prefetch.count
    ):
        channel.queue_declare(queue=queue, durable=durable)
        channel.queue_bind(queue=queue, exchange=exchange)
        channel.basic_qos(prefetch_count=prefetch_count)
        channel.basic_consume(queue=queue, on_message_callback=on_message_callback)
    
        return channel
    
    def wait_for_result(
        anchor,
        tries=0,
        retry_after=.6
    ):
        if len(anchor) > 0 or tries > 5: assert len(anchor) > 0
        else:
            sleep(retry_after)
            return wait_for_result(anchor, tries + 1)
    
    @pytest.mark.integration
    def test_rabbitmq_factory():
        # Should be able to create a RabbitMQ connection
        calls = []
        def mocked_handler(ch, method, props, body):
            calls.append(1)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            ch.close()
    
        rabbitmq_channel = rabbitmq_adapter.channel.create(config.rabbitmq.host)
        rabbitmq_channel = setup_listener(rabbitmq_channel, mocked_handler)
        rabbitmq_channel.basic_publish(
            exchange=config.rabbitmq.exchange,
            routing_key=config.rabbitmq.queue,
            body='MORTY'
        )
    
        rabbitmq_channel.start_consuming()
        # wait_for_result(calls)
    
    def test_rabbitmq_listen_to_queue():
        # Should be able to listen to a RabbitMQ queue
        assert True
    
    def test_rabbitmq_queue_one_to_many_queue_handler():
        # Should be able to have an one-to-many relationship between the queue and the handler function
        assert True
    
    def test_rabbitmq_send_message():
        # Should be able to send a message in a given queue
        assert True
     
Пока файл `config/config.py` пустой Pycharm на это будет ругаться, заполним файл:

    import os
    import yaml
    from pathlib import Path
    from dotmap import DotMap
    
    def load_only_current_env(config):
        configs = yaml.load(config)
        return configs[os.environ['ENV']]
    
    config_files = [os.path.join(r, file) for r, d, f in os.walk(os.environ['CONFIG']) for file in f if '.yaml' in file]
    config = DotMap({Path(cfg).stem: load_only_current_env(open(cfg, 'r')) for cfg in config_files})

Вот сейчас нам становиться нужна переменная среды `CONFIG, для этого заведем файл 
`pytest.ini`

    [pytest]
    markers =
      integration
      unit
    env =
      ENV=test
      CONFIG={PWD}/config/
  
 Сейчас уже становится нужным переменная среды `PWD`, его конечно можно заменить в
 конфигурационном файле `CONFIG=../config/` будет работать, я же его прописал
 в конфигурацию запуска тестов Pycharm `PWD=..`.
 
 Чтобы тесты могли видеть настройки для соединения с сервером заполним файл
 `rabbitmq.yaml`, rabbitmq у меня локальный:
 
    test:
      host: 'amqp://localhost'
      exchange: 'amq.direct'
      queue: 'TEST::NEW'
      prefetch:
        count: 1
        
После того как в файле `rabbitmq_adapter/channel.py` были раскоменченные все
строки, интеграционный тест прошел. Если сервер остановить, то тест проваливается.
Строку `wait_for_result(calls)` я тоже закоментировал, тест работает также как и
работал.

Пока наблюдения такие:
 * Можем проверить правильно ли используем интерфейсы
 * Каким-то образом устанавливаем соединение, на сервере появляется очередь `TEST:NEW`

Посмотрим далее, автор обозначает следующие цели:

* Объявите очередь: это не интуитивно понятно, но мы можем 
прослушивать только те очереди, которые уже созданы на нашем сервере. 
Итак, если мы попытаемся прослушать несуществующую очередь, наш 
скрипт выдаст ошибку.
    
* Привязать к очереди: для прослушивания очереди нам необходимо 
связать эту очередь с обменом. Обмен - это в основном набор правил 
для упорядочения сообщений между отправителями и получателями. 
Существует четыре типа обмена: прямой, тематический, заголовки и 
разветвление. Я не буду углубляться в это, но мы собираемся 
использовать прямой обмен.

* Задайте количество неподтвержденных сообщений: эта точка 
указывается параметром basic_qos. Идея состоит в том, чтобы 
установить, сколько сообщений служба получит от сервера RabbitMQ.

* Начните потреблять новые сообщения: это действительно интуитивно 
понятно, оно в основном начинает получать сообщения и отправлять их 
в функцию-обработчик.

Добавим модульный тест `tests\test_listener.py`:

    import pytest
    import rabbitmq_adapter
    import sys
    import os
    from unittest.mock import Mock
    from tests.__mocks__ import pika
    
    # sys.path.append(os.environ['CONFIG'])
    from config import *
    
    def mocked_handler(): pass
    
    @pytest.mark.unit
    def test_listener_subscribe_queue_declared(monkeypatch):
        channel = pika.Channel()
        channel.queue_declare = Mock()
    
        rabbitmq_adapter.listener.subscribe(channel, mocked_handler)
    
        channel.queue_declare.assert_called_once_with(
            queue=config.rabbitmq.queue,
            durable=True
        )
    
    @pytest.mark.unit
    def test_listener_subscribe_queue_bind(monkeypatch):
        channel = pika.Channel()
        channel.queue_bind = Mock()
    
        rabbitmq_adapter.listener.subscribe(channel, mocked_handler)
    
        channel.queue_bind.assert_called_once_with(
            queue=config.rabbitmq.queue,
            exchange=config.rabbitmq.exchange
        )
    
    @pytest.mark.unit
    def test_listener_subscribe_basic_qos(monkeypatch):
        channel = pika.Channel()
        channel.basic_qos = Mock()
    
        rabbitmq_adapter.listener.subscribe(channel, mocked_handler)
    
        channel.basic_qos.assert_called_once_with(prefetch_count=config.rabbitmq.prefetch.count)
    
    @pytest.mark.unit
    def test_listener_subscribe_basic_consume(monkeypatch):
        channel = pika.Channel()
        channel.basic_consume = Mock()
    
        rabbitmq_adapter.listener.subscribe(channel, mocked_handler)
    
        channel.basic_consume.assert_called_once_with(
            queue=config.rabbitmq.queue,
            on_message_callback=mocked_handler
        )

разрабатываемый функционал `rabbitmq_adapter\listener.py`:

    import sys
    import os
    
    # sys.path.append(os.environ['CONFIG'])
    from config import *
    
    def subscribe(
        channel,
        handler,
        queue=config.rabbitmq.queue,
        durable=config.rabbitmq.durable,
        exchange=config.rabbitmq.exchange,
        prefetch_count=config.rabbitmq.prefetch.count
    ):
        channel.queue_declare(queue=queue, durable=durable)
        channel.queue_bind(queue=queue, exchange=exchange)
        channel.basic_qos(prefetch_count=prefetch_count)
        channel.basic_consume(queue=queue, on_message_callback=handler)

Также надо уже настраивать импорты с разрабатываемого модуля `rabbitmq_adapter\__init__.py`:

    import rabbitmq_adapter.channel
    import rabbitmq_adapter.listener

В тестовую конфигурацию `config\rabbitmq.yaml` добавляется строка с параметром `durable`:

    test:
      host: 'amqp://localhost'
      exchange: 'amq.direct'
      queue: 'TEST::NEW'
      durable: True
      prefetch:
        count: 1

И нам наконец становится нужным заглушка `tests\__mocks__\pika.py`, он начинает 
приобретать неинтересные на момент тестирования части, если посмотреть на описанный
выше тест, то становиться ясно что функционал `listener` надо проверять на работу,
при этом интересен только вызов одного метода интерфейса, хотя конечно можно было
проверять все сразу:

    class Channel:
        def __init__(self): pass
        def exchange_declare(self): pass
        def queue_declare(self, queue, durable): pass
        def queue_bind(self, queue, exchange): pass
        def basic_qos(self, prefetch_count): pass
        def basic_consume(self, queue, on_message_callback): pass
        def start_consuming(self): pass
        def basic_publish(self): pass
        def basic_ack(self): pass
    
    class Connection:
        def __init__(self): pass
        def channel(self): return Channel()
        
Обратите внимание на использование объекта `config` в по умолчанию параметрах 
`listener.py`, насколько это удобно и практично. В простых приложениях наврняка
параметры всегда будут по умолчанию т.е. те что описаны в конфигурационном файле,
для более многопользовательских объект `config` можно сделать динамическим.
только если `listener` используется два раза в одном приложении вероятно
придется передавать параметры "программно", хотя это конечно мое первое впечатление.

Что же реализуем следующий интеграционный тест:

    ## .........
    @pytest.mark.integration
    def test_rabbitmq_listen_to_queue():
        # Should be able to listen to a RabbitMQ queue
        calls = []
        rabbitmq_channel = rabbitmq_adapter.channel.create(config.rabbitmq.host)
    
        def mocked_handler(ch, method, props, body):
            calls.append(1)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            ch.close()
    
        rabbitmq_adapter.listener.subscribe(rabbitmq_channel, mocked_handler, durable=False)
        rabbitmq_channel.basic_publish(
            exchange=config.rabbitmq.exchange,
            routing_key=config.rabbitmq.queue,
            body='MORTY'
        )
    
        rabbitmq_channel.start_consuming()
        wait_for_result(calls)
    
    ## .........

Все работает, этот тест очень похож на предыдущий, добавлен только `listener.subscribe`.
Автор отметил новый пункт заслуг:

    Уметь слушать очередь, запускать функцию каждый раз, когда получает новое сообщение → (готово)
    


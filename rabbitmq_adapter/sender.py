from config import *


def publish(
        channel,
        body,
        queue=config.rabbitmq.queue,
        exchange=config.rabbitmq.exchange
):
    channel.basic_publish(routing_key=queue, exchange=exchange, body=body)

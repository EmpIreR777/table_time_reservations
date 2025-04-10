from faststream.rabbit import RabbitBroker

broker = RabbitBroker("amqp://admin:password@localhost:5672/myapp_vhost")


@broker.subscriber("test")
async def handle(msg):
    print(f"Получено: {msg}")


async def main():
    await broker.start()
    await broker.publish("test", queue="test")
if __name__ == "__main__":
    import asyncio

    asyncio.run(main()) 
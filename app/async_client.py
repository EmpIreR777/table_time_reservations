from contextlib import asynccontextmanager
from typing import List
import asyncio
import logging
import httpx


class HTTPClientManager:
    def __init__(self, pool_size: int = 5, **client_kwargs):
        """
        Инициализация менеджера HTTP-клиентов.
        """
        if pool_size <= 0:
            raise ValueError('Значение pool_size должно быть положительным целым числом')

        self._clients: List[httpx.AsyncClient] = []  # Пул клиентов
        self._pool_size = pool_size  # Максимальный размер пула
        self._client_kwargs = client_kwargs  # Аргументы для создания клиента
        self._lock = asyncio.Lock()  # Блокировка для обеспечения потокобезопасности

        if "timeout" not in self._client_kwargs:
            self._client_kwargs["timeout"] = 30.0

    async def get_client(self) -> httpx.AsyncClient:
        """
        Получение клиента из пула. Если пул пуст, создается новый клиент.
        """
        async with self._lock:
            if len(self._clients) < self._pool_size:
                logging.info(f'Создание нового клиента. Размер пула: {len(self._clients)}/{self._pool_size}')
                try:
                    # Создаем новый клиент с переданными параметрами (включая timeout)
                    client = httpx.AsyncClient(**self._client_kwargs)
                    self._clients.append(client)
                    return client
                except Exception as e:
                    logging.error(f'Не удалось создать HTTP-клиент: {e}')
                    raise RuntimeError(f'Не удалось создать HTTP-клиент: {e}')
            else:
                logging.info(f'Использование клиента из пула. Размер пула: {len(self._clients)}/{self._pool_size}')
                return self._clients.pop(0)  # Возвращаем первый клиент из пула

    async def release_client(self, client: httpx.AsyncClient):
        """
        Возвращение клиента в пул. Если пул заполнен, клиент закрывается.
        """
        async with self._lock:
            if client.is_closed:
                logging.warning('Попытка вернуть закрытый клиент в пул.')
                return
            if len(self._clients) < self._pool_size:
                self._clients.append(client) # Возвращаем клиент в пул
            else:
                await client.aclose() # Закрываем клиент, если пул заполнен

    async def close_client(self, client: httpx.AsyncClient):
        """
        Закрытие клиента и удаление его из пула.
        """
        async with self._lock:
            if client not in self._clients:
                raise ValueError('Предоставленный клиент не управляется этим HTTPClientManager')
            try:
                await client.aclose()  # Закрываем клиент
                self._clients.remove(client)  # Удаляем клиент из пула
            except Exception as e:
                logging.error(f'Не удалось закрыть клиент: {e}')

    async def close_all_clients(self):
        """
        Закрытие всех клиентов в пуле.
        """
        async with self._lock:
            for client in self._clients[:]:  # Используем копию списка для безопасного удаления
                try:
                    await client.aclose()  # Закрываем клиент
                except Exception as e:
                    logging.error(f'Не удалось закрыть клиент: {e}')
                    raise f'Ошибки при закрытии клиентов: {e}'
                finally:
                    self._clients.remove(client)  # Удаляем клиент из пула

    @asynccontextmanager
    async def client(self):
        """
        Асинхронный контекстный менеджер для работы с клиентом.
        """
        client = await self.get_client()  # Получаем клиент из пула
        try:
            yield client
        except Exception as e:
            logging.error(f'Ошибка при работе с HTTP-клиентом: {e}')
            raise
        finally:
            await self.release_client(client)  # Возвращаем клиент в пул


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

http_client_manager = HTTPClientManager()

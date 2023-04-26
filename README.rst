===========
AIOMonobank
===========

Asynchronous Python library for `monobank <https://api.monobank.ua/docs>`_ API


.. image:: https://img.shields.io/pypi/l/aiomonobank.svg?style=flat-square
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

.. image:: https://img.shields.io/pypi/status/aiomonobank.svg?style=flat-square
    :target: https://pypi.python.org/pypi/aiomonobank
    :alt: PyPi status

.. image:: https://img.shields.io/pypi/v/aiomonobank.svg?style=flat-square
    :target: https://pypi.python.org/pypi/aiomonobank
    :alt: PyPi Package Version

.. image:: https://img.shields.io/pypi/dm/aiomonobank.svg?style=flat-square
    :target: https://pypi.python.org/pypi/aiomonobank
    :alt: Downloads

.. image:: https://img.shields.io/pypi/pyversions/aiomonobank.svg?style=flat-square
    :target: https://pypi.python.org/pypi/aiomonobank
    :alt: Supported python versions

Setup
=====

- You get token for your client from `MonobankAPI <https://api.monobank.ua/>`_.
- Install the **latest version** of the **aiomonobank**: ``pip install aiomonobank``


Examples
========

    We currently have 2 different classes for using the Monobank API.
- ``MonoPublic`` is simple base class for others, can only get currencies
- ``MonoPersonal`` - this class for talk to personal Monobank API


`get_currency <https://api.monobank.ua/docs/#tag/Publichni-dani/paths/~1bank~1currency/get>`_ request
-----------------------------------------------------------------------------------------------

.. code-block:: python

    import json
    import asyncio

    from aiomonobank import MonoPublic


    async def main():
        async with MonoPublic() as mono_client:
            currency = await mono_client.get_currency()

        print(json.dumps(currency, ensure_ascii=False, indent=4))


    if __name__ == '__main__':
        asyncio.run(main())


`get_client_info <https://api.monobank.ua/docs/#tag/Kliyentski-personalni-dani/paths/~1personal~1client-info/get>`_ request
--------------------------------------------------------------------------------------------------------------------------

.. code-block:: python

    import json
    import asyncio

    from aiomonobank import MonoPersonal

    MONOBANK_API_TOKEN = 'your_token'


    async def main():
        mono_client = MonoPersonal(MONOBANK_API_TOKEN)
        try:
            client_info = await mono_client.get_client_info()

            print(json.dumps(client_info, ensure_ascii=False, indent=4))
        finally:
            await mono_client.close()


    if __name__ == '__main__':
        asyncio.run(main())


`get_statement <https://api.monobank.ua/docs/#tag/Kliyentski-personalni-dani/paths/~1personal~1statement~1{account}~1{from}~1{to}/get>`_ request
-----------------------------------------------------------------------------------------------------------------------------------------------

.. code-block:: python

    import json
    import asyncio
    from datetime import datetime, timedelta

    from aiomonobank import MonoPersonal

    MONOBANK_API_TOKEN = 'your_token'


    async def main():
        mono_client = MonoPersonal(MONOBANK_API_TOKEN)
        try:
            transactions = await mono_client.get_statement(
                account_id='0',
                from_datetime=datetime.utcnow() - timedelta(days=3),
                to_datetime=datetime.utcnow() - timedelta(days=2)
            )

            print(json.dumps(transactions, ensure_ascii=False, indent=4))
        finally:
            await mono_client.close()


    if __name__ == '__main__':
        asyncio.run(main())


Resources:
==========

- PyPI: `aiomonobank <https://pypi.org/project/aiomonobank>`_
- Documentation: (soon)

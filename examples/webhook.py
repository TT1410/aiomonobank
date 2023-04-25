import json
import logging
from http import HTTPStatus

from aiohttp import web
from aiomonobank import MonoPersonal, types

WEBHOOK_HOST = "https://example.com"
WEBAPP_HOST = "localhost"
WEBAPP_PORT = 8822
MONOBANK_API_TOKEN = 'your_token'

logger = logging.getLogger(__name__)

mono_client = MonoPersonal(MONOBANK_API_TOKEN)

router = web.RouteTableDef()


@router.get("/{token}")
async def check_webhook_url(request: web.Request, token: str) -> web.Response:
    """
    The check_webhook_url function is used to check the webhook URL.

    :param request: web.Request: Get the request object
    :param token: str: Check the token from the webhook url
    :return: A response with the status code 200
    """
    if token == MONOBANK_API_TOKEN:
        logger.debug(f"Successful check webhook URL path: {request.path}")

        return web.json_response(status=HTTPStatus.OK)

    return web.json_response(status=HTTPStatus.FORBIDDEN)


@router.post("/{token}")
async def new_transaction(request: web.Request, token: str) -> web.Response:
    """
    The new_transaction function is a webhook handler for the new transaction event.
    It receives a request from the Monobank API and returns an HTTP response with status code 200.
    The function also logs information about the new transaction.

    :param request: web.Request: Receive the request data
    :param token: str: Check the authenticity of the request
    :return: The status code 200
    """
    webhook_data = types.WebhookData(
        **await request.json()
    )

    if webhook_data.type == "StatementItem":
        logger.debug(f"The account ID of the new transaction: {webhook_data.data.account_id}. "
                     f"Sum: {webhook_data.data.statement.amount} UAH")

        print(json.dumps(webhook_data, ensure_ascii=False, indent=4))

    return web.json_response(status=HTTPStatus.OK)


async def on_startup(app: web.Application):
    result = await mono_client.set_webhook(f"{WEBHOOK_HOST}/{MONOBANK_API_TOKEN}")
    logger.debug(f'Wet webhook result: {result}')


async def on_shutdown(app: web.Application):
    await mono_client.close()


def main() -> None:
    """
    The main function is the entry point for this application.
    It creates an instance of a web.Application object, and then calls run_app() to start the server listening on port 8080.
    The app's startup and shutdown hooks are also registered here.

    :return: None, so it will not be used by the server
    """
    try:
        app = web.Application()

        app.on_startup.append(on_startup)
        app.on_shutdown.append(on_shutdown)

        logger.warning('Start...')

        web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)
    finally:
        logger.warning('Closed...')


if __name__ == '__main__':
    main()

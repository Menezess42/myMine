import os
import sys
from pathlib import Path

import grpc

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "generated"))

import myMine_pb2
import myMine_pb2_grpc


RUNTIME_DIR = Path(
    os.environ.get("XDG_RUNTIME_DIR", "/tmp")
)

SOCKET_PATH = RUNTIME_DIR / f"myMine-daemon-{os.getuid()}.sock"
SOCKET_ADDRESS = f"unix://{SOCKET_PATH}"


def main():
    print(f"[cli] Conectando ao daemon em {SOCKET_ADDRESS}")

    try:
        with grpc.insecure_channel(SOCKET_ADDRESS) as channel:
            client = myMine_pb2_grpc.myMineServiceStub(channel)

            response = client.Ping(
                myMine_pb2.PingRequest(
                    message="Oi, daemon!",
                ),
                timeout=3,
            )

            print(f"[cli] Resposta: {response.message}")

    except grpc.RpcError as error:
        print(f"[cli] Falha na comunicação: {error.code()}")
        print(error.details())
        sys.exit(1)


if __name__ == "__main__":
    main()
# import click
#
#
# def startServer():
#     """
#     Safely starts the main server
#     """
#     ...
#
#
# def verifyServer():
#     """
#     Verify if server is up and running
#     """
#     ...
#
#
# def safelyKillServer():
#     """
#     Safely stop and killing the server
#     """
#     ...
#
#
# @click.group()
# def cli():
#     """
#     Bundle all the commands together
#     """
#     pass
#
#
# @click.command()
# def bee():
#     serverStatus = verifyServer()
#     if serverStatus:
#         click.echo("Opening mine!")
#     else:
#         click.echo("Starting server")
#         startServer()
#         click.echo("Opening mine!")
#
#
# @click.command()
# def kbee():
#     click.echo("Killing Server")
#     safelyKillServer()
#     click.echo("Server killed")
#
#
# cli.add_command(bee)
# cli.add_command(kbee)
#
#
# if __name__ == "__main__":
#     """this is a temp format for development purpose. After the CLI is finished and goes to production this will be replaced by entry points"""
#     cli()

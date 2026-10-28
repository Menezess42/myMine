# Babe steps:
# 1- Have something that can be up and runing [ ]
# 2- Have something that can listens [ ]
# 3- Have something that can process what did listen [ ]
# 4- Have something that can responde [ ]
# 5- Deal with signals [ ]
# 6 - Call child(modular tools) [ ]
# 7 - Comunicate with child [ ]

import os
import sys
import signal
from concurrent import futures
from pathlib import Path

import grpc

# Permite importar os módulos gerados.
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "generated"))

import myMine_pb2
import myMine_pb2_grpc


RUNTIME_DIR = Path(
    os.environ.get("XDG_RUNTIME_DIR", "/tmp")
)

SOCKET_PATH = RUNTIME_DIR / f"myMine-daemon-{os.getuid()}.sock"
SOCKET_ADDRESS = f"unix://{SOCKET_PATH}"


class myMineService(myMine_pb2_grpc.myMineServiceServicer):
    def Ping(self, request, context):
        print(f"[daemon] Recebi: {request.message}")

        return myMine_pb2.PingResponse(
            message=f"Olá, CLI! Recebi: {request.message}"
        )


def main():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=4)
    )

    myMine_pb2_grpc.add_myMineServiceServicer_to_server(
        myMineService(),
        server,
    )

    # Este protótipo pressupõe que não existe outra
    # instância usando este socket.
    if SOCKET_PATH.exists():
        raise RuntimeError(
            f"Socket já existe: {SOCKET_PATH}. "
            "Verifique se o daemon já está rodando."
        )

    if not server.add_insecure_port(SOCKET_ADDRESS):
        raise RuntimeError(
            f"Não foi possível abrir {SOCKET_ADDRESS}"
        )

    server.start()

    print(f"[daemon] Rodando em {SOCKET_ADDRESS}")
    print("[daemon] Aguardando chamadas RPC...")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\n[daemon] Encerrando...")
    finally:
        server.stop(grace=0).wait()
        SOCKET_PATH.unlink(missing_ok=True)


if __name__ == "__main__":
    main()

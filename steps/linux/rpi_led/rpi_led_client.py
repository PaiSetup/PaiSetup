#!/bin/python


import enum
import errno  # Linux-only
import os
import select
import socket  # Linux-only
import threading
import time

import watchdog.events
import watchdog.observers

server_address = "192.168.100.36"
server_port = 30123
connect_timeout = 1
send_interval = 8
home_path = os.environ["HOME"]
config_path = f"{home_path}/.config/PaiSetup/rpi_led_config"


class ThreadState:
    def __init__(self, target_function):
        self.thread = threading.Thread(target=target_function)
        self.condition = threading.Condition()
        self.kill_event = threading.Event()

    def start(self):
        self.thread.start()

    def kill(self):
        with self.condition:
            self.kill_event.set()
            self.condition.notify()

    def join(self):
        self.thread.join()


class LedThread(ThreadState):
    class ConnectResult(enum.Enum):
        Success = enum.auto()
        Error = enum.auto()
        Killed = enum.auto()
        Timeout = enum.auto()

    def __init__(self):
        super().__init__(self._main)
        self._connection_stop_signal = socket.socketpair()

        self.update_event = threading.Event()
        self.message = ""

    def kill(self):
        with self.condition:
            self._connection_stop_signal[1].send(b"stop")
            self.kill_event.set()
            self.condition.notify()

    def join(self):
        self.thread.join()
        self._connection_stop_signal[0].close
        self._connection_stop_signal[1].close

    def get_led_message(self):
        if not self.message.endswith("\n"):
            self.message = f"{self.message}\n"
        return self.message.encode("ascii")

    def _main(self):
        while not self.kill_event.is_set():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                # Try to connect to the server. In case of connection errors, wait for
                # a while and retry with a new socket.
                connect_result, connect_data = self._connect_to_server(sock)
                match connect_result:
                    case LedThread.ConnectResult.Success:
                        print("Connected")
                    case LedThread.ConnectResult.Error:
                        print(f"Connection error ({connect_data})")  # TODO make sure we waited for at least connect_timeout
                        continue
                    case LedThread.ConnectResult.Killed:
                        break
                    case LedThread.ConnectResult.Timeout:
                        print("Connection timeout")
                        continue

                try:
                    self._communicate_with_server(sock)
                except (BrokenPipeError, ConnectionResetError):
                    print("Disconnected")

        print("Led thread finishing...")

    def _connect_to_server(self, sock_fd):
        sock_fd.setblocking(False)
        connect_result = sock_fd.connect_ex((server_address, server_port))
        if connect_result == 0:
            return (LedThread.ConnectResult.Success, "")
        if connect_result != errno.EINPROGRESS:
            error_string = f"{errno.errorcode[connect_result]} - {os.strerror(connect_result)}"
            return (LedThread.ConnectResult.Error, error_string)

        # Wait for either stop signal or socket connection
        stop_fd = self._connection_stop_signal[0]
        readable, writable, _ = select.select([stop_fd], [sock_fd], [], connect_timeout)

        # If stop fd is ready, we have been killed by the main thread
        if stop_fd in readable and self.kill_event.is_set():
            return (LedThread.ConnectResult.Killed, "")

        # If socket fd is ready, we need to check the result
        if sock_fd in writable:
            connect_result = sock_fd.connect_ex((server_address, server_port))
            if connect_result in [0, errno.EISCONN]:
                return (LedThread.ConnectResult.Success, "")
            else:
                error_string = f"{errno.errorcode[connect_result]} - {os.strerror(connect_result)}"
                return (LedThread.ConnectResult.Error, error_string)

        # If neither stop fd nor socket fd was ready, it means we have
        # timed out from select().
        return (LedThread.ConnectResult.Timeout, "")

    def _communicate_with_server(self, sock):
        sock.sendall(led_state.get_led_message())
        while True:
            with led_state.condition:
                was_notified = led_state.condition.wait(send_interval)

                # If update_event is set, ObserverThread gave us new data. Send it to the RPI.
                if led_state.update_event.is_set():
                    led_state.update_event.clear()
                    sock.sendall(led_state.get_led_message())
                    print(f'Updating LED to "{led_state.message.strip()}"')

                # If kill_event is set, main thread got interrupted. End execution.
                if led_state.kill_event.is_set():
                    break

                # If the wait timed out, periodically check if the socket is still open. Server
                # never sends anything, so we can use recv() to test this.
                if not was_notified:
                    try:
                        sock.recv(1)  # Returns empty byte array when socket is closed.
                        break
                    except BlockingIOError:
                        pass


class ObserverThread(ThreadState):
    def __init__(self):
        super().__init__(self._main)

    def _main(self):
        self._notify_led()

        def on_config_modified(event):
            if event.src_path == config_path:
                self._notify_led()

        event_handler = watchdog.events.FileSystemEventHandler()
        event_handler.on_modified = on_config_modified
        event_handler.on_created = on_config_modified
        observer = watchdog.observers.Observer()
        observer.schedule(event_handler, config_path)
        observer.start()

        while True:
            with self.condition:
                self.condition.wait()
                if self.kill_event.is_set():
                    break

        observer.stop()
        observer.join()
        print("Observer thread finishing...")

    def _read_config(self):
        try:
            with open(config_path, "r") as file:
                return file.readline()
        except:
            return "\n"

    def _notify_led(self):
        with led_state.condition:
            led_state.message = self._read_config()
            led_state.update_event.set()
            led_state.condition.notify()


# Setup threads
observer_thread = ObserverThread()
led_state = LedThread()
threads = [observer_thread, led_state]

# Start threads
for t in threads:
    t.start()

# Wait for threads to finish. They will never actually finish on their own, but
# we will kill them when user presses Ctrl+C.
try:
    for t in threads:
        t.join()
except KeyboardInterrupt:
    print("Interrupt detected. Exiting...")
    for t in threads:
        t.kill()
    for t in threads:
        t.join()

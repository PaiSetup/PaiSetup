#!/bin/python


import enum
import errno  # Linux-only
import os
import select  # Linux-only
import socket
import threading
import time

from steps.linux.rpi_led.client.led_state import LedState, fifo_file_path

server_port = 30123
connect_timeout = 1
minimum_send_interval = 0.015
# Using hostname would be better, but it doesn't work. We're currently setting hostname on RPI to "RpiLed",
# but it's not visible from PC. See https://github.com/orgs/micropython/discussions/15562
server_address = "192.168.100.36"


class Thread:
    def __init__(self, target_function):
        self.thread = threading.Thread(target=target_function)
        self.condition = threading.Condition()
        self.kill_event = threading.Event()
        self._connection_stop_signal = socket.socketpair()

    def start(self):
        self.thread.start()

    def kill(self):
        with self.condition:
            self._connection_stop_signal[1].send(b"stop")
            self.kill_event.set()
            self.condition.notify()

    def join(self):
        self.thread.join()
        self._connection_stop_signal[0].close
        self._connection_stop_signal[1].close


class LedThread(Thread):
    class ConnectResult(enum.Enum):
        Success = enum.auto()
        Error = enum.auto()
        Killed = enum.auto()
        Timeout = enum.auto()

    def __init__(self, initial_led_state):
        super().__init__(self._main)
        self.led_state = initial_led_state
        self.update_event = threading.Event()
        self._last_send_time = None

    def _main(self):
        while not self.kill_event.is_set():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                # Try to connect to the server. In case of connection errors, wait for
                # a while and retry with a new socket.
                connect_result, connect_data = self._connect_to_server(sock)
                match connect_result:
                    case LedThread.ConnectResult.Success:
                        print("LED: Connected")
                    case LedThread.ConnectResult.Error:
                        print(f"LED: Connection error ({connect_data})")  # TODO make sure we waited for at least connect_timeout
                        continue
                    case LedThread.ConnectResult.Killed:
                        break
                    case LedThread.ConnectResult.Timeout:
                        print("LED: Connection timeout")
                        continue

                try:
                    self._communicate_with_server(sock)
                except (BrokenPipeError, ConnectionResetError):
                    print("LED: Disconnected")

        print("LED: Finishing...")

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
        # Initial send.
        self._send_to_server(sock)

        # Pacing variable. RPI Pico is not a very powerful machine and we cannot send messages at arbitrary
        # frequency. We have to pace it to some minimum interval between to sends to not stress the PRI too
        # much. Before each send we will check whether the time interval between sends is not too small. If
        # it is, we'll enter pacing mode and ignore all send requests until it ends. When pacing mode ends
        # we will perform one send with the most recent data.
        pacing_send_time = None

        while True:
            with self.condition:
                # Wait for something to happen. Other threads can notify us (wake us up) through
                # the condition variable when state changes. We have a default timeout to regularly
                # wake up and check whether we're still connected. But if we're in pacing mode, we'll
                # calculate a timeout to wake us up and perform a send that we previously deferred.
                timeout = connect_timeout
                if pacing_send_time is not None:
                    timeout = pacing_send_time - time.time()  # is negative timeout okay? I think so.
                was_timeout = not self.condition.wait(timeout)

                # If the wait timed out in pacing mode, pace period ended and we can perform a deferred send.
                # If the wait timed out while not in pacing mode, check if the socket is still open.
                if was_timeout:
                    if pacing_send_time is not None:
                        print("LED: pace period ended")
                        pacing_send_time = None
                        self._send_to_server(sock)
                    else:
                        try:
                            # The server never sends anything, so we can use recv() to test if socket still
                            # works. It returns an empty byte array when socket is closed and throws an
                            # exception if there's no data t to receive, but the socket is open.
                            sock.recv(1)
                            break
                        except BlockingIOError:
                            pass

                # If update_event is set, ObserverThread gave us new data which can be sent to the RPI.
                if self.update_event.is_set():
                    self.update_event.clear()

                    # Check how recent our last send was. If it was too recent, calculate a pacing time - earliest
                    # time, at which we should make the send. Otherwise, send normally.
                    if pacing_send_time is None:
                        current_send_time = time.time()
                        interval = current_send_time - self._last_send_time
                        if interval < minimum_send_interval:
                            print(f"LED: starting pace period with {minimum_send_interval}s timeout.")
                            pacing_send_time = self._last_send_time + minimum_send_interval
                        else:
                            self._send_to_server(sock)

                # If kill_event is set, main thread got interrupted. End execution.
                if self.kill_event.is_set():
                    break

    def _send_to_server(self, sock):
        self._last_send_time = time.time()

        message = self.led_state.to_message()
        print(f'LED: sending "{message}" to RPI')
        binary_message = (message + "\n").encode("ascii")
        sock.sendall(binary_message)


class ObserverThread(Thread):
    def __init__(self, initial_led_state, led_thread):
        super().__init__(self._main)
        self._shadow_led_state = initial_led_state
        self._led_thread = led_thread

    def _main(self):
        while not self.kill_event.is_set():
            with open(fifo_file_path, "r", opener=ObserverThread._non_blocking_file_opener) as file:
                self._handle_opened_fifo_file(file)
        print("OBSERVER: Finishing...")

    @staticmethod
    def _non_blocking_file_opener(path, flags):
        # We need to open the file with NONBLOCK flag, because open() on FIFO file
        # blocks until there's a writer available. That means we wouldn't be able
        # to timeout or interrupt it. Nonblocking mode will give us a file descriptor
        # immediately, which we can use in select().
        return os.open(path, flags | os.O_NONBLOCK)

    def _handle_opened_fifo_file(self, file):
        while True:
            stop_fd = self._connection_stop_signal[0]
            file_fd = file.fileno()
            readable, _, _ = select.select([stop_fd, file_fd], [], [])

            # If stop fd is ready, we have been killed by the main thread.
            if stop_fd in readable and self.kill_event.is_set():
                break

            # If file fd is ready, we have new data to read from the file.
            if file_fd in readable:
                # Read exactly one line the file. Empty line means file has
                # been closed.
                line = file.readline()
                if not line:
                    break

                # Strip the line of whitespace. If it became empty, it means
                # we had an empty line. Ignore it for robustness.
                line = line.strip()
                if not line:
                    continue

                # Try to apply the command passed via the file. If it's applied
                # correctly, notify the LED thread, so it makes neccessary changes.
                if self._shadow_led_state.apply_change(line):
                    self._send_state_to_led_thread()
                    self._shadow_led_state.write_to_cache()
                else:
                    print(f'WARNING: invalid command passed to fifo "{line}"')

    def _send_state_to_led_thread(self):
        with self._led_thread.condition:
            print(f"OBSERVER: sending {self._shadow_led_state.to_message()} to LED")
            self._led_thread.led_state = self._shadow_led_state.copy()
            self._led_thread.update_event.set()
            self._led_thread.condition.notify()


# Setup threads
initial_led_state = LedState.read_from_cache()
led_thread = LedThread(initial_led_state.copy())
observer_thread = ObserverThread(initial_led_state.copy(), led_thread)
threads = [observer_thread, led_thread]

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

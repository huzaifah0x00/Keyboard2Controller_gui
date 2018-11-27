import tkinter
import vjoy
import pickle
import socket

from threading import Thread


class MainApplication:
    def __init__(self, master):
        self.frame = tkinter.Frame(master, height=50, width=50,)
        self.frame.pack( fill="both")

        self.server_thread = Thread(target=self.StartServer)
        print("up " + str(self.server_thread))
        self.start_server_btn = tkinter.Button(self.frame, text="Start Server", command=self.server_thread.start,
                                               height=5, width=10)
        self.start_server_btn.pack(side="left")

        self.stop_server_btn = tkinter.Button(self.frame, text="Stop Server", command=self.StopServer, height=5,
                                              width=10)
        self.stop_server_btn.pack(side="right")

    class Client(Thread):
        def __init__(self, conn, joystick_id):
            super().__init__()
            self.vj = vjoy.vJoy(joystick_id)
            self.conn = conn

        def close(self):
            self.conn.close()

        def run(self):
            while True:
                data = self.conn.recv(2048)
                if not data:
                    print('connection lost ? ')
                    break
                else:
                    try:
                        keystates = pickle.loads(data)

                    except (pickle.UnpicklingError, ValueError):
                        keystates = "nokeys"
                    if keystates != "nokeys":
                        # print(f"called handling funcitons at {time.asctime()}")
                        self.vj.handle_buttons(keystates)
                        # print(f"handling funcitons done at {time.asctime()}")

    def StartServer(self):
        self.server_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostname()
        port = 4444
        try:
            self.server_s.bind((host, port))
        except socket.error as e:
            print(str(e))
        print("Server IP: {}\n Port: {}".format(host, port))
        self.server_s.listen(5)
        print('Waiting for a connection.')
        joystick_id = 0
        self.clients = []
        while True:
            joystick_id += 1
            try:
                conn, addr = self.server_s.accept()
            except OSError:
                print("Ending the listener?")
                return 1
            print('connected to: ' + addr[0] + ':' + str(addr[1]))
            print('Waiting for Keystrokes From: ' + str(addr[0]))
            c = self.Client(conn, joystick_id)
            self.clients.append(c)
            c.start()
            # start_new_thread(threaded_client, (conn, joystick_id), )

    def StopServer(self):
        for c in self.clients:
            c.close()
        self.server_s.close()
        print("Closed the Server?")
        try:
            self.server_thread.join()
        except RuntimeError:
            print("Server Not Running")

        self.server_thread = Thread(target=self.StartServer)
        self.start_server_btn.configure(command=self.server_thread.start)
        print("Resetting the server thread")


if __name__ == '__main__':
    root = tkinter.Tk()
    main = MainApplication(root)
    root.mainloop()

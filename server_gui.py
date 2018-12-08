import pickle
import socket
import tkinter.ttk as ttk
from threading import Thread
from tkinter import Tk as Tk

import vjoy


# TODO add server info into GUI


class MainApplication:
	def __init__(self, master):

		frame = ttk.Frame(master, )
		frame.grid(row=0, columnspan=2, )

		lower_frame = ttk.Frame(master, height=10, width=10, )
		lower_frame.grid(row=1, column=0, sticky="news")

		self.server_thread = Thread(target=self.StartServer)

		self.start_server_btn = ttk.Button(frame, text="Start Server", command=self.server_thread.start, )
		# height=5, width=10)
		self.start_server_btn.grid(row=0, column=0, sticky="news")

		self.stop_server_btn = ttk.Button(frame, text="Stop Server", command=self.StopServer, )
		# width=10, height=5)
		self.stop_server_btn.grid(row=0, column=1)

		self.server_status = "not_running"

		self.server_status_TB = ttk.Label(lower_frame, text="server status:" + self.server_status)
		self.server_status_TB.grid(row=2, column=0, )

		self.connd_clients = []

		self.connd_clients = ttk.Label(lower_frame, text="Connected clients:\n\t")
		self.connd_clients.grid(row=3, column=0, )

		self.host = socket.gethostname()
		self.port = 4444
		self.server_info = """
        hostname : {}
        port: {}
        """.format(self.host, self.port)
		self.server_info_l = ttk.Label(lower_frame, text=self.server_info)
		self.server_info_l.grid(row=2, column=1)
		self.clients = []

		self.update_widgets()

	def update_widgets(self):
		self.start_server_btn.configure(command=self.server_thread.start)
		try:
			clienstbox = [str(i.addr[0]) for i in self.clients]
			ids = [str(i.id) for i in self.clients]
			addrs = [str(i.addr[0]) for i in self.clients]
			clientsbox = """Connected clients:
id	address
							
{}	{}
""".format('\n'.join(ids), '\n'.join(addrs))

			self.connd_clients.configure(text=clientsbox)

		except:
			raise
		# self.server_status_TB.delete(1.0, ttk.END)
		# self.server_status_TB.insert(ttk.END, self.server_status)
		self.server_status_TB.configure(text="server status: " + self.server_status)
		self.server_info_l.configure(text=self.server_info)

	class Client(Thread):
		def __init__(self, conn, addr, joystick_id):
			super().__init__()
			self.vj = vjoy.vJoy(joystick_id)
			self.conn = conn
			self.id = joystick_id
			self.addr = addr

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
		self.host = socket.gethostname()
		self.port = 4444
		self.server_info = """
        hostname : {}
        port: {}
        """.format(self.host, self.port)

		self.server_status = "Running."
		self.update_widgets()
		self.server_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		try:
			self.server_s.bind((self.host, self.port))
		except socket.error as e:
			print(str(e))
		print("Server hostname: {}\n Port: {}".format(self.host, self.port))
		try:
			self.server_s.listen(5)
		except:
			pass
		print('Waiting for a connection.')
		joystick_id = 0
		while True:
			joystick_id += 1
			try:
				conn, addr = self.server_s.accept()
			except OSError:
				print("Ending the listener?")
				return 1

			print('connected to: ' + addr[0] + ':' + str(addr[1]))
			print('Waiting for Keystrokes From: ' + str(addr[0]))
			c = self.Client(conn, addr, joystick_id)
			self.clients.append(c)
			self.update_widgets()
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

		self.server_status = "Not Running."
		self.server_thread = Thread(target=self.StartServer)
		self.update_widgets()

		print("Resetting the server server")


if __name__ == '__main__':
	root = Tk()
	main = MainApplication(root)
	root.mainloop()

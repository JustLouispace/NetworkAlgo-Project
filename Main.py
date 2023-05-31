import threading
import socket
import time
import os

CITY_ID = int(os.environ["CITY_ID"])
PORT = int(os.environ["PORT"])
NUM_CITIES = 4
PORTS = [5001, 5002, 5003, 5004]

class Node(threading.Thread):
    def __init__(self, city, port, distances):
        threading.Thread.__init__(self)
        self.city = city
        self.port = port
        self.distances = distances
        self.neighbors = ["node " + str(i+1) for i in range(NUM_CITIES) if i+1 != city]
        self.isSent = False
        self.receivedMessages = []
        self.path = []

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', self.port))
            if not self.isSent:
                for neighbor in self.neighbors:
                    self.sendMessage(neighbor, str(self.city))
                self.isSent = True

            while True:
                conn, addr = s.accept()
                data = conn.recv(1024)
                if data:
                    self.receivedMessages.append(data.decode())
                    if len(self.receivedMessages) == NUM_CITIES - 1:
                        print(f"[Received] Node {self.city} received: {self.receivedMessages}")
                        break

    def sendMessage(self, neighbor, message):
        neighborInfo = neighbor.split(" ")
        neighborPort = PORTS[int(neighborInfo[1]) - 1]
        for i in range(5):  # Retry 5 times
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((neighborInfo[0] + neighborInfo[1], neighborPort))
                    s.sendall(message.encode())
                    time.sleep(2)
                break
            except ConnectionRefusedError:
                print(f"Connection failed. Retrying in {2 ** i} seconds.")
                time.sleep(2 ** i)  # Exponential backoff


    def calculateDistances(self):
        totalDistance = 0
        self.path.append(self.city)
        currentCity = self.city
        unvisitedCities = [i+1 for i in range(NUM_CITIES) if i+1 != self.city]

        while unvisitedCities:
            nextCity = unvisitedCities.pop(0)
            distanceToNextCity = self.distances[nextCity-1]
            totalDistance += distanceToNextCity
            self.path.append(nextCity)
            print(f"[Step] Distance from city {currentCity} to city {nextCity}: {distanceToNextCity}")
            print(f"[Step] Cumulative total distance for node {self.city}: {totalDistance}")
            currentCity = nextCity

        # Add the distance to return to the original city
        distanceToOrigin = self.distances[self.city-1]
        totalDistance += distanceToOrigin
        self.path.append(self.city)
        print(f"[Step] Distance from city {currentCity} to city {self.city}: {distanceToOrigin}")
        print(f"[Step] Cumulative total distance for node {self.city}: {totalDistance}")

distances = [[0, 10, 15, 20], [10, 0, 35, 25], [15, 35, 0, 30], [20, 25, 30, 0]]
node = Node(CITY_ID, PORT, distances[CITY_ID-1])
node.start()
node.join()
node.calculateDistances()
print("Path:", node.path)

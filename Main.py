import socket
import threading
import time
from typing import List

NUM_CITIES = 4
PORTS = [5001, 5002, 5003, 5004]

class Node(threading.Thread):
    def __init__(self, city, port, lock, distances):
        threading.Thread.__init__(self)
        self.city = city
        self.port = port
        self.lock = lock
        self.neighbors = []
        self.receivedMessages = []
        self.isSent = False
        self.distances = distances
        self.path = []

        for i in range(NUM_CITIES):
            if i + 1 != city:
                self.neighbors.append("node " + str(i + 1))

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
            serverSocket.bind(('localhost', self.port))
            serverSocket.listen()
            print(f"\n[Info] Node {self.city} is running on port {self.port}\n")

            with self.lock:
                if not self.isSent:
                    for i in range(1, NUM_CITIES + 1):
                        if i != self.city:
                            self.sendMessage("node " + str(i), str(self.city))
                    self.isSent = True

            while True:
                clientSocket, addr = serverSocket.accept()
                message = clientSocket.recv(1024).decode('utf-8')
                self.receivedMessages.append(message)

                if len(self.receivedMessages) == NUM_CITIES - 1:
                    print(f"[Received] Node {self.city} received: {self.receivedMessages}")
                    break

    def sendMessage(self, neighbor, message):
        neighborInfo = neighbor.split(" ")
        neighborHost = "localhost"
        neighborPort = PORTS[int(neighborInfo[1]) - 1]

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketClient:
            socketClient.connect((neighborHost, neighborPort))
            socketClient.sendall(message.encode('utf-8'))

        time.sleep(2)

    def calculateDistances(self, distances):
        totalDistance = 0
        self.path.append(self.city)
        currentCity = self.city
        unvisitedCities = []

        for i in range(NUM_CITIES):
            if i + 1 != self.city:
                unvisitedCities.append(i + 1)

        while unvisitedCities:
            nextCity = unvisitedCities.pop(0) # Take the first city from the list of unvisited cities
            distanceToNextCity = distances[currentCity-1][nextCity-1]
            totalDistance += distanceToNextCity
            print(f"[Step] Distance from city {currentCity} to city {nextCity}: {distanceToNextCity}")
            print(f"[Step] Cumulative total distance for node {self.city}: {totalDistance}")
            currentCity = nextCity
            self.path.append(currentCity)

        distanceToStartCity = distances[currentCity-1][self.city-1] # Distance back to the starting city
        totalDistance += distanceToStartCity
        print(f"[Step] Distance from city {currentCity} back to city {self.city}: {distanceToStartCity}")
        print(f"[Step] Cumulative total distance for node {self.city}: {totalDistance}")
        self.path.append(self.city) # Add the starting city back to the path

        print(f"[Neighbors] Node {self.city} has neighbors: {self.neighbors}")
        print(f"[Path] Path for node {self.city}: {self.path}")
        print(f"[Total Distance] Total distance for node {self.city}: {totalDistance}\n")

def main():
    nodes = []
    lock = threading.Lock()

    distances = [
        [0, 10, 15, 20],
        [10, 0, 35, 25],
        [15, 35, 0, 30],
        [20, 25, 30, 0]
    ]

    for i in range(NUM_CITIES):
        port = PORTS[i]
        node = Node(i + 1, port, lock, distances[i])
        nodes.append(node)
        node.start()

    for node in nodes:
        node.join()

    for node in nodes:
        node.calculateDistances(distances)

if __name__ == "__main__":
    main()

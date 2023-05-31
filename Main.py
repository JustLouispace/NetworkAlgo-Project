import threading
import socket
import time

NUM_CITIES = 4
PORTS = [5001, 5002, 5003, 5004]

class Node(threading.Thread):
    def __init__(self, city, port, lock, distances):
        threading.Thread.__init__(self)
        self.city = city
        self.port = port
        self.lock = lock
        self.distances = distances
        self.neighbors = ["node " + str(i+1) for i in range(NUM_CITIES) if i+1 != city]
        self.isSent = False
        self.receivedMessages = []
        self.path = []

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', self.port))
            self.lock.acquire()
            try:
                if not self.isSent:
                    for i in range(1, NUM_CITIES+1):
                        if i != self.city:
                            self.sendMessage("node " + str(i), str(self.city))
                    self.isSent = True
            finally:
                self.lock.release()

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
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', neighborPort))
            s.sendall(message.encode())
            time.sleep(2)

    def calculateDistances(self, distances):
        totalDistance = 0
        self.path.append(self.city)
        currentCity = self.city
        unvisitedCities = [i+1 for i in range(NUM_CITIES) if i+1 != self.city]

        while unvisitedCities:
            nextCity = unvisitedCities.pop(0)
            distanceToNextCity = distances[currentCity-1][nextCity-1]
            totalDistance += distanceToNextCity
            print(f"[Step] Distance from city {currentCity} to city {nextCity}: {distanceToNextCity}")
            print(f"[Step] Cumulative total distance for node {self.city}: {totalDistance}")
            currentCity = nextCity

def main():
    distances = [[0, 10, 15, 20], [10, 0, 35, 25], [15, 35, 0, 30], [20, 25, 30, 0]]
    lock = threading.Lock()
    nodes = [Node(i+1, PORTS[i], lock, distances[i]) for i in range(NUM_CITIES)]
    for node in nodes:
        node.start()
    for node in nodes:
        node.join()
    for node in nodes:
        node.calculateDistances(distances)

if __name__ == "__main__":
    main()

import java.net.*;
import java.io.*;
import java.util.concurrent.TimeUnit;

public class Node implements Runnable {
    private int nodeNumber;
    private ServerSocket serverSocket;
    private String message;

    public Node(int nodeNumber, int port) throws IOException {
        this.nodeNumber = nodeNumber;
        this.serverSocket = new ServerSocket(port);
        this.message = Integer.toString(nodeNumber);
    }

    @Override
    public void run() {
        System.out.println("Node " + nodeNumber + " is running on port " + serverSocket.getLocalPort());

        while (true) {
            try {
                Socket socket = serverSocket.accept();
                BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                String receivedMessage = in.readLine();

                System.out.println("Node " + nodeNumber + " received: " + receivedMessage);

                message += " " + receivedMessage;

                for (int i = 1; i <= 4; i++) {
                    if (i != nodeNumber) {
                        Socket sendSocket = new Socket("localhost", 5000 + i);
                        PrintWriter out = new PrintWriter(sendSocket.getOutputStream(), true);
                        out.println(message);
                        sendSocket.close();
                    }
                }

                TimeUnit.SECONDS.sleep(2); // Sleep for 2 seconds between rounds
            } catch (IOException | InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    public static void main(String[] args) throws IOException {
        for (int i = 1; i <= 4; i++) {
            Node node = new Node(i, 5000 + i);
            new Thread(node).start();
        }
    }
}

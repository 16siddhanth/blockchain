import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

class Block {
    public String hash;
    public String previousHash;
    private String data;
    private long timeStamp;

    public Block(String data, String previousHash) {
        this.data = data;
        this.previousHash = previousHash;
        this.timeStamp = System.currentTimeMillis();
        this.hash = calculateHash();
    }

    public String calculateHash() {
        String input = previousHash + Long.toString(timeStamp) + data;
        return applySha256(input);
    }

    public static String applySha256(String input) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(input.getBytes("UTF-8"));
            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) hexString.append('0');
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    public String getData() {
        return data;
    }

    public long getTimeStamp() {
        return timeStamp;
    }
}

class Blockchain {
    private List<Block> chain;

    public Blockchain() {
        chain = new ArrayList<>();
        chain.add(createGenesisBlock());
    }

    private Block createGenesisBlock() {
        return new Block("Genesis Block", "0");
    }

    public void addBlock(String data) {
        Block newBlock = new Block(data, chain.get(chain.size() - 1).hash);
        chain.add(newBlock);
    }

    public void printChain() {
        for (Block block : chain) {
            System.out.println("Block Hash: " + block.hash);
            System.out.println("Previous Hash: " + block.previousHash);
            System.out.println("Data: " + block.getData());
            System.out.println("Timestamp: " + block.getTimeStamp());
            System.out.println();
        }
    }
}

public class q1 {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        Blockchain myBlockchain = new Blockchain();

        System.out.print("Enter the number of blocks to add to the blockchain: ");
        int numBlocks = scanner.nextInt();
        scanner.nextLine();

        for (int i = 0; i < numBlocks; i++) {
            System.out.print("Enter data for Block " + (i + 1) + ": ");
            String data = scanner.nextLine();
            myBlockchain.addBlock(data);
        }

        myBlockchain.printChain();

        scanner.close();
    }
}

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;


public class BlockMining {
    
    public static void main(String[] args) {
        // Create a new blockchain
        Blockchain blockchain = new Blockchain(6); 
        
        System.out.println("Mining block 1...");
        blockchain.addBlock(new Block(1, "Block 1 Balle Balle", blockchain.getLatestBlock().getHash()));
        
        System.out.println("Mining block 2...");
        blockchain.addBlock(new Block(2, "Block 2 YoYo ", blockchain.getLatestBlock().getHash()));
        
        System.out.println("Mining block 3...");
        blockchain.addBlock(new Block(3, "Block 3 the goattttt", blockchain.getLatestBlock().getHash()));
        
        System.out.println("\nBlockchain validation: " + blockchain.isChainValid());
        
        // Print the entire blockchain
        System.out.println("\nThe blockchain:");
        System.out.println(blockchain);
    }
}

class Block {
    private int index;
    private long timestamp;
    private String data;
    private String previousHash;
    private String hash;
    private int nonce;
    
    
    public Block(int index, String data, String previousHash) {
        this.index = index;
        this.timestamp = new Date().getTime();
        this.data = data;
        this.previousHash = previousHash;
        this.nonce = 0;
        this.hash = calculateHash();
    }
    
    
    public String calculateHash() {
        String dataToHash = index + timestamp + previousHash + data + nonce;
        return applySha256(dataToHash);
    }
    
    
    private String applySha256(String input) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(input.getBytes(StandardCharsets.UTF_8));
            StringBuilder hexString = new StringBuilder();
            
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) hexString.append('0');
                hexString.append(hex);
            }
            
            return hexString.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
    }
    
    
    public void mineBlock(int difficulty) {
        // Create a target string with 'difficulty' number of leading zeros
        String target = new String(new char[difficulty]).replace('\0', '0');
        
        while (!hash.substring(0, difficulty).equals(target)) {
            nonce++;
            hash = calculateHash();
        }
        
        System.out.println("Block mined! Hash: " + hash);
    }
    
    // Getters
    public String getHash() {
        return hash;
    }
    
    public String getPreviousHash() {
        return previousHash;
    }
    
    @Override
    public String toString() {
        return "Block {" +
                "\n   index: " + index +
                "\n   timestamp: " + timestamp +
                "\n   data: '" + data + '\'' +
                "\n   previousHash: '" + previousHash + '\'' +
                "\n   hash: '" + hash + '\'' +
                "\n   nonce: " + nonce +
                "\n}";
    }
}


class Blockchain {
    private List<Block> chain;
    private int difficulty;
    
    
    public Blockchain(int difficulty) {
        this.chain = new ArrayList<>();
        this.difficulty = difficulty;
        
        // Create the genesis block (first block in the chain)
        Block genesisBlock = new Block(0, "Genesis Block", "0");
        genesisBlock.mineBlock(difficulty);
        chain.add(genesisBlock);
        
        System.out.println("Genesis block created!");
    }
    
    
    public void addBlock(Block newBlock) {
        newBlock.mineBlock(difficulty);
        chain.add(newBlock);
    }
    
    
    public Block getLatestBlock() {
        return chain.get(chain.size() - 1);
    }
    
    
    public boolean isChainValid() {
        for (int i = 1; i < chain.size(); i++) {
            Block currentBlock = chain.get(i);
            Block previousBlock = chain.get(i - 1);
            
            // Verify the current block's hash
            if (!currentBlock.getHash().equals(currentBlock.calculateHash())) {
                System.out.println("Current hash is not valid");
                return false;
            }
            
            // Verify the reference to the previous block's hash
            if (!currentBlock.getPreviousHash().equals(previousBlock.getHash())) {
                System.out.println("Previous hash reference is not valid");
                return false;
            }
        }
        
        return true;
    }
    
    @Override
    public String toString() {
        StringBuilder builder = new StringBuilder();
        for (int i = 0; i < chain.size(); i++) {
            builder.append("Block #").append(i).append(":\n");
            builder.append(chain.get(i).toString()).append("\n\n");
        }
        return builder.toString();
    }
}

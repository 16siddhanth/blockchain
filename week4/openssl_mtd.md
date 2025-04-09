
# 🔐 OpenSSL AES Encryption & Decryption Over a Text File

## 📄 Step 1: Create a Text File

Create a sample transaction data file named `tx.txt`.

```bash
echo "Eve pays David 20 BTC" > tx.txt
```

---

## 🔒 Step 2: Encrypt the File using AES-256-CBC

Use OpenSSL to encrypt `tx.txt` with AES in CBC mode.

```bash
openssl enc -aes-256-cbc -salt -in tx.txt -out tx.enc -pass pass:mysecurekey
```

- `-aes-256-cbc`: Specifies AES with 256-bit key in CBC mode
- `-salt`: Adds a random salt for better security
- `-in`: Input file (`tx.txt`)
- `-out`: Encrypted file (`tx.enc`)
- `-pass`: Password used for key generation

---

## 🔓 Step 3: Decrypt the File

Use OpenSSL to decrypt the encrypted file back to plain text.

```bash
openssl enc -d -aes-256-cbc -in tx.enc -out tx.dec.txt -pass pass:mysecurekey
```

- `-d`: Decryption mode
- `-in`: Encrypted file (`tx.enc`)
- `-out`: Decrypted output file (`tx.dec.txt`)

---

## 📄 Step 4: View the Decrypted Output

```bash
cat tx.dec.txt
```

You should see:

```
Eve pays David 20 BTC
```

---

## 🔁 Optional: Try Other Modes

- AES-128-CBC: `-aes-128-cbc`
- AES-192-CBC: `-aes-192-cbc`
- AES-256-CTR (stream-like mode): `-aes-256-ctr`

---

## 📚 Reference

OpenSSL AES is ideal for testing command-line encryption of sensitive data. Use strong passwords and secure key storage in production systems.

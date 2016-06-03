This server demonstrates a pretty famous attack against AES-CBC mode. 

You will get a ciphertext from the server, to get the secret, you will have to decrypt (most of) the
ciphertext.

You can send up ciphertexts to the server, it will decrypt them and inform you whether or not the 
corresponding plaintext has valid padding or not. This is one of those subtle implementation details
that completely undermine the cryptosystem. 

============================================
I HIGHLY RECCOMEND YOU TEST LOCALLY. Constantly pinging the server will be slow, and you 
won't be sure your code is working unless you happen to perfectly implement the attack.
============================================

Submit your code and the secret to receive full credit.

Email me if anything is broken or if you're having issues. 

Good luck, have fun :).

-Patrick

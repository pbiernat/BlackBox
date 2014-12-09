This is a backdoored version of Dual_EC_DRBG. 

Upon connecting, you will receive the Q point, as well as the backdoor that this particular generator
was created with. You will also get the first random number it outputs.

Given this information, you can predict the next number it will generate. Do that, and get the secret.

Note that a new backdoored RNG is created upon every connection, so make sure your code dynamically 
calculates the secret "key" used to break the RNG.

There were a few high profile blog posts about this when the first PoC came out, they will be very 
helpful in this challenge :)

Email biernp@rpi.edu with questions and comments. 

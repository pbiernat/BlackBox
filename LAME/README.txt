A keyed MAC is one that takes the form of hash(secret + message). 

In theory, this will let you know if anyone changes "message", since they don't know "secret" they 
cannot create a valid hash for their new message. This is true in general, but there is a class of 
attacks known as Length Extension which can be used to create a valid hash for "message + Appended Data". 

Performing one of these will help you get the flag for this challenge.

Email biernp@rpi.edu with comments/questions.

Have fun!

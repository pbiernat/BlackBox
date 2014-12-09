This challenge showcases another potential issue with using PRNGs. 

Oftentimes, it is possible to leak information about their internal state. The Mersenne Twister is 
particularly susceiptble to this: It leaks 32 bits of its Internal State every time it gives you a 
number! 

This is due to the fact that its "tempering" function is invertible. It should be possible to 
create a fake generator that matches the server-side one. 

I reccomend you do this one locally, it will be a lot easier to debug your "untempering" functions. 
If you have it working locally, but something isn't matching up server-side, please let me know!

Have fun :)
-Patrick

biernp@rpi.edu 

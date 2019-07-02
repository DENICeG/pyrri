# pyrri
Commandline client and module to send/receive RRI commands, written in Python 3

# requirements
You must have a recent version of Python 3 installed. The client is tested with Python 3.6,
but it may run with older versions, too. It is not compatible with Python 2.x!

No third party modules are needed.

# Use it as a client

You need to copy "rri.py" somewhere in your PATH and make it executable. Then call it with "-h"
to show help:

    rri.py -h
    
All parameters are optional:
* -s SERVER defaults to "rri.denic.de:51131"
* Username and Password can be given as Parameters with -u and -p, but also
  and more secure as environment variables RRI\_USERNAME and RRI\_PASSWORD
* order can be piped in from stdin or as file with parameter -i
* answer is written to stdout or to a file which can be set with parameter -o

Example 1:

    export RRI_USERNAME="DENIC-1000006-USER"
    export RRI_PASSWORD="this is a secret"
    cat example_kv.txt | ./rri.py
    
Example 2:

    ./rri.py -s rri.test.denic.de:51131 -u DENIC-1000006-USER -p password -i example_kv.txt -o answer.txt


# Use it as a module

Copy rri.py to your project, import the RRIClient class, instantiate it, connect to the rri server and login

    from rri import RRIClient
    ...
    
    rri = RRIClient()
    # connect to rri server
    rri.connect(hostname, port)
    # login with your credentials
    rri.login(username, password)
    
Now you can send a command to the rri server:

    answer = rri.talk(order)

You can repeatedly call the "talk"-method with further orders.

When you are done, logout and disconnect     
    
    rri.logout()
    rri.disconnect()
    
When an error occures the methods raise exceptions, which you should handle properly!
 
    
# TODO
* Implement check and validation of certificate with trustchain in module and cli
* add automated tests


# License

Copyright (c) 2019 DENIC eG

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.



Retcon
======

Retcon is a tool for managing your Icinga alerts.

It can speak to multiple Icinga installs, and allows you to acknowledge alerts
(by scheduling down time). It gives an audible notification of change, and
can track you down via XMPP, Prowl and SMS to let you know.


The Quick Start
---------------

	# Install the dependencies
	$ pip install -r requirements.txt

	# Optionally install pymemc, if you have memcached
	$ pip install pymemc

	# Customise the config file

	# Run the web server! (Or run under WSGI-compatible wrapper)
	$ RETCON_CONFIG=/etc/retcon.cfg python runserver.py

License
-------

Copyright (c) 2010-2013, Aaron Brady  
Copyright (c) 2010-2013, Darren Worrall  
Copyright (c) 2010-2013, Interactive Web Solutions Ltd  


Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

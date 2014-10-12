Yik Yak Command Line Version
==============

Python implementation of Yik Yak using the pyak API by joseph346. It reads and posts yaks. More features to come in the future.

--------------------------------------------------------------------------------------
## Getting Started Guide for Users on OS X and Linux (you can skip this if you are experienced with Python and the Terminal):

- Click Download ZIP
- Install Python 3 (latest version is 3.4.0): http://www.python.org/downloads/
- Install Requests (using pip): http://docs.python-requests.org/en/latest/user/install/#install
- Open Terminal
- Type this command: ```cd ./Downloads/YikYakTerminal-master```
- Hit enter and then type ```python3 YikYak.py```

You should get text that looks like this:

    Yik Yak Command Line Edition : Created by djtech42
    
    
    Note: This app is currently only for viewing and posting yaks at any location. There is no ability to vote or delete yet.


--------------------------------------------------------------------------------------

## Instructions

It allows you to enter the name of a college or university.

```Enter college name or address: Capital University ```

The app will save this location as default, so you don't have to enter it each time. 

```Location is set to:  Capital University ```

You can change this location at any time and see yaks from different colleges.

```Read(R), Post(P), Choose New Location(L), or Quit(Q) -> L```

You can specify a handle for a post and choose whether to show location:

    Enter message to yak: 
    Good morning!
    Add handle: (Blank to omit): 
    Friendly Yakker
    Show location? (Y/N)Y


Viewing a Yak:

    _____________________________________________________________________________________________
    
    Can they turn the heat on in our dorms...its too cold in here
    
    	3 likes  |  Posted  2014-10-12 00:50:19  at  39.9435063 -82.9450901
    
    		Comments:2
    		-----------------------------------------------------------------------------
    		(2) Supposedly that's happening Wednesday 
    
    		Posted  2014-10-12 01:11:52
    		-----------------------------------------------------------------------------
    		(1) thank god  
    
    		Posted  2014-10-12 01:15:36
    		
## API and Licensing

This app is licensed under the GPL license.

This software utilizes PyGeoCoder to convert addresses to coordinates (licensed under BSD): http://code.xster.net/pygeocoder/wiki/Home

API url was http://github.com/joseph346/pyak/, but the repo seems to be deleted now.

Radiati0n has a version of it at http://github.com/Radiati0n/pyak. 

I modified the original to create specific output for this app.

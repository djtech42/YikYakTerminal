Yik Yak Command Line Version (Version 2.1)
==============

Python implementation of Yik Yak using the pyak API by joseph346. More features to come in the future.

--------------------------------------------------------------------------------------
## Getting Started Guide for Users on OS X (Mac) and Linux

- Click Download ZIP
- Install Python 3 (latest version is 3.4.2): http://www.python.org/downloads/
- Open Terminal
- Install Requests ```python3.4 -m pip install requests```

Commands below are used for running the app:
- Type this command: ```cd ./Downloads/YikYakTerminal-master```
- Hit enter and then type ```python3 YikYak.py```

You should get text that looks like this:

    Yik Yak Command Line Edition : Created by djtech42


    Enter college name or address: 

If you are having trouble getting it to run, let me know in Issues.

--------------------------------------------------------------------------------------

## Location Setup

It allows you to enter the name of a college or university.

```Enter college name or address: Capital University ```

The app will save this location as default, so you don't have to enter it each time. 

```Location is set to:  Capital University ```

You can change this location at any time and see yaks from different colleges.

```*Choose New Location		(L) or (L <location>)```

## Actions

Actions are performed using a single letter and optional parameter(s).

    *Read Latest Yaks		    (R)
    *Read Top Local Yaks		(T)
    
    *Read Best Yaks of All Time	(B)
    
    *Show User Yaks			    (S)
    *Show User Comments		    (O)
    
    *Post Yak			        (P) or (P <message>)
    *Post Comment			    (C) or (C <yak#>)
    
    *Upvote Yak			        (U) or (U <yak#>)
    *Downvote Yak			    (D) or (D <yak#>)
    *Report Yak					(E) or (E <yak#>)
    
    *Upvote Comment			    (V) or (V <yak# comment#>)
    *Downvote Comment		    (H) or (H <yak# comment#>)
    *Report Comment				(M) or (M <yak# comment#>)
    
    *Yakarma Level			    (Y)
    
    *Choose New User ID		    (I) or (I <userID>)
    *Choose New Location		(L) or (L <location>)
    
    *Contact Yik Yak			(F)
    
    *Quit App			    	(Q)
    
    ->
    
Input looks like this:
```-> P I love this college!```

## Getting Yaks to Show Up

```R``` retrieves the latest yaks from your location.

```T``` retrieves the highest upvoted yaks from your location.

```B``` retrieves the highest upvoted yaks from anywhere.

```S``` retrieves your own yaks.

```O``` retrieves your own replies to yaks.

## Posting

To start a post, enter ```P```

You can specify a handle for a post and choose whether to show location:

    Enter message to yak: 
    Good morning!
    Add handle: (Blank to omit): 
    Friendly Yakker
    Show location? (Y/N) Y
    
Using the parameter allows for quicker posting:

```-> P Good Morning!```

## Commenting

You specify the number of the yak, which is in the top-left corner:

    _____________________________________________________________________________________________
    31

    Losing your wallet is like losing a part of your soul.
    
Comment: ```-> C 31```

```Enter comment:```
    
Same for upvoting a yak: ```-> U 31```

Downvoting a yak: ```-> D 31```

Upvoting a comment requires the yak number as well as the comment number to the left of the dashed line.

		Comments:1
      1 -----------------------------------------------------------------------------
	    (1) Best yak I've read today. You win.  

	    Posted  2014-10-19 20:50:59
	    
Upvoting a comment: ```-> V 31 1```

Downvoting a comment: ```-> H 31 1```

## Yak Interface:

    _____________________________________________________________________________________________
    83
    
    Can they turn the heat on in our dorms...its too cold in here
    
    	3 likes  |  Posted  2014-10-12 00:50:19  at  39.9435063 -82.9450901
    
    		Comments:2
    	 1	-----------------------------------------------------------------------------
    		(2) Supposedly that's happening Wednesday 
    
    		Posted  2014-10-12 01:11:52
    	 2	-----------------------------------------------------------------------------
    		(1) thank god  
    
    		Posted  2014-10-12 01:15:36
    		
- Yak Number
- Yak
- Number of likes | Post date and time, location
- Number of comments
- Comment Number
- (Vote Number) Comment
- Comment post date and time

## Experimental Versions

Commits containing new, unreleased features will be available on the beta branch. There is no guarantee that these features will work.
    		
## API and Licensing

This app is licensed under the GPL license. Feel free to contribute to it.

This software utilizes PyGeoCoder to convert addresses to coordinates (licensed under BSD): http://code.xster.net/pygeocoder/wiki/Home

API url was http://github.com/joseph346/pyak/, but the repo seems to be deleted now.

I modified the original to create specific output for this app.

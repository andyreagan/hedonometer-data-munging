Here is a ton of info from my notes on what the heck I did before:
==================================================================

That's all, next steps:
-code the backend for the data for the movies
-> two scripts, one to produce the timeseries, the other the word vectors
-> both tunable for sliding window! and then make the front end tunable for the sliding window.
-> use the database to pull the filenames
-> make a final call on that API tomorrow after 9PM

Here are some commands that I used to move the raw data files around...so that I know what I did.
Had to move about 6 of them.
Also turns out that some are blank, and some are too short at 10K word resolution of the sliding window.

\begin{verbatim}
  mv raw/48-Hrs{-,}.txt 

  root@bicentennial:/usr/share/nginx/data/moviedata# ls raw/Austin
  ls: cannot access raw/Austin: No such file or directory
  root@bicentennial:/usr/share/nginx/data/moviedata# ls raw/Austin*
  raw/Austin-Powers---International-Man-of-Mystery.txt  raw/Austin-Powers---The-Spy-Who-Shagged-Me.txt
  root@bicentennial:/usr/share/nginx/data/moviedata# mv raw/Austin-Powers-{--,}The-Spy-Who-Shagged-Me.txt 
  root@bicentennial:/usr/share/nginx/data/moviedata# mv raw/Austin-Powers-{--,}International-Man-of-Mystery.txt 
  root@bicentennial:/usr/share/nginx/data/moviedata# ls raw/E-*
  raw/E-T-.txt
  root@bicentennial:/usr/share/nginx/data/moviedata# mv raw/E-T{-,}.txt
  root@bicentennial:/usr/share/nginx/data/moviedata# ls raw/Escape-From-*
  raw/Escape-From-L-A-.txt  raw/Escape-From-New-York.txt
  root@bicentennial:/usr/share/nginx/data/moviedata# mv raw/Escape-From-L-A{-,}.txt 
  root@bicentennial:/usr/share/nginx/data/moviedata# ls raw/Maj
  Majestic,-The-(The-Bijou).txt  Major-League.txt               
  root@bicentennial:/usr/share/nginx/data/moviedata# ls raw/Majestic*
  raw/Majestic,-The-(The-Bijou).txt
  root@bicentennial:/usr/share/nginx/data/moviedata# mv raw/Majestic\,-The-\(The-Bijou\).txt raw/Majestic-\(The-Bijou\)\,-The.txt
\end{verbatim}

Need to decrease the resolution of the scripts, and update the JS to handle that for making shifts.
Maybe make all of the files for 500,1000,2000,5000,10000.
Make it part of the URL? Not super flexible for changing.
But making it change without a reload is a huge pain, and probably not necessary for now.
Let's settle for a URL parameter, and then picking a default is easy.
Use folders for the different files.

Annotations don't work on the movies online yet- no shock.
Patch that up and get the panometer up!

root@bicentennial:/usr/share/nginx/data/moviedata# mkdir word-vectors/{500,1000,2000,5000,10000}
root@bicentennial:/usr/share/nginx/data/moviedata# mkdir timeseries/{500,1000,2000,5000,10000}

Okay just pushed up the correct models and everything.
The next few additions:
-add window to the views for a POST
-add window to filter in drawMovieTimeseries

Next things:
-get lens to work
-add slider for different resolutions
(react.js?)


10:29PM

Making the final API call!?
I accidentally stopped the script that was making all of the backend data at ``The Matrix Reloaded'', oops.

Just submitted for the API to call movies 701 to 2000...so that should get them all.
Looks like the movies that it's adding to the database would require me to reprocess all of the backend data anyway, which is fine (since they're in the middle of the alphabet).
I'll just send it to nohup, should happen overnight.

When building the search API for movies (or the webpage to hit it)...need to make sure that the movies exist at resolution 2000.
Really only the blank ones will not exist at the resolution.

To get the resolution into the annotation form, I think I'll need to create a hidden field on the form.
Can do this when the form is build in the first place, I think.

Turns out that I hit the hard drive limit with the movies, it stopped at ``They'', so I'll restart the thing now.
Cleared some space by deleting all of the \verb|parsed.*| files in word vectors for both arabic and english. They're all on the VACC anyway.

Added a model field called ``score'' to the movies, at some point, go back and get all of the scores from the IMDB database...since it's unlimited now.

\begin{verbatim}
  for FILE in $(\ls -1 rawer/*.html); do grep -A 1000000 "<body>" $FILE | sed -n '2,1000000p' > $FILE.end; done
  for FILE in $(\ls -1 rawer/*.html.end); do grep -B 1000000 "</body>" $FILE > $FILE.beg; done
  for FILE in $(\ls -1 rawer/*.html.end.beg); do sed -i '$ d' $FILE > $FILE.beg; done
\end{verbatim}

\begin{verbatim}
  for FILE in $(\ls -1 rawer/*.html.end.beg); do cat $FILE | sed -e "s/<b>//" | sed -e "s/<\/b>//" > $FILE.clean; done
\end{verbatim}

Now going to try parsing that raw text, line by line.
Do it in javascript.

Looks like when Lewis cleaned the scripts, he removed everything inside the bold tags.
The cleaned version of 127 Hours has 15887 words, and the uncleaned version has 18361.
I'm thinking to remove everything inside of the bold tags, for a super cleaned version.
But keep the line breaks.

Okay so my parse is now slightly longer than lewis' because I'm keeping words like ``A'' which he lost.
I'm just ignoring lines that begin with a bold tag...which may not work as well across all movies. I'm guessing that lewis removed all capital words...which I think that I could do with sed as well...but I think that I should keep them.
Unless there are movies where it doesn't work.
Let's try a different movie!

In "a few good men", my parse actually does a little bit better...by keep capital words in the description, that we want.
I think I'll just need to reparse the thing in python, and also save a file where I'm keeping track of the line numbers in which every 200 break is made.
Since I'm only using the 2000, this will be okay (wouldn't be any harder to do it for everything).
Then I can load that file, and save the computation in the browser. Although it seems like I could just parse the whole thing, it's so fast. Don't do it.
I'll make a CSV with the line numbers, and then I'll load those to generate the javascript function that controls the scrolling of the complete text on the LHS.

Got the whole thing working!!
Bad news though: my clean up job of the scripts didn't go as hot as I thought it did.
Check file sizes with
ll rawer/*.html.end.beg
and realize that about half of them are blank. Which means that the script isn't just directly between the two html tags.

this is just one line:
rawer/Training-Day.html

this one has tons of nasty formatting
rawer/12.html

going to try again but instead of capturing the first body tag, going to capture the first \verb|class="scrtext"|.

2014-12-20

After I've run the clean script, run the checkclean script to move the ones that didn't work right away into the rawer/trouble folder.
As of now, 1000 worked with the clean.sh script, and 93 didn't work.
I could clean 93 of them by hand....

Looking at 12.html.
The beginning should have matched...but I don't think that the end did.
Yes.

Copying clean over to clean2, and going to try some different things.
The movie 12 on the website seems to have a bunch of issues, it points to a different looking thing.
The movie 187 seems to have been saved wrong to html.
Grabbed it again with curl.
The \verb|class=scrtext| was lacking quotes, so I added them.
Fixed a bug in the clean.sh script.
Now 187 works.

Removed the </pre> tags from the beginning of 12.html and added one at the end, added some special stuff to fix up the some crazy extra tags at the beginning...and now we're cooking.

Redownloaded 25th hour, and cleaned it up. I can't do this for all of them...
Going to try to write a new clean script.

Need to reframe the goals here.
I want two scripts to come out of this, one with the bold tags and one with just the <b> tags.
The one with the bold tags remaining should be the one displayed, and the one with just the beginning tags is used to generate the precompute timeseries.
Lewis did a better job of cleaning these things up, and he removed all CAPS rather than rely on the <b> tags for the direction.
I'm trying to thing of a better way to store these scripts...just a better overall format that I can get them to...but this is getting a little bit away from me.

I redownloaded all of them, and my clean2 script did a better job at cleaning them all up.
So I moved everything back into the rawer directory.
Ran checkclean.sh again and I only got 7 bad eggs.

So far the steps are
. clean.sh
. checkclean.sh
. clean2.sh
cd rawer
mv trouble/* .
cd ..
# go clean some up individually from the .html.end.beg file
. clean3.sh
. clean4.sh

Manually deleted the 7 movies from that database that didn't work.
Now I have the two files, clean01 and clean04 that are the ones that I want.
Just need to update the python preprocessor to use those, and the javascript to pull the right one.
The preprocessor will use the more cleaned 04, and I will show the less clean 01.

25th hour causing me problems still, and the html is crap, so I deleted it out of the database.

Counting number of elements on a page:
\begin{verbatim}
  document.getElementsByTagName("circle").length
\end{verbatim}

Had to rename all of the 48-Hrs files.

In Ace Ventura, there are these \205 and \226 things. Damnit this is annoying, I'm not sure how Lewis did such a good job cleaning these things up.

I could try to write some sort of zaney file structure which captures these things, here's a description of how standard they should be:
\url{http://www.scriptologist.com/Magazine/Formatting/formatting.html}
installed dos2unix...giving up on ace ventura.

``After life'' is gone, file didn't exist.
Had to rename all of the Alien vs. Predator, and change it in the database.

This is VERY slow going so far.
I need to get them into a clean format.
Can I do it with a raw text file? Probably. I don't like the XML garbage.

Strip away all of the XML.
Delete all blank lines.
Scene direction is always caps, beginning with INT. or EXT.
Character lines are always the name with CAPS, spaced into the middle, and then lines with lots of space.
Description of scenes is without much space.
Within character dialogue, there are lines that have the description of how they are talking within parenthesis.

At first sight has bad characters.
Had to move all of the Austin Powers movies.
I think that they could even do well with a latex style formatting.
This is a bit insane though. Maybe someday if I'm really really bored.

Went to a monospace font, had to go down to size 5px.

Benny and Joon
Bottle Rocket
Brazil
Cinema Paradiso
Collateral
Cube
Days of Heaven
El Mariachi

Discovered a bug with showing the shift- it's using the full timeseries length to compute the refFextent...but the problem is that the word vectors which it's going to use to draw the shift are actually a bit smaller than that...they're one less in size.
Then it may be a rounding issue.
For now, I'm just going to subtract one from the refFextent when it's using fulltimeseries.length.
Okay got this working, the right hand side of the comparison area seems a bit off though, not sure why.

Skipped, but didn't delete:
Enemy of the State
Escape From L A
Freddy vs  Jason
Frequency
G I  Jane
G I  Joe The Rise of Cobra
Highlander Endgam
John-Q
The Majestic
The Rage Carrie 2

Here is how to reprocess them from the start:
=============================================

Unpack the scripts from Lewis, the two zip files.
unzip scripts.zip -d rawer-take2



Get the titles of all of the scripts into a better format, just the titles, with none of ",The" business (using text editor magic).
Specific things to fix: (note the double space)
\([a-zA-Z ]+\), The -> The \1
\([a-zA-Z ]+\), A -> A \1
remove apostrophes:
' -> 
remove dots (replace with nothing)
. -> 
  ->
Fix this one:
L Avventura (The Adventure)

Run addIMDB....py to make all of the database entries.
It may take a lot of failures to get through this script.
It dumps the ones for which it couldn't get info into noresult.txt.

Now, let's process them.
Run the chopmovies, just to rename them.
It fails on a couple, fix them like it tells you to.

mv rawer-take2/Talented-Mr.-Ripley,-The.html rawer-take2/The-Talented-Mr-Ripley.html
mv rawer-take2/Majestic\,-The-\(The-Bijou\).html rawer-take2/The-Majestic-\(The-Bijou\).html

Edit the database entry for talented mr ripley to remove the dot.

Now run the shell script to make all sorts of different processed versions.
. clean.sh

Have to get these two manually using wget, the python shell escape doesn't do the job:

Benny-&-Joon.html
You've-Got-Mail.html

Have to move this guy by hand:

mv rawer-take2/redownload/Who-Framed-Roger-Rabbit\?.html rawer-take2/redownload/Who-Framed-Roger-Rabbit%3f.html 

Fixed "there's something about mary" by hand, reran clean.sh, and clean-pass2.sh.

unzip
list files into the .txt
clean up the .txt with regex's
rename all the files using python
run the clean script
run python to redownload most of them
download the couple that don't work with python
rerun the python script to rename them
run the clean-pass2 script
make sure they are all in the database (or create them), noting the ones that failed parsing both ways
process them into timeseries!

2015-06-15

Re-running the python script to do the final processing step, and to save the database models which didn't work in the final process this time.
Also, replacing "." with "-" in the raw title, which is already doing a better job at getting filenames.

It will definitely take a few hours to crunch through.
Have to do everything myself if I want to understand it....

Now to go ahead and make a page.
I'll need to write another script for the backend part which fills out the happs from the database model and writes a word-vector file.
Made `word-vectors/full` folder and going to push the full script word vectors into that.

2016-11-04

Started digging in again yesterday.
Lots added to the end of chopmovies.py.
Confirmed there are 1090 in scriptsClean folder from Lewis, and working on processing them even better in the raw folder (points to rawer-take2), made a .txt version and a .txt.clean version.
Also made sure 1090 database model entries, and there are 40 or so still missing IMDB info (there were 1091, cleaned it up).
Part of the chopmovies.py script is a for loop that will ping the API, I think that there are about 20 to go yet.
The open database has info that I don't have saved in the database models, but the actor/director info isn't as good, so try to finish with the apathetic API first, then I'll go back and add the IMDB rating (e.g., 7.2/10), number of reviews from users info.
http://www.omdbapi.com/




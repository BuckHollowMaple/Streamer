# Streamer

Instantly streams for free Movies, TV Shows, Music, Radio, Books and more!

You're going to need to re-program some of stream.py for the current primewire site format, since they change it.

## Usage:
  python stream.py "COMMAND"
  
  python stream.py "stream the show reno 911 season 2"

## GENERAL COMMANDS:

 [stream the next show] - Plays the next episode of the previously streamed show
 
 [stream the previous show] - Plays the previous episode
 
 [stream the show] TITLE OF SHOW [latest episode] - Plays the last available episode of a show
 
 [stream the weather] - Shows radar and tells you the weekly forecast
 
 [stream the episode of] TITLE OF SHOW [when/where] DESCRIPTION OF SHOW - Finds & plays show from desc.
 
 [stream a suggestion for a] GENRE | TITLE - Suggests a movie/show of a given genre
 
 [stream who played in] TITLE - Tells you actors that played in movie/show
 
 [stream what] [movie/show] ACTOR [played in] - Tells you movies/shows that an actor played in
 
 [stream what year was] TITLE [released] - Tells the year a movie/show was released
 
 [stream the radio station] RADIO CALLSIGN - Streams radio
 
 [stream the radio station] DESCRIPTION - Finds & streams radio station from description
 
 [stream youtube for] DESCRIPTION - Streams youtube under the description
 
 [stream the movie] TITLE - Streams the movie
 
 [stream the show] TITLE - Streams the show at season 1 episode 1
 
 [stream the show] TITLE [season X] - Streams the show at season X episode 1
 
 [stream the show] TITLE [season X episode Y] - Streams the show at season X episode Y
 
## RPI COMMANDS:

--- IF A STREAM IS PLAYING, MUTE IT WITH YOUR REMOTE BEFORE USING THESE COMMANDS ---

[turn on] - Turns the TV on

[turn off] - Turns the TV off

[volume to] VOLUME PERCENT - Changes the volume to the percent of the number given

[volume up] - Turns the volume up

[volume down] - Turns the volume down

[pause stream] - Pauses the stream

[play stream] - Plays the paused stream

[stop stream] - Stops the stream and saves its position to resume later

[resume stream] - Resumes the stream at the saved position from [stop stream]

[stream help] - Gives you a generic listing of all commands available

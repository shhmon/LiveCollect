# LiveCollect
LiveCollect is a tool for automated collection of sample dependencies for Ableton Live projects. 

`python3 livecollect.py /path/to/liveset/file.als`

## What is this?
If you're like me, then putting samples into your user library while producing is kind of a vibe killer. By omitting this step however, you surrender your ability to move audio files from your download folder without stuff exploding. Also, it is virtually impossible to move projects to another machine. This was written to adress this by copying all external samples to the project folder and updating their references (without manually having to open projects and pressing "Collect all and save"). It currently only supports Live 11 projects, but I'm working on getting it compatible with Live 10 and 9 as well.

***Note:** I take no responsibility for what this does to your project files*
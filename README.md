chaperone.py
============

Chaperone is a command line, time tracking utility.

### Getting started

To get started, out `chaperone.py` and edit the path to the file with your
hours. And then run:

    chaperone.py -i

### API

Print out what I'm currently working on.

    chaperone.py

Print out all my projects:

    chaperone.py --list-projects
    chaperone.py -l

Add a new project:

    chaperone.py --add-project "Project name"
    chaperone.py -a "Project name"

Print out how many billable hours I have worked this week:

    chaperone.py --billable
    chaperone.py -b

Print out daily report (how many hours I have worked today):

    chaperone.py --report
    chaperone.py -r

Tell chaperone.py that I have started working on a project:

    chaperone.py --start "Project name"
    chaperone.py --start ProjectName
    chaperone.py -s "Project name"
    chaperone.py -s ProjectName

Tell chaperone.py that I have stopped/paused working on the current project:

    chaperone.py --pause
    chaperone.py -p

Resume a paused project:

    chaperone.py --start
    chaperone.py -s

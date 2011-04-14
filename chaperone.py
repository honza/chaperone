#!/usr/bin/env python
"""
chaperone is a command line, time tracking utility
"""
import os
import sys
import json
from datetime import datetime, timedelta
from optparse import OptionParser


ROOT = os.path.abspath(os.path.dirname(__file__))
DATA_NAME = 'hours.txt'
DATA_PATH = os.path.join(ROOT, DATA_NAME)


class Entry(object):

    start = None
    end = None
    project = None
    comment = None
    length = None

    def __init__(self, object):
        start = "%s %s" % (object['date'], object['start'],)
        self.start = datetime.strptime(start, "%Y-%m-%d %H:%M")
        try:
            end = "%s %s" % (object['date'], object['end'],)
            self.end = datetime.strptime(end, "%Y-%m-%d %H:%M")
            self.calculate_length()
        except:
            pass

        self.comment = object['comment']
        self.project = object['project']

    def __str__(self):
        return "%s: %s: %s" % (self.start.strftime("%Y-%m-%d %H:%M"),
                self.project, self.comment,)

    def calculate_length(self):
        if  self.is_active():
            return
        self.length = self.end - self.start

    def is_active(self):
        if self.end:
            return False
        else:
            return True

    def this_week(self):
        today = datetime.now()
        delta = int(today.strftime("%w")) - 1
        monday = today - timedelta(days=delta)
        monday = datetime(monday.year, monday.month, monday.day, 0, 0)
        d = self.start - monday
        if d.days >= 0:
            return True
        else:
            return False

    def today(self):
        today = datetime.now()
        delta = int(today.strftime("%H"))
        x = today - timedelta(hours=delta)
        x = today - x
        y = today - self.start
        if x > y:
            return True
        else:
            return False

        return self.project

    def to_json(self):
        d = {
            "date": self.start.strftime("%Y-%m-%d"),
            "start": self.start.strftime("%H:%M"),
            "comment": self.comment,
            "project": self.project
        }
        try:
            d['end'] = self.end.strftime("%H:%M")
        except:
            pass
        return d


class EntryCollection(object):

    entries = []
    active = None

    def __init__(self, entries):
        self.entries = entries
        self.set_active()

    def set_active(self):
        for e in self.entries:
            if e.is_active():
                self.active = e
                break

    def this_week(self):
        r = []
        for e in self.entries:
            if e.this_week():
                r.append(e)
        return r

    def today(self):
        r = []
        for e in self.entries:
            if e.today():
                r.append(e)
        return r

    def project(self, project):
        r = []
        for e in self.entries:
            if e.project == project:
                r.append(e)
        return r

    def append(self, item):
        self.entries.append(item)

    def to_json(self):
        return [e.to_json() for e in self.entries]


class Chaperone(object):

    data = None
    projects = []
    entries = []

    def __init__(self, init=False):
        if init:
            if os.path.exists(DATA_PATH):
                print 'Path exists: %s' % DATA_PATH
                return
            f = open(DATA_PATH, 'w')
            f.write("{\"projects\": [], \"entries\": []}")
            f.close()
            print "All set. You can start entering hours."
            return

        if not os.path.exists(DATA_PATH):
            print "Can't find your data file."
            sys.exit(1)

        self._load_data()

    def finish(self):
        """
        Render data as JSON and save to disk
        """
        data = {
            'projects': self.projects,
            'entries': self.entries.to_json()
        }

        f = open(DATA_PATH, 'w')
        f.write(json.dumps(data, indent=4))
        f.close()

    def _load_data(self):
        if os.path.exists(DATA_PATH):
            f = open(DATA_PATH, 'r')
            contents = f.read()
            f.close()
            if not contents:
                print 'No data to read'
                return
            self.data = json.loads(contents)
            self.projects = self.data['projects']
            self.entries = self.data['entries']
            self._parse_entries()
        else:
            print "Couldn't find your data file."
            return

    def _parse_entries(self):
        entries = self.entries
        self.entries = []

        for entry in entries:
            self.entries.append(Entry(entry))

        self.entries = EntryCollection(self.entries)

    def list_entries(self):
        for entry in self.entries:
            print entry.comment

    def _entries_this_week(self):
        for e in self.entries.this_week():
            print e.comment

    def entries_by_project(self, project):
        if not project in self.projects:
            print "Unknown project"
        else:
            for e in self.entries.project(project):
                print e

    # public calls

    def list_projects(self):
        print 'Projects:'
        for project in self.projects:
            print project

    def add_project(self, project):
        if not project in self.projects:
            self.projects.append(project)
        else:
            print 'Project already exists'
        self.finish()

    def billable(self):
        entries = self.entries.this_week()
        now = datetime.now()
        total = timedelta()
        for e in entries:
            if not e.is_active():
                total += e.length
            else:
                total += (now - e.start)
        t = self.format_timedelta(total)
        print "This week you've worked %s." % t

    def format_timedelta(self, td):
        minute = 60
        hour = 60 * minute
        t = td.seconds
        try:
            d = td.days
        except:
            d = None
        if t < hour:
            m = t / minute
            if int(m) == 1:
                return "%d minute" % int(t / minute)
            return "%d minutes" % int(t / minute)
        h = int(t / hour)
        m = t - (h * hour)
        m = int(m / minute)
        if d:
            h += d * 24
        if m == 1:
            m_text = "%d minute" % m
        else:
            m_text = "%d minutes" % m
        if h is 1:
            return "%d hour %s" % (int(h), m_text)
        return "%d hours %s" % (int(h), m_text)

    def report(self):
        total = timedelta()
        now = datetime.now()
        for e in self.entries.today():
            if not e.is_active():
                total += e.length
            else:
                total += (now - e.start)

        t = self.format_timedelta(total)
        print "Today you've worked %s." % t

    def start(self, project):
        self.get_active()
        if self.active:
            print "You're already working on something. Stop doing that first."
            return
        now = datetime.now()
        entry = {
            "date": now.strftime("%Y-%m-%d"),
            "start": now.strftime("%H:%M"),
            "project": project,
            "comment": ""
        }
        self.entries.append(Entry(entry))
        self.finish()

    def pause(self):
        self.get_active()
        if not self.active:
            print "You're not working on anything."
            return
        now = datetime.now()
        self.entries.active.end = now
        self.finish()
        print "You've stopped working on %s." % (self.entries.active.project)

    def get_active(self):
        self.active = self.entries.active


if __name__ == '__main__':
    os.system("clear")
    parser = OptionParser()

    parser.add_option("-l", "--list-projects", action="store_true",
            dest="list_projects")

    parser.add_option("-a", "--add-project", action="store",
            dest="add_project")

    parser.add_option("-b", "--billable", action="store_true", dest="billable")
    parser.add_option("-r", "--report", action="store_true", dest="report")
    parser.add_option("-s", "--start", action="store", dest="start")

    parser.add_option("-p", "--pause", action="store_true", dest="pause")
    parser.add_option("-i", "--init", action="store_true", dest="init")

    (options, args) = parser.parse_args()

    if options.init:
        c = Chaperone(init=True)
        sys.exit(1)
    else:
        c = Chaperone()

    if options.list_projects:
        c.list_projects()

    elif options.add_project:
        c.add_project(options.add_project)

    elif options.billable:
        c.billable()

    elif options.report:
        c.report()

    elif options.start:
        c.start(options.start)

    elif options.pause:
        c.pause()

    else:
        # no arguments - display what I'm working on
        c.get_active()
        print c.active

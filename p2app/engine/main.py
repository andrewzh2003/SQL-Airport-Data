# p2app/engine/main.py
#
# ICS 33 Fall 2022
# Project 2: Learning to Fly
#
# An object that represents the engine of the application.
#
# This is the outermost layer of the part of the program that you'll need to build,
# which means that YOU WILL DEFINITELY NEED TO MAKE CHANGES TO THIS FILE.

import p2app.events as e
import sqlite3

class Engine:
    """An object that represents the application's engine, whose main role is to
    process events sent to it by the user interface, then generate events that are
    sent back to the user interface in response, allowing the user interface to be
    unaware of any details of how the engine is implemented.
    """

    def __init__(self):
        """Initializes the engine"""
        self._conn = None

    def process_event(self, event):
        """A generator function that processes one event sent from the user interface,
        yielding zero or more events in response."""

        # app and database stuff here
        if isinstance(event, e.app.QuitInitiatedEvent):
            yield e.app.EndApplicationEvent()

        if isinstance(event, e.database.OpenDatabaseEvent):
            try:
                conn = sqlite3.connect(event._path)

            except:
                string = "ERROR: database not valid"
                yield e.database.DatabaseOpenFailedEvent(string)
            self._conn = conn
            self._conn.execute("PRAGMA foreign_keys = ON;")
            yield e.database.DatabaseOpenedEvent(event._path)

        if isinstance(event, e.database.CloseDatabaseEvent):
            yield e.database.DatabaseClosedEvent()


        # THIS IS FOR ALL OF THE COUNTRIES EVENTS
        if isinstance(event, e.continents.StartContinentSearchEvent):
            condition1 = True
            condition2 = True
            if event._continent_code == None:
                condition1 = False
            if event._name == None:
                condition2 = False
            cur = self._conn.cursor()
            contList = [a for a in cur.execute("SELECT c.continent_id, c.continent_code, name FROM continent as c")]
            rList = []
            for i in contList:
                cond4 = True
                if condition1:
                    if i[1] != event._continent_code:
                        cond4 = False
                if condition2:
                    if i[2] != event._name:
                        cond4 = False
                if cond4:
                    rList.append(i)
            if rList != []:
                for i in rList:
                    x = e.continents.Continent(i[0],i[1],i[2])
                    yield e.continents.ContinentSearchResultEvent(x)
            else:
                pass

        if isinstance(event, e.continents.LoadContinentEvent):
            try:
                cur = self._conn.cursor()
                contList = [a for a in cur.execute("SELECT c.continent_id, c.continent_code, name FROM continent as c")]
                rList = []
                for i in contList:
                    if i[0] == event._continent_id:
                        rList.append(i)
                if rList != []:
                    for i in rList:
                        x = e.continents.Continent(i[0], i[1], i[2])
                        yield e.continents.ContinentLoadedEvent(x)
                else:
                    pass
            except:
                yield e.app.ErrorEvent('Error loading continent')

        if isinstance(event, e.continents.SaveNewContinentEvent):
            cur = self._conn.cursor()
            contList = [a for a in cur.execute("SELECT c.continent_id, c.continent_code, name FROM continent as c")]
            ID = 0
            condtion = True
            for i in contList:
                if i[0] > ID:
                    ID = i[0]
            ID += 1
            x = event._continent._replace(continent_id = ID)
            try:
                self._conn.execute("INSERT INTO continent (continent_id, continent_code, name) "
                                   "VALUES (:continent_id, :continent_code, :name);",
                                   {'continent_id': event._continent[0],
                                    'continent_code': event._continent[1],
                                    'name':event._continent[2]})
                self._conn.commit()
                yield e.continents.ContinentSavedEvent(x)
            except:
                yield e.continents.SaveContinentFailedEvent('Missing or duplicate information')

        if isinstance(event, e.continents.SaveContinentEvent):
            cur = self._conn.cursor()
            contList = [a for a in cur.execute("SELECT c.continent_id, c.continent_code, name FROM continent as c")]
            try:
                self._conn.execute("UPDATE continent "
                                   "SET continent_code = (:continent_code), name = (:name)"
                                   "WHERE continent = (:continent_id);",
                                   {'continent_id': event._continent[0],
                                    'continent_code': event._continent[1],
                                    'name': event._continent[2]})
                self._conn.commit()
                yield e.continents.ContinentSavedEvent(x)
            except:
                yield e.continents.SaveContinentFailedEvent('Missing or duplicate information')



        # THIS WILL BE FOR COUNTRIES
        if isinstance(event, e.countries.StartCountrySearchEvent):
            cur = self._conn.cursor()
            condition1 = True
            condition2 = True
            if event._country_code == None:
                condition1 = False
            if event._name == None:
                condition2 = False
            counList = [a for a in cur.execute("SELECT country_id, country_code, name, continent_id, wikipedia_link, keywords FROM country")]
            rList = []
            for i in counList:
                cond4 = True
                if condition1:
                    if i[1] != event._country_code:
                        cond4 = False
                if condition2:
                    if i[2] != event._name:
                        cond4 = False
                if cond4:
                    rList.append(i)
            if rList != []:
                for i in rList:
                    x = e.countries.Country(i[0], i[1], i[2], i[3], i[4], i[5])
                    yield e.countries.CountrySearchResultEvent(x)

        if isinstance(event, e.countries.LoadCountryEvent):
            try:
                cur = self._conn.cursor()
                counList = [a for a in cur.execute("SELECT country_id, country_code, name, continent_id, wikipedia_link, keywords FROM country")]
                rList = []
                for i in counList:
                    if i[0] == event._country_id:
                        rList.append(i)
                    else:
                        pass
                if rList != []:
                    for i in rList:
                        x = e.countries.Country(i[0], i[1], i[2], i[3], i[4], i[5])
                        yield e.countries.CountryLoadedEvent(x)
                else:
                    pass
            except:
                yield e.app.ErrorEvent('Error loading country')
        if isinstance(event, e.countries.SaveNewCountryEvent):
            condition = True

            cur = self._conn.cursor()
            counList = [a for a in cur.execute(
                "SELECT country_id, country_code, name, continent_id, wikipedia_link, keywords FROM country")]

            ID = 0
            for i in counList:
                if i[0] > ID:
                    ID = i[0]
            ID += 1

            x = event._country._replace(country_id = ID)

            contList = [a for a in cur.execute(
                "SELECT c.continent_id FROM continent as c")]
            cList1 = [a[0] for a in contList]

            if event._country[1].strip() == '' or event._country[2].strip() == '' or event._country[4].strip() == '':
                condition = False
                yield e.countries.SaveCountryFailedEvent('Blank string for code and name or wiki')
            if event._country[4] == None:
                condition = False
                yield e.countries.SaveCountryFailedEvent('Blank for wiki')
            if event._country[3] not in cList1:
                condition = False
                yield e.countries.SaveCountryFailedEvent('Invalid Continent ID')

            if condition:
                try:
                    self._conn.execute(
                        'INSERT INTO country (country_id, country_code, name, continent_id, wikipedia_link, keywords) VALUES (:country_id, :country_code, :name, :continent_id, :wikipedia_link, :keywords);',
                                    {'country_id': event._country[0],
                                     'country_code': event._country[1],
                                     'name': event._country[2],
                                     'continent_id': event._country[3],
                                     'wikipedia_link': event._country[4],
                                     'keywords': event._country[5]})
                    self._conn.commit()
                    yield e.countries.CountrySavedEvent(x)
                except:
                    yield e.countries.SaveCountryFailedEvent('Missing or duplicate information')

        if isinstance(event, e.countries.SaveCountryEvent):
            condition = True

            cur = self._conn.cursor()
            contList = [a for a in cur.execute(
                "SELECT c.continent_id FROM continent as c")]
            cList1 = [a[0] for a in contList]

            if event._country[1].strip() == '' or event._country[2].strip() == '':
                condition = False
                yield e.countries.SaveCountryFailedEvent('Blank for code or name or wiki')
            if event._country[4] == None:
                condition = False
                yield e.countries.SaveCountryFailedEvent('Blank wiki')
            if event._country[3] not in cList1:
                condition = False
                yield e.countries.SaveCountryFailedEvent('Invalid Continent ID')
            if condition:
                try:
                    self._conn.execute('UPDATE country '
                                       'SET country_code = (:country_code), name = (:name), continent_id = (:continent_id), wikipedia_link = (:wikipedia_link),keywords = (:keywords)'
                        'WHERE country_id = (:country_id);',
                        {'country_id': event._country[0],
                         'country_code': event._country[1],
                         'name': event._country[2],
                         'continent_id': event._country[3],
                         'wikipedia_link': event._country[4],
                         'keywords': event._country[5]})
                    self._conn.commit()
                    yield e.countries.CountrySavedEvent(event._country)
                except:
                    yield e.countries.SaveCountryFailedEvent('Missing or duplicate information')
            else:
                pass

        # THIS WILL BE FOR REGIONS

        if isinstance(event, e.regions.StartRegionSearchEvent):
            cur = self._conn.cursor()
            condition1 = True
            condition2 = True
            condition3 = True
            if event._region_code == None:
                condition1 = False
            if event._local_code == None:
                condition2 = False
            if event._name == None:
                condition3 = False
            regList = [a for a in cur.execute('SELECT region_id, region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords FROM region')]
            for i in regList:
                cond4 = True
                if condition1:
                    if i[1] != event._region_code:
                        cond4 = False
                if condition2:
                    if i[2] != event._local_code:
                        cond4 = False
                if condition3:
                    if i[3] != event._name:
                        cond4 = False
                if cond4:
                    x = e.regions.Region(i[0], i[1], i[2], i[3], i[4], i[5],i[6], i[7])
                    yield e.regions.RegionSearchResultEvent(x)

        if isinstance(event, e.regions.LoadRegionEvent):
            try:
                cur = self._conn.cursor()
                regList = [a for a in cur.execute('SELECT region_id, region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords FROM region')]
                for i in regList:
                    if i[0] == event._region_id:
                        x = e.regions.Region(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7])
                        yield e.regions.RegionLoadedEvent(x)
            except:
                yield e.app.ErrorEvent('Error loading region')

        if isinstance(event, e.regions.SaveNewRegionEvent):
            condition = True
            cur = self._conn.cursor()
            regList = [a for a in cur.execute(
                'SELECT region_id, region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords FROM region')]
            ID = 0
            for i in regList:
                if i[0] > ID:
                    ID = i[0] + 1
            x = event._region._replace(region_id = ID)
            contList = [a for a in cur.execute(
                "SELECT c.continent_id FROM continent as c")]
            cList1 = [a[0] for a in contList]
            counList = [a for a in cur.execute(
                "SELECT country_id FROM country")]
            counList1 = [a[0] for a in counList]
            if event._region[1].strip() == '' or event._region[2].strip() == '' or event._region[3].strip() == '':
                condition = False
                yield e.regions.SaveRegionFailedEvent('Blank for region code, local code or name')
            if event._region[4] not in cList1:
                condition = False
                yield e.regions.SaveRegionFailedEvent('Invalid Continent ID')
            if event._region[5] not in counList1:
                condition = False
                yield e.regions.SaveRegionFailedEvent('Invalid Country ID')
            if condition:
                try:
                    self._conn.execute(
                        'INSERT INTO region (region_id, region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords) VALUES (:region_id, :region_code, :local_code, :name, :continent_id, :country_id, :wikipedia_link, :keywords);',
                        {'region_id': event._region[0],
                         'region_code': event._region[1],
                         'local_code': event._region[2],
                         'name': event._region[3],
                         'continent_id': event._region[4],
                         'country_id': event._region[5],
                         'wikipedia_link': event._region[6],
                         'keywords': event._region[7]})
                    self._conn.commit()
                    yield e.regions.RegionSavedEvent(event._region)
                except:
                    yield e.regions.SaveRegionFailedEvent('Missing or duplicate information')
            else:
                pass

        if isinstance(event, e.regions.SaveRegionEvent):
            condition = True
            cur = self._conn.cursor()
            contList = [a for a in cur.execute(
                "SELECT c.continent_id FROM continent as c")]
            cList1 = [a[0] for a in contList]
            counList = [a for a in cur.execute(
                "SELECT country_id FROM country")]
            counList1 = [a[0] for a in counList]
            if event._region[1].strip() == '' or event._region[2].strip() == '' or event._region[
                3].strip() == '':
                condition = False
                yield e.regions.SaveRegionFailedEvent('Blank for region code, local code or name')
            if event._region[4] not in cList1:
                condition = False
                yield e.regions.SaveRegionFailedEvent('Invalid Continent ID')
            if event._region[5] not in counList1:
                condition = False
                yield e.regions.SaveRegionFailedEvent('Invalid Country ID')
            if condition:
                try:
                    self._conn.execute(
                        'UPDATE region '
                        'SET region_code = (:region_code), local_code = (:local_code), name = (:name), continent_id = (:continent_id), country_id = (:country_id), wikipedia_link = (:wikipedia_link), keywords = (:keywords) '
                        'WHERE region_id = (:region_id);',
                        {'region_id': event._region[0],
                         'region_code': event._region[1],
                         'local_code': event._region[2],
                         'name': event._region[3],
                         'continent_id': event._region[4],
                         'country_id': event._region[5],
                         'wikipedia_link': event._region[6],
                         'keywords': event._region[7]})
                    self._conn.commit()
                    yield e.regions.RegionSavedEvent(event._region)
                except:
                    yield e.regions.SaveRegionFailedEvent('Missing or duplicate information')
            else:
                pass




        # This is a way to write a generator function that always yields zero values.
        # You'll want to remove this and replace it with your own code, once you start
        # writing your engine, but this at least allows the program to run.

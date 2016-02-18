#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""

    conn = connect()
    curs = conn.cursor()

    SQL = "delete from Match"  # DB name is Record
    curs.execute(SQL)  # SQL to delete from db

    conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""

    conn = connect()
    curs = conn.cursor()

    SQL = "delete from Player"  # DB name is Player
    curs.execute(SQL)  # SQL to delete from db

    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""

    conn = connect()
    curs = conn.cursor()    

    SQL = "select count(id) from Player"  # SQL to counnt ids
    curs.execute(SQL)

    row = curs.fetchone()
    cnt = row[0]
    return cnt


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """

    conn = connect()
    curs = conn.cursor()
    # SQL to insert name
    SQL = 'insert into Player (name) values (%s)' % ("%s")  
    curs.execute(SQL, (name,))

    conn.commit()
    conn.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """

    conn = connect()
    curs = conn.cursor()

    SQL = "select id, name, wins, matches from Standing"  # SQL to counnt ids
    curs.execute(SQL)

    rows = curs.fetchall()

    # convert tuple as speced by api
    standings = [(row[0], row[1], row[2], row[3]) for row in rows]

    return standings


def reportMatch(winner, loser, tie=None):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
      tie: (optional) if set and == True then result is a tie
    """

    conn = connect()
    curs = conn.cursor()
    if (winner == loser):
        # This is bye case since we have no match available
        SQL_bye = 'insert into Match values (%s, %s, %s)' % (
            "%s", "%s", "%s")
        curs.execute(SQL_bye, (winner, loser, "win"))
    else:
        winner_result = 'win'
        loser_result = 'loss'

        if (tie is not None) and (tie is True):
            # if we have a tie then irregardless of winner/loser
            # we set result for both to draw
            winner_result = 'draw'
            loser_result = 'draw'

        # Construct SQL statements,
        # NOTE! although use of interpolation is present we
        # construct SQL statement such that user values are
        # left to cursor.execute to handle by subbing back in
        # %s where necessary

        SQL_winner = 'insert into Match values (%s, %s, %s)' % (
            "%s", "%s", "%s")
        SQL_loser = 'insert into Match values (%s, %s, %s)' % (
            "%s", "%s", "%s")

        curs.execute(SQL_winner, (winner, loser, winner_result))
        curs.execute(SQL_loser, (loser, winner, loser_result))

    conn.commit()
    conn.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    conn = connect()
    curs = conn.cursor()

    # SQL to retrieve standings + bye info
    STANDINGS_WITH_BYE_SQL = '''
    SELECT Standing.id, Standing.name, Num_bye.byes
    FROM Standing INNER JOIN Num_bye
    ON Standing.id = Num_bye.id
    ORDER BY Standing.wins DESC, Standing.opponent_wins DESC
    ''' 
    curs.execute(STANDINGS_WITH_BYE_SQL)

    rows = curs.fetchall()

    # Bit of a dilemna on whether to use len or DB call
    # to count number of rows, player counnt should be
    # identical here to number of rows in standings
    # Although specs for exceed state all counnt/aggregate
    # must use db so i shall do so
    length = countPlayers()
    assign_bye = False
    if(length % 2 == 1):
        assign_bye = True
    # pair and convert tuple as speced by api definition

    
    pairs = []
    while(length > 1):
        if((assign_bye is True) and (rows[0][2] == 0)):
            i = 0
            while(i < length and rows[i][2] != 0):
                i = i + 1
            if(i == length):
                raise ValueError(
                    "Everyone already has a bye! Cannnot construct valid swiss pairinng")
            pairs.append((rows[i][0], rows[i][1], rows[i][0], rows[i][1]))
            assign_bye = False
            length = length - 1
            del rows[0]
        else:
            opponent = findClosestOpponnent(0, 1, rows, length)
            pairs.append((rows[0][0], rows[0][1], rows[opponent][0], rows[opponent][1]))
            length = length - 2
            del rows[opponent]
            del rows[0] 

    return pairs

def isRematch(player1, player2):
    """Returns true or false if two players have already played eachother

    Args:
        player1:  the id number of one player
        player2:  the id of the potential opponent to check
    Returns:
        True or False depending on if they have played each other
    """


    conn = connect()
    curs = conn.cursor()

    # SQL to determie if two players have played each other
    IS_REMATCH_SQL = "SELECT EXISTS(SELECT 1 FROM Match WHERE player1 = %s and player2 = %s)" % ("%s", "%s")
    curs.execute(IS_REMATCH_SQL, (player1, player2))
    result = curs.fetchone()

    return result[0]

def findClosestOpponnent(player1, candidate, standings_tuple, length):
    """ Returns index of closest opponent that is not a isRematch

    Args:
        player1: the index of player in the tuple we are finding opponent for
        candidate: the candidate index in tuple for possible opponent
        standings_tuple: list/tuple of remaining players ordered in standings
        length: length of standings tuple, not sure if len counts as aggregation
    Returns:
        Index of integer
    """


    # Simple recursive call that checks if this candidate is satisfactory
    # if not we recurse down to next closest player in standings
    if(candidate >= length):
        return player1 + 1
    elif not isRematch(standings_tuple[player1][0], standings_tuple[candidate][0]):
        return candidate
    else:
        return findClosestOpponnent(player1, candidate + 1, standings_tuple, length)

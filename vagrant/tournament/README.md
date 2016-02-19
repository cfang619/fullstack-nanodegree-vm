# Tournament Results

## Files
tournament.sql  - This file sets up database schema, creating a new database called `tournament`
tournament.py - python module that provides access to the `tournament` database via a library of functions (add/delete/query) to a client program
tournament_test.py - this is a client program which will uses the functions written in tournament.py. Is mainly used to test said functions.

## Installation and Setup

0. (Assumption is made that workstation already has python 2.7.* and Postgresql installed)
1. (optional) Fork from the following repo link: https://github.com/cfang619/fullstack-nanodegree-vm
2. Clone project to a folder: `git clone https://github.com/cfang619/fullstack-nanodegree-vm.git`
  * Optionally you may use your own forked repo link
3. There should now be a folder called `fullstack`
4. Navigate into that directory all the way to: `./fullstack/vagrant/tournament`

## Usage
1. After completing setup/installation you should be in directory `./fullstack/vagrant/tournament`
  * If not then navigate to said directory.
2. In order to setup database execute following command to launch psql command line interface: `psql`
3. Run `\i tournament.sql` to execute the SQL commands within that file.
4. Run `python tournament_test.py` to execute included test client program to exercise functions in module tournament.py.

## Authors
Clement Fang
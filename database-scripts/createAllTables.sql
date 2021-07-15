# Do this one first then ziliaTableMetadataExtraction.sql

CREATE TABLE spectralfiles (path text, md5 text, fileId integer primary key autoincrement, 
	monkeyId text, date text, region text, 
	eye text, timeline text, comments text);

CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE monkeys (name text, monkeyId text);
CREATE TABLE spectra (wavelength real, intensity real, fileId integer, path text, column text, md5 text);
CREATE INDEX md5Idx on spectra (md5);
CREATE INDEX colIdx on spectra (column);
CREATE INDEX wavelengthIdx on spectra (wavelength);

CREATE INDEX md5Idx2 on spectralfiles (md5);
CREATE INDEX mId on spectralFiles (monkeyId);
CREATE INDEX mId2 on monkeys (id);

CREATE TABLE bloodfiles (path text, md5 text, saturation real, intensity real, led text, comment text);
CREATE TABLE bloodspectra (wavelength real, intensity real, fileId integer, path text, column text, md5 text);
CREATE INDEX md5Idx3 on bloodspectra (md5);
CREATE INDEX wavelengthIdx2 on bloodspectra (wavelength);
CREATE TABLE imagefiles (path text, md5 text, id integer primary key autoincrement,
	monkeyId text, date text, region text, 
	eye text, timeline text, comments text);


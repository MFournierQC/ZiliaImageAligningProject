from dcclab.database import *
import numpy as np

class ZiliaDB(Database):
    statementFromAllJoin = "from spectra as s, spectralFiles as f, monkeys as m where s.md5 = f.md5 and f.monkeyId = m.id"
    statementFromSpectra = "from spectra as s"

    def __init__(self, ziliaDbPath='zilia.db'):
        super().__init__(ziliaDbPath, writePermission=False)
        self._wavelengths = None

    @property
    def wavelengths(self):
        if self._wavelengths is None:
            self._wavelengths = self.getWavelengths()

        return self._wavelengths

    def getWavelengths(self):
        self.execute(r"select distinct(wavelength) from spectra order by wavelength")
        rows = self.fetchAll()
        nTotal = len(rows)

        wavelengths = np.zeros(shape=(nTotal))
        for i,row in enumerate(rows):
            wavelengths[i] = row['wavelength']

        return wavelengths

    def getBloodWavelengths(self, range=(None,None)):
        if range[0] is None:
            min = 0
        if range[1] is None:
            max = 10000

        self.execute(r"select distinct(wavelength) from bloodspectra where wavelength >= {0} and wavelength <= {1} order by wavelength".format(min, max))
        rows = self.fetchAll()
        nTotal = len(rows)

        wavelengths = np.zeros(shape=(nTotal))
        for i,row in enumerate(rows):
            wavelengths[i] = row['wavelength']

        return wavelengths

    def getAcquisitionType(self):
        self.execute(r"select distinct(acquisition) from spectralFiles order by acquisition")
        rows = self.fetchAll()
        nTotal = len(rows)

        types = set()
        for row in rows:
            acquisition = row['acquisition']
            if acquisition is not None:
                types.add(acquisition)

        return sorted(types)

    def getColumns(self):
        self.execute(r"select distinct(column) from spectra order by column")
        rows = self.fetchAll()
        nTotal = len(rows)

        types = set()
        for row in rows:
            type = row['column']
            if re.match('raw', type) is not None:
                type = 'raw'
            types.add(type)

        return sorted(types)

    def getTargets(self):
        self.execute(r"select distinct(target) from spectralFiles order by target")
        rows = self.fetchAll()
        targets = []
        for row in rows:
            target = row['target']
            if target is not None:
                targets.append(target)
        return targets

    def getMonkeyNames(self):
        self.execute("select name from monkeys order by name")
        rows = self.fetchAll()
        names = []
        for row in rows:
            names.append(row['name'])
        return names

    def getRawIntensities(self, monkey=None, type=None ,target=None, column=None):
        stmnt = r"select s.wavelength, s.intensity, s.md5, s.column {0} ".format(self.statementFromAllJoin)

        if monkey is not None:
            stmnt += " and (m.id = '{0}' or m.name = '{0}')".format(monkey)

        if column is not None:
            stmnt += " and s.column like '{0}%'".format(column)

        if target is not None:
            stmnt += " and f.target = '{0}'".format(target)

        if type is not None:
            stmnt += " and f.acquisition = '{0}'".format(type)

        self.execute(stmnt)
        rows = self.fetchAll()
        nWavelengths = len(self.wavelengths)
        nSamples = len(rows)//nWavelengths
        spectra = np.zeros(shape=(nWavelengths, nSamples))
        for i,row in enumerate(rows):
            spectra[i%nWavelengths, i//nWavelengths] = float(row['intensity'])

        return spectra

    def getBloodIntensities(self, range=(None,None)):
        if range[0] is None:
            min = 0
        if range[1] is None:
            max = 10000


        stmnt = r"select s.wavelength, s.intensity,s.column, f.saturation from bloodspectra as s, bloodfiles as f where s.wavelength >= {0} and s.wavelength <= {1} and f.md5 = s.md5 and s.column like '%raw%' and f.saturation is not null order by s.md5, s.column, f.saturation, s.wavelength".format(min, max)

        self.execute(stmnt)
        rows = self.fetchAll()
        nWavelengths = len(self.getBloodWavelengths(range=(None,None)))
        nSamples = len(rows)//nWavelengths
        if nSamples*nWavelengths != len(rows):
            raise LogicalError("Wavelength field appears incorrect")

        spectra = np.zeros(shape=(nWavelengths, nSamples))
        for i,row in enumerate(rows):
            spectra[i%nWavelengths, i//nWavelengths] = float(row['intensity'])

        stmnt = r"select s.wavelength, s.intensity,s.column, f.saturation,f.path from bloodspectra as s, bloodfiles as f where s.wavelength >= {0} and s.wavelength <= {1} and f.md5 = s.md5 and s.column like '%raw%' and f.saturation is not null group by s.md5 order by s.md5, s.column, f.saturation, s.wavelength".format(min, max)
        self.execute(stmnt)
        rows = self.fetchAll()
        saturation = []
        for i,row in enumerate(rows):
            saturation.append(float(row['saturation']))

        return self.getBloodWavelengths(), spectra, saturation

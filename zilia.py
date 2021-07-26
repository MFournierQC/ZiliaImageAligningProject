from dcclab.database import *
import numpy as np
from skimage.io import imread
from skimage.color import rgb2gray

class ZiliaDB(Database):
    statementFromAllJoin = "from spectra as s, spectralfiles as f, monkeys as m where s.md5 = f.md5 and f.monkeyId = m.monkeyId"
    statementFromSpectra = "from spectra as s"

    def __init__(self, ziliaDbPath='zilia.db', root="/Volumes/GoogleDrive/My Drive/Zilia/ZDS-CE Zilia DataShare CERVO"):
        super().__init__(ziliaDbPath, writePermission=False)
        self._wavelengths = None
        self.root = root

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

    def getTimelines(self):
        self.execute(r"select distinct(timeline) from spectralfiles order by timeline")
        rows = self.fetchAll()
        nTotal = len(rows)

        types = set()
        for row in rows:
            timeline = row['timeline']
            if timeline is not None:
                types.add(timeline)

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

    def getRegions(self):
        self.execute(r"select distinct(region) from spectralfiles order by region")
        rows = self.fetchAll()
        targets = []
        for row in rows:
            target = row['region']
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

    def getImagePaths(self):
        self.execute("select path from imagefiles order by path")
        rows = self.fetchAll()
        paths = []
        for row in rows:
            paths.append(row['path'])
        return paths

    def getSpectraPaths(self):
        self.execute("select path from spectralfiles order by path")
        rows = self.fetchAll()
        paths = []
        for row in rows:
            paths.append(row['path'])
        return paths

    def getRGBImages(self, monkey=None, timeline=None, rlp=None, region=None, content=None, eye=None):
        stmnt = r"select path from imagefiles as f, monkeys as m where m.monkeyId = f.monkeyId "

        if monkey is not None:
            stmnt += " and (m.monkeyId = '{0}' or m.name = '{0}')".format(monkey)

        if rlp is not None:
            stmnt += " and f.rlp = {0}".format(rlp)

        if eye is not None:
            stmnt += " and f.eye = '{0}'".format(eye)

        if content is not None:
            stmnt += " and f.content = '{0}'".format(content)

        if region is not None:
            stmnt += " and f.region = '{0}'".format(region)

        if timeline is not None:
            stmnt += " and f.timeline like '%{0}%'".format(timeline)

        stmnt += " order by f.path"
        self.execute(stmnt)
        rows = self.fetchAll()

        images = []
        for row in rows:
            relativePath = row['path']
            absolutePath = "{0}/{1}".format(self.root, relativePath)
            image = imread(absolutePath)
            images.append(image)
            print("Loading {0}".format(absolutePath))

        return images

    def getGrayscaleEyeImages(self, monkey=None, timeline=None, rlp=None, region=None, eye=None):
        images = self.getRGBImages(monkey=monkey, timeline=timeline, rlp=rlp, region=region, content='eye', eye=eye)
        grayscaleImages = []
        for image in images:
            image[:,:,2] = 0 # For eye images, always strip blue channel before conversion
            grayscaleImages.append(rgb2gray(image))

        return grayscaleImages

    def getRawIntensities(self, monkey=None, timeline=None ,region=None, column=None):
        stmnt = r"select s.wavelength, s.intensity, s.md5, s.column {0} ".format(self.statementFromAllJoin)

        if monkey is not None:
            stmnt += " and (m.monkeyId = '{0}' or m.name = '{0}')".format(monkey)

        if column is not None:
            stmnt += " and s.column like '{0}%'".format(column)

        if region is not None:
            stmnt += " and f.region = '{0}'".format(region)

        if timeline is not None:
            stmnt += " and f.timeline = '{0}'".format(timeline)

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

from dcclab.database import *
import numpy as np
from skimage.io import imread
from skimage.color import rgb2gray
import time
import subprocess

class ZiliaDB(Database):
    statementFromAllJoin = "from spectra as s, spectralfiles as f, monkeys as m where s.md5 = f.md5 and f.monkeyId = m.monkeyId"
    statementFromSpectra = "from spectra as s"

    databaseCandidates = ["zilia.db", "../zilia.db", "/Volumes/Goliath/labdata/dcclab/zilia/zilia.db",
    r"z:\labdata\dcclab\zilia\zilia.db"]
    rootCandidates = [".", "..", "/Volumes/Goliath/labdata/dcclab/zilia", r"z:\labdata\dcclab\zilia",
    "U:/labdata/dcclab/zilia", "/Volumes/GoogleDrive/My Drive/Zilia/ZDS-CE Zilia DataShare CERVO"]

    @classmethod
    def findDatabasePath(cls) -> str:
        for path in cls.databaseCandidates:
            absPath = os.path.abspath(path)
            if os.path.exists(path):
                return absPath

        return None

    @classmethod
    def findDataFilesRoot(cls) -> str:
        ZiliaDB.addCyberduckPathsIfPresent()

        someRelativePath = "./March2021" # FIXME: don't hardcode path

        for root in cls.rootCandidates:
            absolutePath = "{0}/{1}".format(root, someRelativePath)
            if os.path.exists(absolutePath):
                return root

        return None

    @classmethod
    def addCyberduckPathsIfPresent(cls) -> bool:
        try:
            result = subprocess.run(['duck', '-h'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                match = re.match(r'Third.+in\s+(.+duck)/Profiles', line)
                if match is not None:
                    shortPath = match.group(1)
                    duckDir = os.path.expanduser(shortPath)
                    ziliaPath = ("{0}/Volumes/Zilia".format(duckDir))
                    if os.path.exists(ziliaPath):
                        ZiliaDB.rootCandidates.append(ziliaPath)
            return True
        except:
            return False # cyberduck not installed or available

    def __init__(self, ziliaDbPath=None, root=None):  
        """
        Creates the database object for the Zilia experiments.

        The path to the database can be obtained dynamically. The root directory is not mandatory: it simply means you will not be able to 
        read image files if it is None.

        """
        if ziliaDbPath is None:
            ziliaDbPath = ZiliaDB.findDatabasePath()
        if root is None:
            root = ZiliaDB.findDataFilesRoot()

        super().__init__(ziliaDbPath, writePermission=False)

        self.root = root
        self._wavelengths = None
        self.progressStart = None

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

    def getAcquisitionIdList(self):
        self.execute("select date as acquisitionId, m.monkeyId, timeline, rlp, region, content, eye from imagefiles as f left join monkeys as m on m.monkeyId = f.monkeyId group by acquisitionId order by acquisitionId")
        rows = self.fetchAll()
        paths = []
        for row in rows:
            paths.append(row['acquisitionId'])
        return rows

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

    def getRGBImages(self, monkey=None, timeline=None, rlp=None, region=None, content=None, eye=None, limit=None, mirrorLeftEye=True):
        images = self.getRGBImagesWithPaths(monkey=monkey, timeline=timeline, rlp=rlp, region=region, content=content, eye=eye, limit=limit, mirrorLeftEye=mirrorLeftEye)
        return images.values()

    def getRGBImagesWithPaths(self, monkey=None, timeline=None, rlp=None, region=None, content=None, eye=None, limit=None, mirrorLeftEye=True):
        if self.root is None:
            raise RuntimeError('To read image files, you must provide a root directory')

        stmnt = self.buildImageSelectStatement(monkey=monkey, timeline=timeline, rlp=rlp, region=region, content=content, eye=eye, limit=limit)
        self.execute(stmnt)
        rows = self.fetchAll()

        images = {}
        nTotal = len(rows)
        for i,row in enumerate(rows):
            relativePath = row['path']
            absolutePath = "{0}/{1}".format(self.root, relativePath)
            if not os.path.exists(absolutePath):
                raise FileNotFoundError(absolutePath)

            image = imread(absolutePath)
            if row['eye'] == 'os' and mirrorLeftEye:
                image = self.mirrorImageHorizontally(image) 
            images[relativePath] = image
            self.showProgressBar(i+1, nTotal)

        return images

    def mirrorImageHorizontally(self, image):
        return image[:,::-1,:]

    def getGrayscaleEyeImages(self, monkey=None, timeline=None, rlp=None, region=None, eye=None, limit=None, mirrorLeftEye=True):
        images = self.getGrayscaleEyeImagesWithPaths(monkey=monkey, timeline=timeline, rlp=rlp, region=region, eye=eye, limit=limit, mirrorLeftEye=mirrorLeftEye)
        return images.values()

    def getGrayscaleEyeImagesWithPaths(self, monkey=None, timeline=None, rlp=None, region=None, eye=None, limit=None, mirrorLeftEye=True):
        images = self.getRGBImagesWithPaths(monkey=monkey, timeline=timeline, rlp=rlp, region=region, content='eye', eye=eye, limit=limit, mirrorLeftEye=mirrorLeftEye)

        grayscaleImages = {}
        for key, image in images.items():
            image[:,:,2] = 0 # For eye images, always strip blue channel before conversion
            grayscaleImages[key] = rgb2gray(image)

        return grayscaleImages

    def getCalculatedImageProperties(self, monkey=None, timeline=None, rlp=None, region=None, content=None, eye=None, limit=None):

        stmnt = self.buildImageSelectStatement(monkey=monkey, timeline=timeline, rlp=rlp, region=region, content=content, eye=eye, limit=limit)
        self.execute(stmnt)
        rows = self.fetchAll()

        records = []
        nTotal = len(rows)
        for i,row in enumerate(rows):
            record = {}

            for property in row.keys():
                record[property] = row[property]

            if row['properties'] is not None: # We may have records without any calculations
                properties = row['properties'].split(',')
                values = row['floatValues'].split(',')

                for property, value in zip(properties, values):
                    record[property] = value

            records.append(record)
            self.showProgressBar(i+1, nTotal)

        return records

    def buildImageSelectStatement(self, monkey=None, timeline=None, rlp=None, region=None, content=None, eye=None, limit=None):
        stmnt = r"""select f.*, m.*, group_concat(c.property) as properties, group_concat(c.value) as floatValues, group_concat(c.stringValue) as stringValues
        from imagefiles as f left join monkeys as m on m.monkeyId = f.monkeyId left join calculations as c on c.path = f.path where 1 = 1 """

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
            
        if eye is not None:
            stmnt += " and f.eye like '%{0}%'".format(eye)

        stmnt += " group by f.path"
        stmnt += " order by f.path"

        if limit is not None:
            stmnt += " limit {0}".format(limit)

        return stmnt

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

    def showProgressBar(self, iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
        """
        From: https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console

        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
            printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        """

        if self.progressStart is None:
            self.progressStart = time.time()

        if time.time() > self.progressStart + 3:
            percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
            filledLength = int(length * iteration // total)
            bar = fill * filledLength + '-' * (length - filledLength)
            print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)

            if iteration == total: 
                print()
        
        if iteration == total: 
            self.progressStart = None

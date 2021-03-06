
# Routines used for building cubes
import logging
from . import cube_build_io_util
from . import file_table
from . import instrument_defaults


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class CubeData():
# CubeData - holds all the important information for IFU Cube Building:
# wcs, data, reference data

    def __init__(self,
                 input_models,
                 input_filenames,
                 par_filename,
                 resol_filename,
                 **pars):

        self.input_models = input_models
        self.input_filenames = input_filenames
        self.par_filename = par_filename
        self.resol_filename = resol_filename
        self.single = pars.get('single')
        self.channel = pars.get('channel')
        self.subchannel = pars.get('subchannel')
        self.grating = pars.get('grating')
        self.filter = pars.get('filter')
        self.weighting = pars.get('weighting')
        self.output_type = pars.get('output_type')
        self.detector = None
        self.instrument = None

        self.all_channel = []
        self.all_subchannel = []
        self.all_grating = []
        self.all_filter = []

        self.output_name = ''
#********************************************************************************
    def setup(self):

        """
        Short Summary
        -------------
        Set up overall structure of the cubes to be created
        Read in the input_models and fill in the dictionary master_table that stores
        the files for each channel/subchannel or grating/filter

        if the channel/subchannel or grating/filter is not set then determine which
        ones are found in the data

        Read in necessary reference data:
        * cube parameter reference file
        * if miripsf weighting paramter is set then read in resolution file

        Parameters
        ----------
        instrument_info holds the defaults roi sizes  for each channel/subchannel (MIRI)
        or grating (NIRSPEC)

        Returns
        -------
        self with necessary files filled in
        """

#________________________________________________________________________________
# Read in the input data (association table or single file)
# Fill in MasterTable   based on Channel/Subchannel  or filter/grating
#________________________________________________________________________________
        master_table = file_table.FileTable()
        instrument, detector = master_table.set_file_table(self.input_models,
                                                           self.input_filenames)
#________________________________________________________________________________
# find out how many files are in the association table or if it is an single file
# store the input_filenames and input_models

#        num = len(self.input_filenames)
        self.detector = detector
        self.instrument = instrument
#________________________________________________________________________________
    # Determine which channels/subchannels or filter/grating cubes will be
    # constructed from.
    # fills in band_channel, band_subchannel, band_grating, band_filer
#________________________________________________________________________________
        self.determine_band_coverage(master_table)
#________________________________________________________________________________
# InstrumentDefaults is an  dictionary that holds default parameters for
# difference instruments and for each band
#________________________________________________________________________________
        instrument_info = instrument_defaults.InstrumentInfo()
#--------------------------------------------------------------------------------
        # Load the parameter ref file data model
        # fill in the appropriate fields in InstrumentInfo
        # with the cube parameters
        log.info('Reading  cube parameter file %s', self.par_filename)
        cube_build_io_util.read_cubepars(self.par_filename,
                                         self.instrument,
                                         self.all_channel,
                                         self.all_subchannel,
                                         self.all_grating,
                                         self.all_filter,
                                         instrument_info)
#--------------------------------------------------------------------------------
        # Load the miri resolution ref file data model -
        # fill in the appropriate fields in instrument_info
        # with the cube parameters
        if(self.weighting == 'miripsf'):
            log.info('Reading default MIRI cube resolution file %s', self.resol_filename)
            cube_build_io_util.read_resolution_file(self.resol_filename,
                                                    self.channel,
                                                    self.all_channel,
                                                    self.all_subchannel,
                                                    instrument_info)
#________________________________________________________________________________
        self.instrument_info = instrument_info
#________________________________________________________________________________
# Set up values to return and acess for other parts of cube_build

        self.master_table = master_table

        return {'instrument': self.instrument,
                'detector': self.detector,
                'instrument_info': self.instrument_info,
                'master_table': self.master_table}

#********************************************************************************
    def determine_band_coverage(self, master_table):
#********************************************************************************
        """
        Short Summary
        -------------
        Function to determine which files contain channels and subchannels are used
        in the creation of the cubes.
        For MIRI The channels  to be used are set by the association and the
        subchannels are  determined from the data

        Parameter
        ----------
        self containing user set input parameters:
        self.channel, self.subchannel

        Returns
        -------
        fills in self.band_channel, self.band_subchannel
        self.band_grating, self.band_filter

        """
#________________________________________________________________________________
# IF INSTRUMENT = MIRI
# loop over the file names

        if self.instrument == 'MIRI':
            valid_channel = ['1', '2', '3', '4']
            valid_subchannel = ['short', 'medium', 'long']

            nchannels = len(valid_channel)
            nsubchannels = len(valid_subchannel)
#________________________________________________________________________________
        # for MIRI we can set the channel and subchannel
            user_clen = len(self.channel)
            user_slen = len(self.subchannel)
#________________________________________________________________________________
            for i in range(nchannels):
                for j in range(nsubchannels):
                    nfiles = len(master_table.FileMap['MIRI'][valid_channel[i]][valid_subchannel[j]])
                    if nfiles > 0:
#________________________________________________________________________________
        # neither parameters not set
                        if user_clen == 0 and user_slen == 0:
                            self.all_channel.append(valid_channel[i])
                            self.all_subchannel.append(valid_subchannel[j])
#________________________________________________________________________________
# channel was set by user but not sub-channel
                        elif user_clen != 0 and user_slen == 0:
                        # now check if this channel was set by user
                            if (valid_channel[i] in self.channel):
                                self.all_channel.append(valid_channel[i])
                                self.all_subchannel.append(valid_subchannel[j])
#________________________________________________________________________________
# sub-channel was set by user but not channel
                        elif user_clen == 0 and user_slen != 0:
                            if (valid_subchannel[j] in self.subchannel):
                                self.all_channel.append(valid_channel[i])
                                self.all_subchannel.append(valid_subchannel[j])
#________________________________________________________________________________
# both parameters set
                        else:
                            if (valid_channel[i] in self.channel and
                                valid_subchannel[j] in self.subchannel):

                                self.all_channel.append(valid_channel[i])
                                self.all_subchannel.append(valid_subchannel[j])

            log.info('The desired cubes covers the MIRI Channels: %s',
                     self.all_channel)
            log.info('The desired cubes covers the MIRI subchannels: %s',
                     self.all_subchannel)

            number_channels = len(self.all_channel)
            number_subchannels = len(self.all_subchannel)

            if number_channels == 0:
                raise ErrorNoChannels(
                    "The cube  does not cover any channels, change channel parameter")
            if number_subchannels == 0:
                raise ErrorNoSubchannels(
                    "The cube does not cover any subchannels, change band parameter")

#______________________________________________________________________
        if self.instrument == 'NIRSPEC':
        # 1 to 1 mapping valid_gwa[i] -> valid_fwa[i]
            valid_gwa = ['g140m', 'g140h', 'g140m', 'g140h', 'g235m', 'g235h',
                        'g395m', 'g395h', 'prism']
            valid_fwa = ['f070lp', 'f070lp', 'f100lp', 'f100lp', 'f170lp',
                        'f170lp', 'f290lp', 'f290lp', 'clear']

            nbands = len(valid_fwa)
#________________________________________________________________________________
        # check if input filter or grating has been set
            user_glen = len(self.grating)
            user_flen = len(self.filter)

            if user_glen == 0 and user_flen != 0:
                raise ErrorMissingParameter("Filter specified, but Grating was not")

            if user_glen != 0 and user_flen == 0:
                raise ErrorMissingParameter("Grating specified, but Filter was not")
        # Grating and Filter not set - read in from files and create a list of all
        # the filters and grating contained in the files
            if user_glen == 0 and user_flen == 0:
                for i in range(nbands):

                    nfiles = len(master_table.FileMap['NIRSPEC'][valid_gwa[i]][valid_fwa[i]])
                    if nfiles > 0:
                        self.all_grating.append(valid_gwa[i])
                        self.all_filter.append(valid_fwa[i])

        # Both filter and grating input parameter have been set
        # Find the files that have these parameters set

            else:
                for i in range(nbands):
                    nfiles = len(master_table.FileMap['NIRSPEC'][valid_gwa[i]][valid_fwa[i]])
                    if nfiles > 0:
                        # now check if THESE Filter and Grating input parameters were set
                        if (valid_fwa[i] in self.filter and
                            valid_gwa[i] in self.grating):
                            self.all_grating.append(valid_gwa[i])
                            self.all_filter.append(valid_fwa[i])

            number_filters = len(self.all_filter)
            number_gratings = len(self.all_grating)

            if number_filters == 0:
                raise ErrorNoFilters("The cube does not cover any filters")
            if number_gratings == 0:
                raise ErrorNoGratings("The cube does not cover any gratings")

#______________________________________________________________________


    def number_cubes(self):

        """
        Short Summary
        -------------
        Determine the number of IFUcubes to created based on:
        Type of cube (single band, multiple bands, or Single mode)

        # check which type of cubes to create: A user selected one, single, or default set
        """
        num_cubes = 0
        cube_pars = {}
#______________________________________________________________________
# MIRI
#______________________________________________________________________
        if self.instrument == 'MIRI':
            band_channel = self.all_channel
            band_subchannel = self.all_subchannel

#user and single
            if (self.output_type == 'user' or self.output_type == 'single' or
                self.output_type == 'multi'):

                if self.output_type == 'multi':
                    log.info('Output IFUcube are constructed from all the data ')
                if self.single:
                    log.info(' Single = true, creating a set of single exposures mapped' +
                          ' to output IFUCube coordinate system')
                if self.output_type == 'user':
                    log.info(' The user has selected the type of IFU cube to make')

                num_cubes = 1
                cube_pars['1'] = {}
                cube_pars['1']['par1'] = {}
                cube_pars['1']['par2'] = {}
                cube_pars['1']['par1'] = self.all_channel
                cube_pars['1']['par2'] = self.all_subchannel

# default band cubes
            if self.output_type == 'band':
                log.info('Output Cubes are single channel, single sub-channel IFU Cubes')
                for i in range(len(band_channel)):
                    num_cubes = num_cubes + 1
                    cube_no = str(num_cubes)
                    cube_pars[cube_no] = {}
                    cube_pars[cube_no]['pars1'] = {}
                    cube_pars[cube_no]['pars2'] = {}
                    this_channel = []
                    this_subchannel = []
                    this_channel.append(band_channel[i])
                    this_subchannel.append(band_subchannel[i])
                    cube_pars[cube_no]['par1'] = this_channel
                    cube_pars[cube_no]['par2'] = this_subchannel

# default channel cubes
            if self.output_type == 'channel':
                log.info('Output cubes are single channel and all subchannels in data')
                num_cubes = 0
                channel_no_repeat = list(set(band_channel))
                for i in range(len(channel_no_repeat)):
                        num_cubes = num_cubes + 1
                        cube_no = str(num_cubes)
                        cube_pars[cube_no] = {}
                        cube_pars[cube_no]['pars1'] = {}
                        cube_pars[cube_no]['pars2'] = {}
                        this_channel = []
                        for j in range(band_channel):
                            if j == i:
                                this_subchannel = band_subchannel[j]
                        this_channel.append(i)
                        cube_pars[cube_no]['par1'] = this_channel
                        cube_pars[cube_no]['par2'] = this_subchannel
#______________________________________________________________________
# NIRSPEC
#______________________________________________________________________
        if self.instrument == 'NIRSPEC':

            band_grating = list(set(self.all_grating))
            band_filter = list(set(self.all_filter))
            if (self.output_type == 'user' or self.output_type == 'single' or
                self.output_type == 'multi'):
                if self.output_type == 'multi':
                    log.info('Output IFUcube are constructed from all the data ')
                if self.single:
                    log.info(' Single = true, creating a set of single exposures mapped' +
                          ' to output IFUCube coordinate system')
                if self.output_type == 'user':
                    log.info(' The user has selected the type of IFU cube to make')

                num_cubes = 1
                cube_pars['1'] = {}
                cube_pars['1']['par1'] = {}
                cube_pars['1']['par2'] = {}
                cube_pars['1']['par1'] = self.all_grating
                cube_pars['1']['par2'] = self.all_filter

# default band cubes
            if self.output_type == 'band':
                log.info('Output Cubes are single grating, single filter IFU Cubes')
                for i in range(len(band_grating)):
                    for j in range(len(band_filter)):
                        num_cubes = num_cubes + 1
                        cube_no = str(num_cubes)
                        cube_pars[cube_no] = {}
                        cube_pars[cube_no]['pars1'] = {}
                        cube_pars[cube_no]['pars2'] = {}
                        this_grating = []
                        this_filter = []
                        this_grating.append(band_grating[i])
                        this_filter.append(band_filter[j])
                        cube_pars[cube_no]['par1'] = this_grating
                        cube_pars[cube_no]['par2'] = this_filter
# default grating cubes
            if self.output_type == 'grating':
                log.info('Output cubes are single grating and all filters in data')
                num_cubes = 0
                for i in range(len(band_grating)):
                        num_cubes = num_cubes + 1
                        cube_no = str(num_cubes)
                        cube_pars[cube_no] = {}
                        cube_pars[cube_no]['pars1'] = {}
                        cube_pars[cube_no]['pars2'] = {}
                        this_grating = []
                        this_filter = band_subchannel
                        this_grating.append(i)
                        cube_pars[cube_no]['par1'] = this_grating
                        cube_pars[cube_no]['par2'] = this_filter


        self.num_cubes = num_cubes
        self.cube_pars = cube_pars
        return self.num_cubes, self.cube_pars
#********************************************************************************

class ErrorMissingParameter(Exception):
    pass

class ErrorNoChannels(Exception):
    pass

class ErrorNoSubchannels(Exception):
    pass

class ErrorNoFilters(Exception):
    pass

class ErrorNoGratings(Exception):
    pass

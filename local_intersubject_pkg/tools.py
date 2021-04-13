# tools.py: A module containing useful non-statistical functions
#  

import os
import glob
import json
import configparser

import numpy as np
import nibabel as nib

# =============================
# Basic data handling functions
# =============================

# NOTE: this may require me to explicitly define cwd through os module on Oak/Sherlock
# Make directories, with error exception
def create_directory(dir_):
    """
    Creates directory if it doesn't exist already and prints directory
    creation errors to the console.
    """

    # TODO: replace print statements with logging
    # Make these directories; print results or errors
    if os.path.exists(dir_) == False:
        print(f'> Path: {dir_}\n...could not be found.\n> Attempting to create directory...\n')
        try:
            os.makedirs(dir_)
            print(f'> Path: {dir_}\n...successfully created.\n')
        except:
            print(f'> Failed to create path: {dir_}\n')
    else:
        print(f'> Path: {dir_}\n...already exists.\n')


# TODO: add logging to this function
def save_data(dir_, *args, **kwargs):
    """
    Uses numpy's save(), savez() or savez_compressed(), 
    but double-checks if directory exists too
    """
    # assert os.path.exists(dir_), f"Path {dir_} does not exists."

    try:
        if dir_.endswith('.npy'):
            np.save(dir_, *args)

        elif dir_.endswith('.npz'):
            np.savez(dir_, **kwargs)

        # Log success here
        assert os.path.exists(dir_), "Path did not work"
        print(dir_ + ' successfully created.\n')
    except:
        # Log failure here
        print(dir_ + ' failed to create.\n')



def get_files_dict(path, id_list):
    
    id_file_dict = {}
    for id_ in id_list:
        for file in glob.iglob(path.format(id_), recursive=True):
            id_file_dict[id_] = file
    return id_file_dict

def prep_data(files_dict, output_path, cutoff_column=None, cutoff_mean=None):
    
    for id_ in files_dict:
        id_path = files_dict[id_]

        try:
            # checks for numpy.npy file 
            if id_path.endswith(".npy"):
                data = np.load(id_path)
                
            # checks for NiFti /*.nii.gz file 
            elif id_path.endswith(".gz"):
                data = nib.load(files_dict[id_path]).get_fdata()[:,:,:, 0: cutoff_column]
        except:
            print("Unrecognized file type.")
            break

        datasize = np.array(data.shape)

        # reshape 4d array to matrix
        # Note: rows=voxels, columns=TRs
        data = data.reshape((datasize[0] * datasize[1] * datasize[2]),
                            datasize[3]).astype(np.float32)
        
        # create boolean mask based on each voxel's mean
        mask = np.mean(data, axis=1) > cutoff_mean
        
        # filter voxels using mask
        data = data[mask, :]
        
        # save filtered data to numpy.npz file
        save_data(output_path.format(id_), data=data, mask=mask)

def create_fake_data(output_path, datasize=(4, 4, 4, 10), no_of_subjects=None, id_list=None):
    """
    Create fake fmri data saved as numpy.npy files. Data is created
    using either a list of subject IDs or a number of 
    subjects.
    
    Note:
    - 
    - Default datasize is 4,4,4,10 or 64 voxels x 10 TRs
    """
    
    if id_list == None:
        # Use range to create ids
        subjects = [i*2+1 for i in range(no_of_subjects)]
    else:
        subjects = id_list
        
    # create fake data then save
    for i, sub in enumerate(subjects):
        seed = i + 500 # hacky way of getting random seed per loop
        np.random.seed(seed)
        fake_data = np.random.randint(1000, 5000, size=datasize)
        save_data(output_path.format(sub), fake_data)

def test_fake():
    cwd = os.getcwd()
    test_dir = cwd+'/data/inputs/test_data'
    create_directory(test_dir)

    test_data = np.array([[420, 69],[1234, 5]])

    file_fake = "/sub-{}.npy"
    file_filter = "/filter_sub-{}.npz"

    np.save(test_dir+file_fake.format(69), test_data)
    np.savez(test_dir+file_filter.format(69), data=test_data, mask='yuhhhh')

    save_data(test_dir+file_fake.format(70), test_data)
    save_data(test_dir+file_filter.format(70), dict(data=test_data, mask='yuhhhh'))

def run_test():
    cwd = os.getcwd()
    test_dir = cwd+'/data/inputs/test_data'
    file_fake = '/sub-{}.npy'
    file_filter = '/filter_sub-{}.npz'
    test_data = np.array([[420, 69],[1234, 5]])
    dict_ = dict(data=test_data, mask='yuh')

    def saver1(path, args):
        np.savez(path, **args)
    
    def saver2(path, **args):
        np.savez(path, **args)

    def saver3(path, *args, **kwargs):
        if path.endswith('.npy'):
            np.save(path, *args)

        elif path.endswith('.npz'):
            np.savez(path, **kwargs)


    saver1(test_dir+file_filter.format(71), dict_)
    saver2(test_dir+file_filter.format(72), data=test_data, mask='hmm')
    saver3(test_dir+file_fake.format(73), test_data)
    saver3(test_dir+file_filter.format(73), data=test_data, mask='horny')

    data1 = np.load(test_dir+file_filter.format(71))
    data2 = np.load(test_dir+file_filter.format(72))
    data3 = np.load(test_dir+file_fake.format(73))
    data4 = np.load(test_dir+file_filter.format(73))
    
    return data1, data2, data3, data4


def get_setting(in_or_out=None, which_input=None, which_fake=None, which_param=None):
    """
    Get details from the script settings file.
    """
    # Get datapaths
    settings_file = "script_settings.json"
    with open(settings_file) as file_:
        config = json.load(file_)

    # Check for parameter request
    if which_param == 'datasize':
        output = config['Parameters']['datasize']

    #  Check for filepath request
    try:
        if in_or_out == 'input':

            # Check for real data
            if which_input == 'npy':
                output = config['Paths']['npy_path']
            elif which_input == 'nifti':
                output = config['Paths']['nifti_path']

            # Check for 
            elif which_fake == 'range_ids':
                output = config['Fake Data Paths']['filter_range']
            elif which_fake == 'real_ids':
                output = config['Fake Data Paths']['filter_real']
        
        elif in_or_out == 'output':
            output = config['Paths']['data_outputs']

        # Double check that directory exists
        assert os.path.exists(output), f"The path...\n{data_path}\n...could not be found or does not exist."
    
    except:
        print(f" :(   ...could not retrieve details from settings file {settings_file}...   :(")

    # Return result
    return output
from PyInstaller.utils.hooks import collect_data_files, copy_metadata
hiddenimports = [
    'cython',
    'sklearn',
    'sklearn.neighbors.typedefs'
]
datas = collect_data_files('resampy')

import io
import tarfile
import warnings
import numpy as np

def write_np_array_to_tar(array: np.ndarray, arrayname: str, tarpath: str):
    abuf = io.BytesIO()
    np.save(abuf, array)
    abuf.seek(0)

    tar=tarfile.open(tarpath,'a')
    if arrayname in tar.getnames():
        tar.close()
        warnings.warn(f"File {arrayname} already present in tar {tarpath}. Skipping.", RuntimeWarning)
        return
    info= tarfile.TarInfo(name=arrayname)
    info.size=len(abuf.getbuffer())
    tar.addfile(tarinfo=info, fileobj=abuf)
    tar.close()


def write_str_to_tar(str_to_write: str, filename: str, tarpath: str):
    
    data = str_to_write.encode('utf8')
    info = tarfile.TarInfo(name=filename)
    info.size = len(data)


    tar=tarfile.open(tarpath,'a')
    if filename in tar.getnames():
        tar.close()
        warnings.warn(f"File {filename} already present in tar {tarpath}. Skipping.", RuntimeWarning)
        return
    info= tarfile.TarInfo(name=filename)
    info.size=len(str_to_write)
    tar.addfile(tarinfo=info, fileobj=io.BytesIO(data))
    tar.close()


def read_seeds_from_tar(filename: str, tarpath: str):
    with tarfile.open(tarpath) as f:
        bytes = f.extractfile(filename).read()
        bytes_io = io.BytesIO(bytes)
        X = np.loadtxt(bytes_io, dtype=int)
        return X
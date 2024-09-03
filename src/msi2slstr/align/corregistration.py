from arosics import COREG_LOCAL

from ..data.gdalutils import create_mem_dataset, TermProgress
from ..data.typing import Sentinel2L1C, Sentinel3RBT


def corregister_datasets(sen2: Sentinel2L1C, sen3: Sentinel3RBT) -> None:
    """
    Run arosics local corregistration.
    """
    CRL = COREG_LOCAL(sen2.dataset.GetDescription(),
                      sen3.dataset.GetDescription(),
                      2.,
                      window_size=(64, 64),
                      path_out=None,
                      fmt_out="VRT",
                      nodata=(0, -32768),
                      r_b4match=9,
                      s_b4match=3,
                      min_reliability=10)
    CRL.correct_shifts(cliptoextent=True)
    proj = CRL.deshift_results.get("updated projection")
    geot = CRL.deshift_results.get("updated geotransform")
    data = CRL.deshift_results.get("arr_shifted")
    
    dataset = create_mem_dataset(*data.shape,
                                 proj=proj,
                                 geotransform=geot)
    dataset.WriteArray(data.swapaxes(-1, 0),
                       band_list=range(1, 1 + data.shape[-1]),
                       callback=TermProgress)
    del data, proj, geot
    
    sen3.dataset = dataset
    sen3.dataset.FlushCache()
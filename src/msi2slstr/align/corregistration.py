from arosics import COREG_LOCAL

from ..data.gdalutils import create_mem_dataset, TermProgress
from ..data.typing import Sentinel2L1C, Sentinel3SLSTR


def corregister_datasets(sen2: Sentinel2L1C, sen3: Sentinel3SLSTR) -> None:
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
                      min_reliability=10,
                      resamp_alg_calc=0,
                      resamp_alg_deshift=0)
    CRL.correct_shifts(cliptoextent=True)
    dataset = create_mem_dataset(*CRL
                                 .deshift_results
                                 .get("arr_shifted")
                                 .shape,
                                 proj=CRL
                                 .deshift_results
                                 .get("updated projection"),
                                 geotransform=CRL
                                 .deshift_results
                                 .get("updated geotransform"))

    # From H, W, C -> Swap W<->C -> Swap W<->H -> Expected shape C, H, W.
    dataset.WriteArray(data.swapaxes(-1, 0).swapaxes(-1, -2),
                       band_list=range(1, 1 + data.shape[-1]),
                       callback=TermProgress)
    del data, proj, geot

    sen3.dataset = dataset
    sen3.dataset.FlushCache()

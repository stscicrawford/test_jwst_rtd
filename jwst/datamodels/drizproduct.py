from . import model_base


__all__ = ['DrizProductModel']


class DrizProductModel(model_base.DataModel):
    """
    A data model for drizzle-generated products.
    """
    schema_url = "drizproduct.schema.yaml"

    def __init__(self, init=None, data=None, con=None, wht=None, hdrtab=None,
                    relsens=None, **kwargs):
        super(DrizProductModel, self).__init__(init=init, **kwargs)

        if data is not None:
            self.data = data

        if con is not None:
            self.con = con

        if wht is not None:
            self.wht = wht

        if hdrtab is not None:
            self.hdrtab = hdrtab

        if relsens is not None:
            self.relsens = relsens

    @property
    def hdrtab(self):
        return self._extra_fits.HDRTAB.data

    @hdrtab.setter
    def hdrtab(self, v):
        self._extra_fits.HDRTAB.data = v

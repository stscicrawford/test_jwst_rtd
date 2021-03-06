from .reference import ReferenceFileModel

__all__ = ['OutlierParsModel']


class OutlierParsModel(ReferenceFileModel):
    """
    A data model for outlier detection parameters reference tables.
    """
    schema_url = "outlierpars.schema.yaml"

    def __init__(self, init=None, outlierpars_table=None, **kwargs):
        super(OutlierParsModel, self).__init__(init=init, **kwargs)

        if outlierpars_table is not None:
            self.outlierpars_table = outlierpars_table

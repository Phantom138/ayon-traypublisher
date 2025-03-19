import re

import pyblish.api
from ayon_core.lib import BoolDef
from ayon_core.pipeline import publish

UDIM_REGEX = re.compile(r"(.*)[._](?P<udim>\d{4})\.(.*)")


class CollectUDIMs(pyblish.api.InstancePlugin, publish.AYONPyblishPluginMixin):
    """Collect UDIMs tiles."""

    label = "Collect Textures"
    order = pyblish.api.CollectorOrder - 0.499
    families = ["textures"]
    hosts = ["traypublisher"]

    def process(self, instance):
        # instance_settings = self.get_attr_values_from_data(instance.data)
        # is_udim = instance_settings.get("isUDIM", False)
        # if not is_udim:
        #     return
        representation = instance.data["creator_attributes"]["representation_files"][0]
        ext = representation["ext"]
        instance.data["representations"] = [
            {
                "name": representation["ext"],
                "ext": representation["ext"],
                "files": representation["filenames"],
                "udim": representation["udim"],
                "stagingDir": representation["directory"]
            }
        ]
        self.log.debug(f"Created Textures Instance: {instance.data}")
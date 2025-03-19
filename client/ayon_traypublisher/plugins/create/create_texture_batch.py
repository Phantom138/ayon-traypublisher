import copy
import os
import clique
from typing import Optional

from ayon_core.lib import (
    FileDef,
    BoolDef,
)
from ayon_core.pipeline import (
    CreatedInstance,
)

from ayon_traypublisher.api.plugin import TrayPublishCreator
import re

class TextureSetBatchCreator(TrayPublishCreator):
    """Creates instances from texture sets.
    Intended for full texture sets for an asset.
    """
    identifier = "texture_set_batch"
    label = "Texture Set"
    product_type = "texture"
    description = "Publish batch of textures"

    # Position batch creator after simple creators
    order = 110

    extensions = {"png", "jpg", "jpeg", "tiff", "tif", "exr"}

    match_patterns = {
        'BaseColor': re.compile("(_|-|\.)BaseColor|Albedo|Diffuse|color|Base|albd|a\.",flags=re.I),
        'Metalness': re.compile("(_|-|\.)metal|M\.",flags=re.I),
        'Normal': re.compile("(_|-|\.)norm|N\.",flags=re.I),
        'Roughness': re.compile("(_|-|\.)rough|R\.",flags=re.I),
        'Displacement': re.compile("(_|-|\.)disp|DM\.",flags=re.I)
    }

    def get_icon(self):
        return "fa.file"

    def create(self, product_name, data, pre_create_data):
        file_paths = pre_create_data.get("filepath")
        if not file_paths:
            return

        folder_path: str = data["folderPath"]
        task_name: Optional[str] = data.get("taskName")
        variant = data["variant"]
        project_name = self.create_context.get_current_project_name()
        folder_entity = self.create_context.get_folder_entity(folder_path)
        task_entity = self.create_context.get_task_entity(folder_path,
                                                          task_name)
        # Process the filepaths to individual instances
        for file_info in file_paths:
            instance_data = copy.deepcopy(data)
            instance_data["families"] = ["textures"]
            instance_data["productGroup"] = "texture" + variant

            filenames = file_info["filenames"]
            collections, remainder = clique.assemble(filenames)
            if collections:
                assert len(collections) == 1
                basename = collections[0].format("{head}").rstrip("._")
                udims = sorted(collections[0].indexes)
            else:
                assert len(remainder) == 1
                basename = os.path.splitext(remainder[0])[0]
                udims = [1001] # TODO add support for single files

            # TODO: Improve parsing of names
            # TODO: Detect images of single UDIM tile so that it does not
            #   include the UDIM tile number in the variant name
            # TODO: Pass on the files!

            repr_file = {
                "directory": file_info["directory"],
                "filenames": filenames,
                "udim": [str(item) for item in udims],
                "ext": os.path.splitext(filenames[0])[1][1:]
            }
            instance_data["creator_attributes"] = {}
            instance_data["creator_attributes"]["representation_files"] = [repr_file]

            # Variant is based on the match with the patterns.
            instance_variant = basename
            for tex_type, pattern in self.match_patterns.items():
                if re.search(pattern, basename):
                    instance_variant = variant + '.' + tex_type
                    break
            
            instance_data["variant"] = instance_variant
            product_name = self.get_product_name(
                project_name,
                folder_entity,
                task_entity,
                instance_variant,
            )

            # Create new instance
            new_instance = CreatedInstance("image", product_name, instance_data, self)
            # raise KeyError(vars(new_instance))
            self._store_new_instance(new_instance)

    def get_instance_attr_defs(self):
        return [
            BoolDef(
                "add_review_family",
                default=False,
                label="Review"
            )
        ]

    def get_pre_create_attr_defs(self):
        # Use same attributes as for instance attributes
        return [
            FileDef(
                "filepath",
                folders=False,
                single_item=False,
                extensions=self.extensions,
                allow_sequences=True,
                label="Filepath"
            ),
            
            BoolDef(
                "add_review_family",
                default=True,
                label="Review"
            )
        ]

    def get_detail_description(self):
        return """# Publish batch of textures for an asset
        It can be any amount of textures for the asset. The texture filename
        will be used to define the "Variant" name.
        """
import os
import shutil
from collections import defaultdict

import supervisely as sly
from dataset_tools.convert import unpack_if_archive
from supervisely.io.fs import (
    file_exists,
    get_file_ext,
    get_file_name,
    get_file_name_with_ext,
)
from supervisely.io.json import load_json_file
from tqdm import tqdm

import src.settings as s


def convert_and_upload_supervisely_project(
    api: sly.Api, workspace_id: int, project_name: str
) -> sly.ProjectInfo:
    # Possible structure for bbox case. Feel free to modify as you needs.

    train_images_path = "/home/alex/DATASETS/TODO/Nevada Smoke/archive/train_images"
    val_images_path = "/home/alex/DATASETS/TODO/Nevada Smoke/archive/val_images"
    batch_size = 30
    ann_train_path = "/home/alex/DATASETS/TODO/Nevada Smoke/archive/annotation_train.json"
    ann_val_path = "/home/alex/DATASETS/TODO/Nevada Smoke/archive/annotation_val.json"

    ds_name_to_data = {
        "train": (train_images_path, ann_train_path),
        "val": (val_images_path, ann_val_path),
    }

    def create_ann(image_path):
        labels = []
        tags = []

        image_name = get_file_name_with_ext(image_path)
        shape = image_name_to_shape.get(image_name)
        if shape is not None:
            img_height = shape[0]
            img_wight = shape[1]

        else:
            image_np = sly.imaging.image.read(image_path)[:, :, 0]
            img_height = image_np.shape[0]
            img_wight = image_np.shape[1]

        ann_data = image_name_to_ann_data[get_file_name_with_ext(image_path)]

        for curr_ann_data in ann_data:
            category_id = curr_ann_data[0]
            obj_class = idx_to_obj_class[category_id]

            bbox_coord = curr_ann_data[1]
            rectangle = sly.Rectangle(
                top=int(bbox_coord[1]),
                left=int(bbox_coord[0]),
                bottom=int(bbox_coord[1] + bbox_coord[3]),
                right=int(bbox_coord[0] + bbox_coord[2]),
            )
            label_rectangle = sly.Label(rectangle, obj_class)
            labels.append(label_rectangle)

        return sly.Annotation(img_size=(img_height, img_wight), labels=labels, img_tags=tags)

    project = api.project.create(workspace_id, project_name, change_name_if_conflict=True)

    idx_to_obj_class = {
        1: sly.ObjClass("low smoke", sly.Rectangle),
        3: sly.ObjClass("mid smoke", sly.Rectangle),
        5: sly.ObjClass("high smoke", sly.Rectangle),
    }

    meta = sly.ProjectMeta(obj_classes=list(idx_to_obj_class.values()))

    api.project.update_meta(project.id, meta.to_json())

    for ds_name, ds_data in ds_name_to_data.items():

        dataset = api.dataset.create(project.id, ds_name, change_name_if_conflict=True)

        images_path, ann_json_path = ds_data

        ann = load_json_file(ann_json_path)

        image_id_to_name = {}
        image_name_to_ann_data = defaultdict(list)
        image_name_to_shape = {}

        for curr_image_info in ann["images"]:
            image_id_to_name[curr_image_info["id"]] = curr_image_info["file_name"].split("/")[-1]
            image_name_to_shape[curr_image_info["file_name"].split("/")[-1]] = (
                curr_image_info["height"],
                curr_image_info["width"],
            )

        for curr_ann_data in ann["annotations"]:
            image_id = curr_ann_data["image_id"]
            image_name_to_ann_data[image_id_to_name[image_id]].append(
                [
                    curr_ann_data["category_id"],
                    curr_ann_data["bbox"],
                ]
            )

        images_names = [
            im_name for im_name in os.listdir(images_path) if get_file_ext(im_name) == ".jpg"
        ]

        progress = sly.Progress("Create dataset {}".format(ds_name), len(images_names))

        for images_names_batch in sly.batched(images_names, batch_size=batch_size):
            img_pathes_batch = [
                os.path.join(images_path, image_name) for image_name in images_names_batch
            ]

            img_infos = api.image.upload_paths(dataset.id, images_names_batch, img_pathes_batch)
            img_ids = [im_info.id for im_info in img_infos]

            anns = [create_ann(image_path) for image_path in img_pathes_batch]
            api.annotation.upload_anns(img_ids, anns)

            progress.iters_done_report(len(images_names_batch))

    return project

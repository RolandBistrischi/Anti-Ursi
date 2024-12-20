import argparse
import logging
import os
from pathlib import Path

from bearfacesegmentation.sam.segment_head import (
    run_with_bearid_xml,
    run_with_yolov8_labels,
)


def make_cli_parser() -> argparse.ArgumentParser:
    """Makes the CLI parser for running the download script.

    Hyperparameters can be passed for training.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--from-head-bbox-yolov8-labels",
        help="directory containing the bbox annotations.",
        required=False,
    )
    parser.add_argument(
        "--from-head-bbox-xml-filepath",
        help="xml filepath containing the annotations and dataset.",
        required=False,
    )
    parser.add_argument(
        "--from-body-masks",
        help="directory containing the bear body masks. Usually generated with SAM.",
    )
    parser.add_argument(
        "--bearid-base-path",
        help="BearID base path",
        default="./data/01_raw/BearID/",
    )
    parser.add_argument(
        "--to",
        help="directory to save the processed data. Make sure to use data/04_features.",
        required=True,
    )
    parser.add_argument(
        "-log",
        "--loglevel",
        default="warning",
        help="Provide logging level. Example --loglevel debug, default=warning",
    )
    return parser


def validate_parsed_args(args: dict) -> bool:
    """Returns whether the parsed args are valid."""
    if args["from_head_bbox_xml_filepath"] and not os.path.isfile(
        args["from_head_bbox_xml_filepath"]
    ):
        logging.error("invalid filepath --from-head-bbox-xml-filepath")
        return False
    if args["from_head_bbox_yolov8_labels"] and not os.path.isdir(
        args["from_head_bbox_yolov8_labels"]
    ):
        logging.error("invalid directory --from-head-bbox-yolov8-labels")
        return False
    elif not os.path.isdir(args["bearid_base_path"]):
        logging.error("invalid --bearid_base_path -- the folder does not exist")
        return False
    elif not os.path.isdir(args["from_body_masks"]):
        logging.error("invalid --from-body-masks -- the folder does not exist")
        return False
    else:
        return True


if __name__ == "__main__":
    cli_parser = make_cli_parser()
    args = vars(cli_parser.parse_args())
    logging.basicConfig(level=args["loglevel"].upper())
    if not validate_parsed_args(args):
        exit(1)
    else:
        print(args)
        if args["from_head_bbox_xml_filepath"]:
            run_with_bearid_xml(
                bearid_base_path=Path(args["bearid_base_path"]),
                label_path=Path(args["from_head_bbox_xml_filepath"]),
                masks_body_dir=Path(args["from_body_masks"]),
                output_dir=Path(args["to"]),
            )
            exit(0)
        elif args["from_head_bbox_yolov8_labels"]:
            run_with_yolov8_labels(
                label_path=Path(args["from_head_bbox_yolov8_labels"]),
                masks_body_dir=Path(args["from_body_masks"]),
                output_dir=Path(args["to"]),
            )
            exit(0)
        else:
            exit(1)

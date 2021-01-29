import os
import argparse
import logging
from glob import glob
from datetime import datetime
from PIL import Image, ImageChops, UnidentifiedImageError


def main():
    source_file_pattern, test_file_pattern, exclusion = parse_arguments()

    make_dir('diff')
    make_dir('logs')
    #clean_diffs()

    now = datetime.now()
    log_time = now.strftime("%Y%m%d%H%M%S")
    logging.basicConfig(filename=f'./logs/log_image_diff_{log_time}.log',
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    try:
        source_images = get_image_list(source_file_pattern, 'source')
        test_images = get_image_list(test_file_pattern, 'target')
    except AssertionError as e:
        print(e)
        logging.error(e)
        return

    if exclusion:
        source_images = exclude_images(source_images, exclusion)
        test_images = exclude_images(test_images, exclusion)

    print(f'{len(source_images)} benchmark image(s), {len(test_images)} target image(s).')
    logging.info(f'{len(source_images)} benchmark image(s), {len(test_images)} target image(s).')
    print()

    screens = zip(source_images, test_images)
    for source, target in screens:
        try:
            image_source = Image.open(source).convert('RGB')
            image_test = Image.open(target).convert('RGB')
        except UnidentifiedImageError:
            print(f"Cannot process image {source} or {target}")
            logging.error(f'Cannot process image {source} or {target}')
            continue

        diff = ImageChops.difference(image_source, image_test)
        if bool(diff.getbbox()):
            if os.path.basename(source) == os.path.basename(target):
                identifier = os.path.basename(source)
            else:
                identifier = os.path.basename(source)[:-4] + "_vs_" + os.path.basename(target)
            print(f'{target} DOES NOT match {source}')
            logging.warning(f'{target} DOES NOT match {source}')
            diff.save('diff/diff_' + identifier)


def get_image_list(file_pattern, purpose):
    images = glob(file_pattern)
    assert len(images) > 0, f"Could not find the {purpose} files. Use -h argument for help on how to " \
                                   f"point the script to {purpose} files. Exiting."
    images.sort()
    return images


def exclude_images(images, exclusion):
    images = [name for name in images if exclusion not in name]
    return images


def make_dir(folder, echo=True):
    if not os.path.exists(f"./{folder}"):
        os.makedirs(f"./{folder}")
        if echo:
            print(f"Created {folder} folder.")


def clean_diffs(echo=True):
    files = glob("./diff/*.*")
    for f in files:
        os.unlink(f)
    if len(files) > 0:
        if echo:
            print(f"Cleared diff folder. Deleted {len(files)} file(s).")


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('source',
                        nargs='?',
                        default='./source/*.*',
                        help="These files are the originals - they are correct. "
                             "Use wildcard format without quotation marks to indicate them. "
                             "For example, *.gif is all files with gif extension in the current "
                             "directory")
    parser.add_argument('target',
                        nargs='?',
                        default='./target/*.*',
                        help="These files are target images - we are not sure if they are correct. "
                             "Use wildcard format without quotation marks to indicate them. "
                             "For example, *.gif is all files with gif extension in the current "
                             "directory")
    parser.add_argument('-x', '--exclude', help="A string for what these files names SHOULD NOT contain. "
                                                "No wildcards here. For example, _nc.gif means that files like "
                                                "one_nc.gif will be ignored.")

    args = parser.parse_args()
    exclusion = args.exclude if args.exclude else ''

    return args.source, args.target, exclusion


if __name__ == "__main__":
    main()

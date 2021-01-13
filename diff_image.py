import os
import argparse
import logging
from glob import glob
from datetime import datetime
from PIL import Image, ImageChops, UnidentifiedImageError


def main():
    source_file_pattern, test_file_pattern, exclusion, log_deletion = parse_arguments()

    delete_logs(log_deletion)
    make_diff_dir()
    clean_diffs()

    now = datetime.now()
    log_time = now.strftime("%Y%m%d%H%M%S")
    logging.basicConfig(filename=f'log_image_diff_{log_time}.log',
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

    print(f'{len(source_images)} benchmark images, {len(test_images)} target images.')
    logging.info(f'{len(source_images)} benchmark images, {len(test_images)} target images.')

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
            identifier = os.path.basename(source)
            print(f'{target} DOES NOT match {source}')
            logging.warning(f'{target} DOES NOT match {source}')
            diff.save('diff/diff_' + identifier + '.gif')


def get_image_list(file_pattern, purpose):
    source_images = glob(file_pattern)
    assert len(source_images) > 0, f"Could not find the {purpose} files. Use -h argument for help on how to " \
                                   f"point the script to {purpose} files. Exiting."
    return source_images


def exclude_images(images, exclusion):
    images = [name for name in images if exclusion not in name]
    return images


def delete_logs(log_deletion, echo=True):
    if not log_deletion:
        return
    files = glob("./log_image_diff_*.log")
    for f in files:
        os.unlink(f)
    if len(files) and echo > 0:
        print(f"Deleted {len(files)} log file(s).")


def make_diff_dir(echo=True):
    if not os.path.exists("./diff"):
        os.makedirs("./diff")
        if echo:
            print("Created diff folder.")


def clean_diffs(echo=True):
    files = glob("./diff/*.*")
    for f in files:
        os.unlink(f)
    if len(files) > 0:
        if echo:
            print(f"Cleared diff folder. Deleted {len(files)} file(s).")


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', help="These files are the originals - they are correct. "
                                               "Use wildcard format without quotation marks to indicate them. "
                                               "For example, *.gif is all files with gif extension in the current "
                                               "directory")
    parser.add_argument('-t', '--target', help="These files are target images - we are not sure if they are correct. "
                                               "Use wildcard format without quotation marks to indicate them. "
                                               "For example, *.gif is all files with gif extension in the current "
                                               "directory")
    parser.add_argument('-x', '--exclude', help="A string for what these files names SHOULD NOT contain. "
                                                "No wildcards here. For example, _nc.gif means that files like "
                                                "one_nc.gif will be ignored.")
    parser.add_argument('-l', '--logdelete', help="Use this argument to delete previously generated log files.",
                        action="store_true")

    args = parser.parse_args()
    source_file_pattern = args.source if args.source else ".\\source\\*.*"
    target_file_pattern = args.target if args.target else ".\\target\\*.*"
    exclusion = args.exclude if args.exclude else ''

    return source_file_pattern, target_file_pattern, exclusion, args.logdelete


if __name__ == "__main__":
    main()

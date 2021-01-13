import unittest
import os
import make_diff_image


class TestImageDiff(unittest.TestCase):
    def setUp(self) -> None:
        self.files = ['one.gif', 'two.gif', 'three_nc.gif']
        self.files.sort()

    def test_exclude_images_with_exclusion(self):
        original = self.files
        exclude = 'nc.gif'
        result = make_diff_image.exclude_images(original, exclude)
        self.assertListEqual(result, ['one.gif', 'two.gif'])

    def test_exclude_images_no_exclusion(self):
        original = ['one.gif', 'two.gif', 'three.gif']
        exclude = 'nc.gif'
        result = make_diff_image.exclude_images(original, exclude)
        self.assertListEqual(result, original)

    def test_get_image_list(self):
        for name in self.files:
            with open(name, 'w') as f:
                f.write(f"name")

        result = make_diff_image.get_image_list('*.gif', 'source')

        self.assertListEqual(self.files, result)
        for name in self.files:
            if os.path.exists(name):
                os.unlink(name)

    def test_get_image_list_exception(self):
        for name in self.files:
            if os.path.exists(name):
                os.unlink(name)
        with self.assertRaises(AssertionError):
            make_diff_image.get_image_list('*.gif', 'source')

    def test_make_diff_dir_no_dir(self):
        was_no_dir = True
        if os.path.isdir("test"):
            was_no_dir = False
            os.rmdir("test")
        make_diff_image.make_dir('test', echo=False)

        self.assertTrue(os.path.isdir("test"))

        if was_no_dir:
            os.rmdir("test")

    def test_clean_diffs_with_files(self):
        was_no_dir = False
        if not os.path.exists("diff"):
            os.mkdir("diff")
            was_no_dir = True
        for name in self.files:
            with open(f"diff/{name}", 'w') as f:
                f.write(f"{name}")

        make_diff_image.clean_diffs(echo=False)
        for name in self.files:
            self.assertFalse(os.path.exists(f"diffs/{name}"))

        if was_no_dir:
            os.rmdir("diff")

    def test_delete_logs(self):
        logfiles = ["log_image_diff_one.log", "log_image_diff_two.log", "log_image_diff_three.log"]
        for name in logfiles:
            with open(name, 'w') as f:
                f.write(name)

        make_diff_image.delete_logs(True, echo=False)
        for name in self.files:
            self.assertFalse(os.path.exists(name))

    def tearDown(self) -> None:
        pass


if __name__ == '__main__':
    unittest.main()

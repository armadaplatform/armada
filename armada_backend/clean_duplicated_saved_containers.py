import filecmp
import glob
import os


def main():
    files = glob.glob('/opt/armada/saved_containers_backup/running_containers_parameters_????-??-??_??-??-??.json')
    previous = None
    for file in sorted(files):
        if previous is not None:
            equal = filecmp.cmp(previous, file)
            if equal:
                os.unlink(previous)
        previous = file


if __name__ == "__main__":
    main()

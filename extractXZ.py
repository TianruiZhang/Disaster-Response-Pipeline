import tarfile

if __name__ == "__main__":
    with tarfile.open("models.tar.xz") as infile:
        infile.extractall(".")
    print("All done!")

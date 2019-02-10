import shutil

if __name__ == "__main__":
    shutil.make_archive(
        base_dir="models",
        format="xztar",
        base_name="models"
        )
    print("All done!")

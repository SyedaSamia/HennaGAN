#code to remove duplicates from dataset

from collections import defaultdict
from PIL import Image
import argparse
import os
import hashlib
import imagehash

def getAverageHash(imgPath):
    try:
        return imagehash.average_hash(Image.open(imgPath))
    except:
        return None

def getDataset(image):
    """Get the images from the directory, partitioned by class."""
    exts = ["jpg", "png"]

    imageClasses = []  # Images, separated by class.
    for subdir, dirs, files in os.walk(image):
        images = []
        for fileName in files:
            # (imageClass, imageName) = (os.path.basename(subdir), fileName)
            imageName = fileName
            if any(imageName.lower().endswith("." + ext) for ext in exts):
                images.append(os.path.join(subdir, fileName))
        imageClasses.append(images)
    return imageClasses


def runOnClass(args, imgs):
    """Find and remove duplicates within an image class."""
    d = defaultdict(list)
    for imgPath in imgs:
        imgHash = getAverageHash(imgPath)
        if imgHash:
            d[imgHash].append(imgPath)

    numFound = 0
    for imgHash, imgs in d.items():
        if len(imgs) > 1:
            print("{}: {}".format(imgHash, " ".join(imgs)))
            numFound += len(imgs) - 1  # Keep a single image.

            if args.delete:
                largestImg = max(imgs, key=os.path.getsize)
                print("Keeping {}.".format(largestImg))
                imgs.remove(largestImg)
                for img in imgs:
                    os.remove(img)

            if args.sha256:
                print("")
                for img in imgs:
                    print(hashlib.sha256(open(img, 'rb').read()).hexdigest())
                print("")
    return numFound

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('inplaceDir', type=str,
                        help="Directory of images, divided into "
                        "subdirectories by class.")
    parser.add_argument('--delete', action='store_true',
                        help="Delete the smallest duplicate images instead "
                        "of just listing them.")
    parser.add_argument('--sha256', action='store_true',
                        help="Show sha256 sum for duplicate images")
    args = parser.parse_args()

    numFound = 0
    for imgClass in getDataset(args.inplaceDir):
        numFound += runOnClass(args, imgClass)
    print("\n\nFound {} total duplicate images.".format(numFound))
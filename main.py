import argparse

from utils import load_image, save_image
from remap import remap_pixels

def main ():
    parser = argparse.ArgumentParser(description="Remap pixels from one image onto another's structure")
    parser.add_argument("image1", help="Source image")
    parser.add_argument("image2", help="Template image")
    parser.add_argument("--output", "-o", default="output.png", help="Output file path (default: output.png)")

    args = parser.parse_args()

    source = load_image(args.image1)
    target= load_image(args.image2)

    result = remap_pixels(source, target)

    save_image(result, args.output)
    print(f"Saved to {args.output}")

if __name__ == "__main__":
    main()


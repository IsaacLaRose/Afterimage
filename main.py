import argparse
import os

from utils import load_image, save_image
from remap import remap_pixels


def main():
    parser = argparse.ArgumentParser(
        description="Remap the pixels of one image onto the structure of another."
    )
    parser.add_argument("image1", help="Source image — provides the pixels")
    parser.add_argument("image2", help="Template image — provides the structure")
    parser.add_argument(
        "-o", "--output",
        default="output.png",
        help="Output file path (default: output.png)"
    )
    parser.add_argument(
        "-m", "--mode",
        choices=["travel", "band"],
        default="travel",
        help="Animation mode: travel or band (default: travel)"
    )
    args = parser.parse_args()

    with open(args.image1, "rb") as f:
        source = load_image(f)
    with open(args.image2, "rb") as f:
        target = load_image(f)

    result, frames = remap_pixels(source, target, args.mode)

    save_image(result, args.output)

    gif_path = os.path.splitext(args.output)[0] + ".gif"
    frames[0].save(
        gif_path,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0,
    )

    print(f"Saved final frame to {args.output}")
    print(f"Saved animation to {gif_path}")


if __name__ == "__main__":
    main()
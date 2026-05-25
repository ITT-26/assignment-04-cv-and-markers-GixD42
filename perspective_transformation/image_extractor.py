import cv2
import argparse

WINDOW_NAME = "Image Extractor"
cv2.namedWindow(WINDOW_NAME)


# storage for points
selected_points = []
original_image = None
displayed_image = None


# arguments in command line
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--outwidth', type=int, required=True)
    parser.add_argument('--outheight', type=int, required=True)
    return parser.parse_args()


def mouse_callback(event, x, y, flags, param):
    global selected_points, original_image, displayed_image
    if event == cv2.EVENT_LBUTTONDOWN and len(selected_points) < 4:
        # add point to list
        selected_points.append((x, y))
        # mark point
        displayed_image = cv2.circle(displayed_image, (x, y), 5, (255, 0, 0), -1)
        # display image
        cv2.imshow(WINDOW_NAME, displayed_image)


def main():
    global selected_points, original_image, displayed_image

    # parse arguments
    args = parse_args()

    # read image
    image = cv2.imread(args.input)

    # if image is None --> tell user and exit
    if image is None:
        print(f"No image at {args.input}")
        return

    original_image = image.copy()
    displayed_image = image.copy()

    cv2.imshow(WINDOW_NAME, displayed_image)
    cv2.setMouseCallback(WINDOW_NAME, mouse_callback)

    # for reading input
    while True:
        # read keyboard input
        key = cv2.waitKey(1) & 0xFF

        # ESC key pressed --> clear selected points
        if key == 27:
            selected_points = []
            displayed_image = original_image.copy()
            cv2.imshow(WINDOW_NAME, displayed_image)

        # S pressed --> save image
        # maybe only save after transformation?
        elif key == ord('s'):
            cv2.imwrite(args.output, image)
            print(f"Image saved to {args.output}")

        # Q pressed --> quit
        elif key == ord('q'):
            break


if __name__ == "__main__":
    main()

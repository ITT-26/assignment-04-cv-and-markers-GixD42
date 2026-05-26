import cv2
import numpy as np


CONTOUR_THRESHOLD = 100


class FingerInput:
    def __init__(self, board_recognizer):
        self.board_recognizer = board_recognizer

    def process_frame(self, frame):
        # hsv -> background is white so this is better for checking for non white objects
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # range for background
        white_mask = cv2.inRange(hsv, (0, 0, 100), (180, 40, 255))

        # white removed from frame
        fg_mask = cv2.bitwise_not(white_mask)

        # find contours
        contours, _ = cv2.findContours(
            fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # for showing the detected fingertip
        debug = frame.copy()
        finger_tip = None

        # find biggest contour and place circle on top of it
        if contours:
            cnt = max(contours, key=cv2.contourArea)
            # filter out small contours that are likely noise
            if cv2.contourArea(cnt) < CONTOUR_THRESHOLD:
                return debug, finger_tip, fg_mask
            top_idx = cnt[:, :, 1].argmin()

            # will be used for the game
            finger_tip = tuple(cnt[top_idx][0])

            # display fingertip for testing
            debug = cv2.circle(debug, finger_tip, 10, (0, 0, 255), 2)

        return debug, finger_tip, fg_mask


if __name__ == "__main__":
    # Testing

    from board_recognizer import BoardRecognizer

    video_id = 0
    cap = cv2.VideoCapture(video_id)
    recognizer = BoardRecognizer()
    finger_input = FingerInput(recognizer)

    while True:
        ret, frame = cap.read()

        if not ret:
            continue

        corners, ids, rejectedImgPoints = recognizer.detect_markers(frame)
        warped = recognizer.warp_board(frame, corners, 640, 480)

        debug, finger_tip, fg_mask = finger_input.process_frame(warped)

        cv2.imshow("finger_debug", debug)
        cv2.imshow("finger_mask", fg_mask)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

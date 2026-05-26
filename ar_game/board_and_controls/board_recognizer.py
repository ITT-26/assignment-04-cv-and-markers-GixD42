import cv2
import numpy as np
from constants import *


class BoardRecognizer:

    # all the stuff for aruco detection
    def __init__(self):
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(
            cv2.aruco.DICT_6X6_250)
        self.aruco_params = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(
            self.aruco_dict, self.aruco_params)

        self.missing_frames = 0
        self.max_missing_frames = MAX_MISSING_FRAMES
        self.last_matrix = None

    # detects markers in frame and returns corners, ids and rejected points
    def detect_markers(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejectedImgPoints = self.detector.detectMarkers(gray)
        return corners, ids, rejectedImgPoints

    # draws markers on frame and returns this (for testing purposes)
    def draw_markers(self, frame, corners):
        ret_frame = frame.copy()
        cv2.aruco.drawDetectedMarkers(ret_frame, corners)
        return ret_frame

    # rewritten from ../perspective_transformation/image_extractor.py
    # orders markers to see what marker is on what position
    def order_points(self, corners):

        # centers of each marker to determine angle
        marker_centers = np.array([corner[0].mean(axis=0)
                                  for corner in corners])

        # center of all markers to determine angle
        center = marker_centers.mean(axis=0)

        # angles to order points -> left right top bottom are now in order
        angles = np.arctan2(
            marker_centers[:, 1] - center[1], marker_centers[:, 0] - center[0])
        order = np.argsort(angles)
        corners_sorted = [corners[i] for i in order]
        marker_centers_sorted = marker_centers[order]

        # top left is where x + y is smallest
        add_vals = np.sum(marker_centers_sorted, axis=1)
        top_left_index = np.argmin(add_vals)

        # top left is starting point
        corners_sorted = np.roll(corners_sorted, -top_left_index, axis=0)

        # markers shouldn't be in the frame
        board_corners = []
        for corner in corners_sorted:
            # closest point to center of marker is the corner of the board
            dists = np.linalg.norm(corner[0] - center, axis=1)
            idx = np.argmin(dists)
            board_corners.append(corner[0][idx])

        return np.array(board_corners, dtype=np.float32)

    # rewritten from ../perspective_transformation/image_extractor.py
    # uses markers as points for persepective transformation
    def warp_board(self, frame, corners, out_width, out_height):

        # board has 4 corner points
        if len(corners) != 4:
            if self.last_matrix is not None:
                self.missing_frames += 1
                if self.missing_frames > self.max_missing_frames:
                    self.last_matrix = None
                    self.missing_frames = 0
                else:
                    return cv2.warpPerspective(frame, self.last_matrix, (out_width, out_height), flags=cv2.INTER_LINEAR), True
            return frame, False

        ordered_corners = self.order_points(corners)

        destination = np.float32(
            [[0, 0], [out_width, 0], [out_width, out_height], [0, out_height]])

        mat = cv2.getPerspectiveTransform(ordered_corners, destination)
        self.last_matrix = mat
        self.missing_frames = 0
        return cv2.warpPerspective(frame, mat, (out_width, out_height), flags=cv2.INTER_LINEAR), True


if __name__ == "__main__":
    # Testing
    video_id = 0
    cap = cv2.VideoCapture(video_id)

    recognizer = BoardRecognizer()

    while True:
        ret, frame = cap.read()

        if not ret:
            continue

        corners, ids, rejectedImgPoints = recognizer.detect_markers(frame)
        view = recognizer.draw_markers(frame, corners)

        warped, is_warped = recognizer.warp_board(frame, corners, 800, 600)

        cv2.imshow('board_recognizer_test', warped)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

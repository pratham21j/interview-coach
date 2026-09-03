import cv2

from liveness.challenge import LivenessChallenge


def main():

    print("=" * 50)
    print("WEBCAM LIVENESS TEST")
    print("=" * 50)
    print("Look at the camera.")
    print("Blink and move your head LEFT / RIGHT.")
    print("Press Q to quit.")
    print("=" * 50)

    detector = LivenessChallenge()

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        print("ERROR: Could not open webcam.")
        detector.close()
        return

    try:

        while True:

            success, frame = camera.read()

            if not success:

                print("Could not read camera frame.")
                break

            # Mirror camera
            frame = cv2.flip(frame, 1)

            result = detector.process_frame(frame)

            # -------------------------------------------------
            # Information
            # -------------------------------------------------

            if result["face_detected"]:

                center = result["face_center"]

                ear = result["eye_aspect_ratio"]

                movement = result["movement_detected"]

                liveness = result["liveness"]

                # Face center
                x = int(center[0] * frame.shape[1])
                y = int(center[1] * frame.shape[0])

                cv2.circle(
                    frame,
                    (x, y),
                    8,
                    (0, 255, 0),
                    -1
                )

                cv2.putText(
                    frame,
                    f"EAR: {ear:.3f}",
                    (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    f"Blinks: {detector.blink_count}",
                    (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    f"Movement: {detector.movement_count}",
                    (20, 105),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

                if movement:

                    cv2.putText(
                        frame,
                        "MOVEMENT DETECTED",
                        (20, 145),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 0),
                        2
                    )

                if liveness:

                    cv2.putText(
                        frame,
                        "LIVE",
                        (20, 185),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0,
                        (0, 255, 0),
                        3
                    )

            else:

                cv2.putText(
                    frame,
                    "NO FACE DETECTED",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 0, 255),
                    2
                )

            cv2.imshow(
                "Interview Coach - Liveness Test",
                frame
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):

                break

    finally:

        camera.release()

        cv2.destroyAllWindows()

        detector.close()


if __name__ == "__main__":
    main()
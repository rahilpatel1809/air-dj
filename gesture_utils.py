import math

class GestureUtils:
    @staticmethod
    def distance(lm1, lm2):
        return math.sqrt((lm1.x - lm2.x) ** 2 + (lm1.y - lm2.y) ** 2)

    @staticmethod
    def is_pinch(hand_landmarks, thumb_idx, finger_idx):
        thumb_tip = hand_landmarks.landmark[thumb_idx]
        finger_tip = hand_landmarks.landmark[finger_idx]
        return GestureUtils.distance(thumb_tip, finger_tip) < 0.05

    @staticmethod
    def is_fist(hand_landmarks):
        tips = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky tips
        folded = 0
        for tip in tips:
            tip_y = hand_landmarks.landmark[tip].y
            pip_y = hand_landmarks.landmark[tip - 2].y
            if tip_y > pip_y:
                folded += 1
        return folded >= 3

    @staticmethod
    def get_palm_center(hand_landmarks):
        coords = [(lm.x, lm.y) for i, lm in enumerate(hand_landmarks.landmark) if i in [0, 1, 5, 9, 13, 17]]
        cx = sum([c[0] for c in coords]) / len(coords)
        cy = sum([c[1] for c in coords]) / len(coords)
        return cx, cy

import cv2
import mediapipe as mp
from gesture_utils import GestureUtils

class GestureController:
    def __init__(self, deck_a, deck_b):
        self.deck_a = deck_a
        self.deck_b = deck_b
        self.mp_hands = mp.solutions.hands
        self.pinch_time = {'Left': 0, 'Right': 0}
        self.pinch_hold_duration = 1
        self.fist_time = {'Left': 0, 'Right': 0}
        self.fist_hold_duration = 1 
        self.hands = self.mp_hands.Hands(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
            max_num_hands=2
        )
        self.cap = cv2.VideoCapture(0)
        self.hand_state = {'Left': {}, 'Right': {}}
        self.prev_positions = {'Left': None, 'Right': None}
        self.last_label = None  # Last gesture label shown

    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            image = cv2.flip(frame, 1)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            result = self.hands.process(rgb_image)

            gesture_label = None

            if result.multi_hand_landmarks and result.multi_handedness:
                for hand_landmarks, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
                    label = handedness.classification[0].label  # 'Left' or 'Right'
                    cx, cy = GestureUtils.get_palm_center(hand_landmarks)

                    # --- Play/Pause with Pinch ---
                    if GestureUtils.is_pinch(hand_landmarks, 4, 8):
                        if not self.hand_state[label].get('pinched', False):
                            self.hand_state[label]['pinched'] = True
                            if label == 'Left':
                                self.deck_a.toggle()
                                gesture_label = "⏯️ Toggle A"
                            else:
                                self.deck_b.toggle()
                                gesture_label = "⏯️ Toggle B"
                    else:
                        self.hand_state[label]['pinched'] = False

                    # --- Fade with Fist ---
                    if GestureUtils.is_fist(hand_landmarks):
                        if not self.hand_state[label].get('fist', False):
                            self.hand_state[label]['fist'] = True
                            if label == 'Left':
                                self.deck_a.fade_out()
                                self.deck_b.fade_in()
                                gesture_label = "⬅️ Crossfade to B"
                            else:
                                self.deck_b.fade_out()
                                self.deck_a.fade_in()
                                gesture_label = "➡️ Crossfade to A"


                    # --- Volume Control by Vertical Movement ---
                    if self.prev_positions[label] is not None:
                        prev_y = self.prev_positions[label][1]
                        delta_y = cy - prev_y
                        if abs(delta_y) > 40:
                            change = -delta_y
                            step = int(change / 40) * 5  # One step per 40px, 5% volume
                            if step != 0:
                                if label == 'Left':
                                    self.deck_a.adjust_volume(step)
                                    gesture_label = f"🎚 Volume A {'+' if step > 0 else '-'}"
                                else:
                                    self.deck_b.adjust_volume(step)
                                    gesture_label = f"🎚 Volume B {'+' if step > 0 else '-'}"
                    self.prev_positions[label] = (cx, cy)

            # --- Draw Gesture Label ---
            if gesture_label:
                self.last_label = gesture_label  # Save the most recent label
                cv2.putText(image, gesture_label, (30, 60), cv2.FONT_HERSHEY_SIMPLEX,
                            1.5, (0, 255, 0), 4)
            elif self.last_label:
                # Still show last gesture for clarity
                cv2.putText(image, self.last_label, (30, 60), cv2.FONT_HERSHEY_SIMPLEX,
                            1.5, (180, 180, 180), 2)

            cv2.imshow("Air DJ Controller", image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()
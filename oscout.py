import tensorflow as tf
import cv2
import numpy as np
from pythonosc import udp_client

np.set_printoptions(suppress=True)

class PatchedDepthwiseConv2D(tf.keras.layers.DepthwiseConv2D):
    @classmethod
    def from_config(cls, config):
        config.pop("groups", None)
        return super().from_config(config)

model = tf.keras.models.load_model(
    "keras_Model.h5",
    compile=False,
    custom_objects={"DepthwiseConv2D": PatchedDepthwiseConv2D},
)

class_names = open("labels.txt", "r", encoding="utf-8").readlines()

# ---------- CAMERA SELECTION ----------
def list_cameras(max_tested=10):
    cams = []
    for i in range(max_tested):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cams.append(i)
            cap.release()
    return cams

cams = list_cameras()
if not cams:
    raise RuntimeError("사용 가능한 카메라가 없습니다.")

print("사용 가능한 카메라:")
for i in cams:
    print(f"  [{i}] Camera {i}")

cam_index = int(input("사용할 카메라 번호를 입력하세요: "))
camera = cv2.VideoCapture(cam_index)

client = udp_client.SimpleUDPClient("127.0.0.1", 10000)
# ------------------------------------

while True:
    ret, image = camera.read()
    if not ret:
        break

    image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
    cv2.imshow("Webcam Image", image)

    # (필요하면 RGB 변환)
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)
    image = (image / 127.5) - 1

    prediction = model.predict(image, verbose=0)
    for name, score in zip(class_names, prediction[0]):
        client.send_message(f"/{name.strip()}", float(score))
    max_index = np.argmax(prediction[0])
    print(f"Predicted: {class_names[max_index].strip()} ({prediction[0][max_index]:.2f})")
    if cv2.waitKey(1) == 27:  # ESC
        break

camera.release()
cv2.destroyAllWindows()